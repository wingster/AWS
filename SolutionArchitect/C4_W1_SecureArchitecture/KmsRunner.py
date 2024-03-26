#
# KmsRunner.py
# 
# Entry point to setup Week1 Exam preparations to exercise AWS Key Management Services
#
# 1. Create minimal policy to allow operation on the created KMS key
# 2. Create IAM role with the above policy to operate on the key
# 3. Create KMS key, retreive the key
# 4. Use it to encrypt/decrypt message similar to the KeyEncrypt.py example
# 
# Setup using utils.config classes 
#

import boto3

from Project import Project
from IamPolicy import IamPolicy
from IamRole import IamRole
from Kms import Kms
from botocore.exceptions import ClientError


import sys
import logging

# The kms defintions can be stored in file, or in this, inline in runner
policy_definitions = {
    "C4W1-Kms-EncryptPolicy": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "kms:Encrypt",
                    "kms:Descrypt",
                    "kms:DescribeKey"
                ],
                "Resource": "*"
            }
        ]
    },
}

role_definition = {
    "C4W1-Kms-EncryptRole": {
        "Service" : "kms.amazonaws.com",
        "UserPolicies": ["C4W1-Kms-EncryptPolicy"],
        "AWSPolicies" : []
    }
}

kms_definition = {
    "C4W1-Kms-Key": {
        "Description": "KMS Key for C4W1",
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "SYMMETRIC_DEFAULT",
        "KeyPolicy": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "XXXXXXXXXXXXX",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
                        

def create(project):
    project.addConfig(IamPolicy, policy_definitions)
    project.addCofnig(IamRole, role_definition)
    
    project.list(IamPolicy)

def list(project):
    project.list()


def run(project):
    """
        Encrypts text by using the specified key.

        :param key_id: The ARN or ID of the key to use for encryption.
        :return: The encrypted version of the text.
        """
    key_id = input("Enter the key id: ")
    if key_id:
        text = input("Enter some text to encrypt: ")
        try:
            kms = project.getConfig(Kms)
            cipher_text = kms.encrypt(
                keyName=key_id, plainText=text.encode()
            )["CiphertextBlob"]

            print(f"Your ciphertext is: {cipher_text}")

            decrypted_text = kms.decrypt(
                keyName=key_id,
                cipherText=cipher_text)
            
            print(f"Your decrypted text is: {decrypted_text}")
            return cipher_text
        except ClientError as err:
            logger.error(
                "Couldn't encrypt text. Here's why: %s",
                err.response["Error"]["Message"],
            )

        






#if this .py is executed directly on the command line
def main(argv):
    # argv[0] is the script name, print remaining arguments separated by space without the bracket
    print("Running :", " ".join(argv[0:]))
    
    project = Project(name="C4_W1_SecureArchitecture", roleName="AWSServiceRoleForSupport")
    # if no additonal arguments are passed, print usage help
    if len(argv) != 2 or argv[1] not in ["create", "delete", "list", "run"]:
        print(f"Usage: python3 {argv[0]} <create|delete|list>")
        print(f"account_id = {boto3.client('sts').get_caller_identity().get('Account')}")
        return
    else:

        # if additional arguments are passed, proceed with the action
        action = argv[1]
        if action == "create":
            create(project)
            #print("Policies created successfully")
        elif action == "delete":
            pass
            #delete_policies()
            #print("Policies deleted successfully")
        elif action == "list":
            list(project)
        elif action == "run":
            project.addConfig(Kms)
            list(project)
            run(project)


if __name__ == "__main__":
    main(sys.argv)

