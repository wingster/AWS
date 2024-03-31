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
from IamPolicy import IamPolicy

# TODO: look into logger configurations & identify log locations
logger = logging.getLogger(__name__)

class IamRole(Config):

    def __init__(self, dict=None):
        super().__init__("iam", dict)

    def do_list(self):
        try:
            response = self.botoClient.list_roles()
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
            return self.resourceMap
        except ClientError as e:
            logger.error(e)
            return None
        
    def do_create(self, client, key, keyConfig):
        try:
            accountId = self.accountId()
            logger.info(f"do_create role: {key}, {keyConfig}")

            response = client.create_role(
                RoleName=key,
                AssumeRolePolicyDocument=json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                keyConfig["PrincipalType"]: keyConfig[keyConfig["PrincipalType"]]
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                })
            )
            for policy_name in keyConfig["UserPolicies"]:
                print(f"Attaching policy {policy_name} to role {key}...")
                client.attach_role_policy(
                    RoleName=key,
                    # It would have been nice to get Arn from IamPolicy, but there isn't a link to IamPolicy at this time
                    PolicyArn=f"arn:aws:iam::{accountId}:policy/{policy_name}" #iamPolicy.getArn(policy_name)
            )
                
            # If there is a way to get Arn directly from IamPolicy, then we
            # can handle both UserPolicies & AWSPolices in one-go and don't
            # need to differentiate them
            for policy_name in keyConfig["AWSPolicies"]:
                print(f"Attaching arn {policy_name} to role {key}...")
                client.attach_role_policy(
                    RoleName=key,
                    PolicyArn=f"arn:aws:iam::aws:policy/{policy_name}"
                )    
            return response
        except ClientError as e:
            logger.error(e)
            return None
        
    # do_delete
    def do_delete(self, client, key, keyConfig):
        pass

def unitTest():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    # Test IAM Policy along with IAM Role
    policy_definition = {
        "Common-UnitTest-IamPolicy-002" : {
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

    role_definition = {
        "Common-UnitTest-IamRole-001" : {
            "PrincipalType" : "AWS",
            "AWS" : Config.accountId(),
            "UserPolicies" : ["Common-UnitTest-IamPolicy-002"],
            "AWSPolicies" : [],
        },
    }


    # create a IamPolicy object with unitTest Key definition
    iamPolicy = IamPolicy(policy_definition)
    iamRole = IamRole(role_definition)
    # create a new policy in IAM
    iamPolicy.create()
    iamRole.create()

    # Assume the newly created role


    iamRole.delete()
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
        role = IamRole()
        action = argv[1]
        if action == "create":
            role.create()
        elif action == "delete":
            role.delete()
        elif action == "list":
            role.list()
        elif action == "unit":
            unitTest()


if __name__ == "__main__":
    main(sys.argv)
