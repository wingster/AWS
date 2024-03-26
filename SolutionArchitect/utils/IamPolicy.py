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

from Config import Config

# TODO: look into logger configurations & identify log locations
logger = logging.getLogger(__name__)

class IamPolicy(Config):

    def __init__(self, inputMap=None, session=None):
        super().__init__("iam", inputMap=inputMap, session=session)


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
            return response
        except ClientError as e:
            logger.error(e)
            return None
        
    def do_create(self, botoClient, configMap):
        try:
            print("do_create polices")
            for policy_name, policy_definition in configMap.items():
                # create the policy
                response = botoClient.create_policy(
                    PolicyName=policy_name,
                    PolicyDocument=json.dumps(policy_definition)
                )
                # print the policy ARN
                print(f"Created policy {policy_name} with ARN {response['Policy']['Arn']}")
            return
        except ClientError as e:
            logger.error(e)
            return None
        
    def do_delete(self):
        try:
            # iterate though the configuration diectionary and only remove the ones defined by this instance
            for policy_name in self.configMap.keys():
                policy_arn = self.configMap[policy_name]

                if policy_arn == None:
                    print(f"Policy ARN for {policy_name} not found")
                    continue
                else:                
                    # delete the policy
                    response = self.botoClient.delete_policy(PolicyArn=policy_arn)
                    print(f"Deleted policy {policy_name} with ARN {policy_arn}")
            return
        except iam.exceptions.DeleteConflictException:
            print(f"Policy {policy_name} is in use and cannot be deleted")
        except iam.exceptions.NoSuchEntityException:
            print(f"Policy {policy_name} does not exist")
        except ClientError as e:
            logger.error(e)
            return None
        
#if this .py is executed directly on the command line
def main(argv):
    # argv[0] is the script name, print remaining arguments separated by space without the bracket
    print("Running :", " ".join(argv[0:]))
    
    # if no additonal arguments are passed, print usage help
    if len(argv) != 2 or argv[1] not in ["create", "delete", "list"]:
        #    print(f"Usage: python3 {argv[0]} <create|delete|list>")
        #print(f"account_id = {boto3.client('sts').get_caller_identity().get('Account')}")
        print("Usage: python3 IamRole.py <create|delete|list> ")
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


if __name__ == "__main__":
    main(sys.argv)
