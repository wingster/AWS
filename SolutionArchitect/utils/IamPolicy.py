#
# IamPolicy.py
#
# Class to manage IAM Policies for AWS config related functions via boto3
#
# With AWS best practices - it is recommended to grant only the necessary permissions. I would expect custom policies
# for each project. And this will be the first step in any project configurations
#
# We will use the JSON document in the configurations. It's the most flexible and it is the basic building blocks and
# should be well understood. 
# 
# AWS policy JSON syntax
#   Version
#   Statement
#   Effect
#   Action
#   Resource
#   Condition
#   Principal
#   NotAction
#   NotResource
#   NotPrincipal
# 

import sys
import json
import logging
import boto3
from botocore.exceptions import ClientError

from Config import Config, Status

# TODO: look into logger configurations & identify log locations
logger = logging.getLogger(__name__)

class IamPolicy(Config):

    def __init__(self, inputMap=None, session=None):
        super().__init__("iam", inputMap=inputMap, session=session)

    # List all the IAM policies defined with the account
    def do_list(self):
        try:
            response = self.botoClient.list_policies()
            for policy in response['Policies']:
                #print(policy)
                attribute = {
                    'Arn' : policy['Arn'],
                    'PolicyId' : policy['PolicyId'],
                    'Path' : policy['Path'],
                }
                self.addResource(policy['PolicyName'], attribute)
            return Status.SUCCESS, self.resourceMap
        except ClientError as e:
            logger.error(e)
            return Status.FAILED, e
        
    def do_create(self, client, key, keyConfig):
        try:
            logger.info(f"do_create polices: {key}, {keyConfig}")
            response = client.create_policy(
                PolicyName=key,
                PolicyDocument=Config.convertJson(keyConfig)
            )
            # log the policy ARN
            logger.info(f"Created policy {key} with ARN {response['Policy']['Arn']}")
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

            response = client.delete_policy(PolicyArn=key_arn)
            logger.info(f"Deleted policy {key} with ARN {key_arn}")
            return Status.SUCCESS, response
        except client.exceptions.DeleteConflictException as dce:
            errorMsg = f"Policy {key} is in use and cannot be deleted : {dce}"
            logger.error(errorMsg)
            return Status.FAILED, errorMsg
        except client.exceptions.NoSuchEntityException as nsee:
            errorMsg = f"Policy {key} does not exist : {nsee}"
            logger.error(errorMsg)
            return Status.FAILED, errorMsg
        except ClientError as e:
            logger.error(e)
            return Status.FAILED, e
        
def unitTest():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    policy_definition = {
        "Common-UnitTest-IamPolicy-001" : {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        "*"
                    ]
                }
            ]
        }       
    }

    # create a IamPolicy object with unitTest Key definition
    iamPolicy = IamPolicy(policy_definition)

    # create a new policy in IAM
    iamPolicy.create()

    # list the policies scoped by policy defintions in IAM
    iamPolicy.list()

    # There isn't much one can exercise a IAM Policy alone, 
    # actual test will be incorporated in IAM Role's unit test
    
    # delete the scoped/defined policies in IAM
    iamPolicy.delete()
    return 0
    # end of unitTest() function.


        
#if this .py is executed directly on the command line
def main(argv):
    # argv[0] is the script name, print remaining arguments separated by space without the bracket
    print("Running :", " ".join(argv[0:]))
    
    # if no additonal arguments are passed, print usage help
    if len(argv) != 2 or argv[1] not in ["create", "delete", "list", "unit"]:
        #    print(f"Usage: python3 {argv[0]} <create|delete|list|unit>")
        #print(f"account_id = {boto3.client('sts').get_caller_identity().get('Account')}")
        print(f"Usage: python3 {argv[0]} <create|delete|list|unit> ")
        return
    else:
        # if additional arguments are passed, proceed with the action
        policy = IamPolicy()
        action = argv[1]
        if action == "create":
            policy.create()
        elif action == "delete":
            policy.delete()
        elif action == "list":
            policy.list()
        elif action == "unit":
            unitTest()
            
if __name__ == "__main__":
    main(sys.argv)
