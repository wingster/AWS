#
# Kms.py
#
# Class to manage Key Management Service via boto3
# https://docs.aws.amazon.com/kms/latest/developerguide/overview.html
#
# Define the encryption keys and the options assoicated with each key 
# 

import sys
import json
import logging
import boto3
from botocore.exceptions import ClientError

from Config import Config, Status, Action

# TODO: look into logger configurations & identify log locations
logger = logging.getLogger(__name__)

class Kms(Config):
    def __init__(self, inputMap=None, session=None):
        super().__init__("kms", inputMap=inputMap, session=session)

    # List all the keys defined in KMS
    def do_list(self):
        try:
            response = self.botoClient.list_keys()
            for key in response['Keys']:
                #print(key['KeyId'])
                aliasResponse = self.botoClient.list_aliases(KeyId=key['KeyId'])
                #print(aliasResponse)
                aliases = aliasResponse['Aliases']
                if len(aliases) == 0:
                    #print("No aliases defined for this key")
                    attribute = {'Arn': key['KeyArn'],
                                 'KeyId': key['KeyId'],}
                    self.addResource(key['KeyId'], attribute)
                    continue
                for alias in aliases:
                    #print(alias)
                    attribute = {'Arn': key['KeyArn'],
                                 'KeyId': alias['TargetKeyId'],
                                 'AliasName': alias['AliasName'],
                                 'AliasArn': alias['AliasArn'],
                                }
                    aliasName = alias['AliasName']
                    # remove 'alias/' prefix from aliasName
                    if aliasName.startswith('alias/'):
                        aliasName = aliasName[len('alias/'):]
                    self.addResource(aliasName, attribute)
            return self.resourceMap
        except ClientError as e:
            logger.error(e)
            return None
        

    # Create a new key in KMS    
    def do_create(self, client, key, keyConfig):
        try:
            logger.info(f"do_create kms key: {key}, {keyConfig}")
            
            response = client.create_key(
                Alias=key,
                Description=keyConfig['Description'],
                KeyUsage=keyConfig['KeyUsage'],
                Origin=keyConfig['Origin'],
                Tags=keyConfig['Tags']
            )
            # log the policy ARN
            logger.info(f"Created Key {key} with ARN {response['KeyMetadata']['Arn']}")
            return Status.SUCCESS, response 
        except ClientError as e:
            logger.error(e)
            return Status.FAILED, e
        
    def do_delete(self, client, key, keyConfig):
        try:
            key_arn = self.getArn(key)
            if key_arn == None:
                errorMsg = f"Unable to resolve ARN for {key}. do_delete failed"
                logger.error(errorMsg)
                return Config.Status.FAILED, errorMsg

            response = client.schedule_key_deletion(
                KeyId=key_arn,
                PendingWindowInDays=7
            )
            logger.info(f"Deleted key {key} with ARN {key_arn}")
            return Status.SUCCESS, response
        except ClientError as e:
            logger.error(e)
            return Status.FAILED, e

    def encrypt(self, keyName, plainText):
        try:
            # get the key ARN
            key_arn = self.getArn(keyName)

            # encrypt the plaintext with the key
            ciphertext = self.botoClient.encrypt(
                KeyId=key_arn,
                Plaintext=plainText,
                #EncryptionAlgorithm="RSAES_OAEP_SHA_1"
            )["CiphertextBlob"]
            # return the ciphertext
            return ciphertext
        except ClientError as e:
            logger.error(e)
            return None

    def decrypt(self, keyName, cipherText):
        try:
            # get the key ARN
            key_arn = self.getArn(keyName)

            # decrypt the ciphertext with the key
            plaintext = self.botoClient.decrypt(
                KeyId=key_arn,
                CiphertextBlob=cipherText,
                #EncryptionAlgorithm="RSAES_OAEP_SHA_1"
            )["Plaintext"]
            # return the plaintext
            return plaintext
        except ClientError as e:
            logger.error(e)
            return None

#            for policy_name in self.dict.keys():
#                policy_arn = self.policy_map[policy_name]

        #         if policy_arn == None:
        #             print(f"Policy ARN for {policy_name} not found")
        #             continue
        #         else:                
        #             # delete the policy
        #             response = self.boto_client.delete_policy(PolicyArn=policy_arn)
        #             print(f"Deleted policy {policy_name} with ARN {policy_arn}")
        #     return
        # except iam.exceptions.DeleteConflictException:
        #     print(f"Policy {policy_name} is in use and cannot be deleted")
        # except iam.exceptions.NoSuchEntityException:
        #     print(f"Policy {policy_name} does not exist")
        # except ClientError as e:
        #     logger.error(e)
        #     return None


def unitTest():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    kms_definition = {
        "Common-UnitTest-Kms-001": {
            "Description": "UnitTest KMS Test Key 001",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "Origin": "AWS_KMS",  # AWS_KMS, EXTERNAL, or AWS_CLOUDHSM
            "KeySpec": "SYMMETRIC_DEFAULT",  # RSA_2048, RSA_3072, RSA_4096, ECC_NIST_P256, ECC_NIST_P384, ECC_NIST_P521, or SYMMETRIC_DEFAULT
            "Tags" : [
                {   "TagKey"  : "Context",
                    "TagValue": "Common-UnitTest-Kms"},
                {   "TagKey" : "Environment", 
                    "TagValue" : "UnitTest"}
            ],
        },
    }

    # create a Kms object with unitTest Key definition
    kms = Kms(kms_definition)

    # create a new key in KMS
    kms.create()

    # list all the keys in KMS
    kms.list()

    try:
        # encrypt and decrypt a message
        message = "Hello, World!"
        key_name = "Common-UnitTest-Kms-001"
        ciphertext = kms.encrypt(key_name, message)
        print(f"Encrypted message: {ciphertext}")
        plaintext = kms.decrypt(key_name, ciphertext)
        print(f"Decrypted message: {plaintext}")
    except Exception as e:
        print(f"Error encrypting or decrypting message {e}")
    except ClientError as e:
        print(f"Error encrypting or decrypting message {e}")

    # delete the keys in KMS
    # KMS implemented a pending removal mechanism. 
    # We temporary disable the remove here
    # The solution to this is to extend the framework to 
    # to support deplay removal -> and have extension to renable the key
    # if it detected that it's pending removal
    #kms.delete()
    return 0
    # end of unitTest() function.

        
#if this .py is executed directly on the command line
def main(argv):
    # argv[0] is the script name, print remaining arguments separated by space without the bracket
    print("Running :", " ".join(argv[0:]))
    
    # if no additonal arguments are passed, print usage help
    if len(argv) != 2 or argv[1] not in ["create", "delete", "list", "unit"]:
        #    print(f"Usage: python3 {argv[0]} <create|delete|list>")
        #print(f"account_id = {boto3.client('sts').get_caller_identity().get('Account')}")
        print("Usage: python3 IamRole.py <create|delete|list|unit> ")
        return
    else:
        # if additional arguments are passed, proceed with the action
        kms = Kms()
        action = argv[1]
        if action == "create":
            kms.create()
        elif action == "delete":
            kms.delete()
        elif action == "list":
            kms.list()
        elif action == "unit":
            unitTest()


if __name__ == "__main__":
    main(sys.argv)
