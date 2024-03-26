#
# IamRole.py
#
# Class to manage IAM Roles for AWS config related functions via boto3
#
# For existing use case, Each IAM Role configuration is associated with an AWS service, and the policies related to the AWS service
# There are User-defined polices and AWS-defined polices. (The policy ARN between user-defined policy and AWS-defined policy are different)
#  

import sys
import json

import logging
import boto3
from botocore.exceptions import ClientError
from Config import Config

# TODO: look into logger configurations & identify log locations
logger = logging.getLogger(__name__)

class IamRole(Config):

    def __init__(self, dict=None):
        super().__init__("iam", dict)

    def do_list(self, botoClient, configMap):
        try:
            response = botoClient.list_roles()
            for role in response['Roles']:
                #print(role)
                attribute = {
                    "Arn" : role['Arn'],
                    "RoleId" : role['RoleId'],
                    "Path" : role['Path'],
                }
                # check to see if role contains Description as key
                if "Description" in role:
                    attribute["Description"] = role["Description"]
                else:
                    attribute["Description"] = ""
                self.addResource(role['RoleName'], attribute)
            return response
        except ClientError as e:
            logger.error(e)
            return None
        
    def do_create(self, botoClient, configMap):
        try:
            accountId = self.accountId()
            for role_name, role_definition in configMap.items():
                print(f"Creating IAM Role {role_name}")

            response = botoClient.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                role_definition["PrincipalType"]: role_definition[role_definition["PrincipalType"]]
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                })
            )
            return response
        except ClientError as e:
            logger.error(e)
            return None
        

def test1(configType, dict=None):
    print(f"calling {configType}")
    ## instantiance an instance of configType
    configObject = configType(dict)
    configObject.list()



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
        role = IamRole()
        action = argv[1]
        if action == "create":
            role.create()
        elif action == "delete":
            role.delete()
        elif action == "list":
            role.list()
            #test1(IamRole)


if __name__ == "__main__":
    main(sys.argv)
