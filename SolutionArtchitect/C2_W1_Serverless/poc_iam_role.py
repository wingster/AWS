# Create IAM roles required for serverless solution in week 1 of the course in AWS Cloud
# Please refer to the Readme.md file for the architectural diagram and additional details.
# URL for the POC: https://aws-tc-largeobjects.s3.us-west-2.amazonaws.com/DEV-AWS-MO-Architecting/exercise-1-serverless.html
#
# In this python script, it will use boto3 to achieve the creation and cleanup of the required resources 
# Step 2: Creating IAM roles and attach the policies created in poc_iam_policy.py 
#       * Lambda-SQS-DynamoDB
#       * Lambda-DynamoDBStreams-SNS
#       * APIGateway-SQS

import boto3
import json
import sys

role_definitions = {
    "POC1-Lambda-SQS-DynamoDB": {
        "Service" : "lambda.amazonaws.com",
        "UserPolices" : ["POC1-Lambda-Write-DynamoDB", "POC1-Lambda-Read-SQS"],
        "AWSPolices" : [],
    },
    "POC1-Lambda-DynamoDBStreams-SNS": {
        "Service" : "lambda.amazonaws.com",
        "UserPolices" : ["POC1-Lambda-SNS-Publish", "POC1-Lambda-DynamoDBStreams-Read"],
        "AWSPolices" : [],
    },
    "POC1-APIGateway-SQS": {
        "Service" : "apigateway.amazonaws.com",
        "UserPolices" : [],
        "AWSPolices" : ["service-role/AmazonAPIGatewayPushToCloudWatchLogs"],
    },
}

# Create IAM roles and attach the defined policies in role_definitions 
def create_roles():
    iam = boto3.client("iam")
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    for role_name, role_definition in role_definitions.items():
        print(f"Creating role {role_name}...")
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": role_definition["Service"]
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            })
        )
        for policy_name in role_definition["UserPolices"]:
            print(f"Attaching policy {policy_name} to role {role_name}...")
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=f"arn:aws:iam::{account_id}:policy/{policy_name}"
            )
        for policy_name in role_definition["AWSPolices"]:
            print(f"Attaching arn {policy_name} to role {role_name}...")
            iam.attach_role_policy(
                RoleName=role_name,
                PolicyArn=f"arn:aws:iam::aws:policy/{policy_name}"
            )

        
# Delete the defined IAM roles
def delete_roles():
    iam = boto3.client("iam")
    for role_name, role_definition in role_definitions.items():
        #find the policies attached to the role and detach them
        try: #Check if role_name exists in IAM role
            iam.get_role(RoleName=role_name)
            role_policies = iam.list_attached_role_policies(RoleName=role_name)["AttachedPolicies"]
            for policy in role_policies:
                print(f"Detaching policy {policy['PolicyName']} from role {role_name}...")
                iam.detach_role_policy(RoleName=role_name, PolicyArn=policy["PolicyArn"])   
            print(f"Deleting role {role_name}...")
            iam.delete_role(RoleName=role_name)
        except iam.exceptions.NoSuchEntityException:
            #role_name does not exist, print error message and continue to next role_name
            print(f"Role {role_name} does not exist")
            continue


# List the defined IAM roles
def list_roles():
    iam = boto3.client("iam")
    for role_name, role_definition in role_definitions.items():
        #Check if role_name exists in IAM role
        try:
            role_response = iam.get_role(RoleName=role_name)
            print(f"Role {role_name} ({role_response['Role']['Arn']}) has the following policies:")
            role_policies = iam.list_attached_role_policies(RoleName=role_name)["AttachedPolicies"]
            for policy in role_policies:
                print(f"  - {policy['PolicyName']}")
        except iam.exceptions.NoSuchEntityException:
            #role_name does not exist, print error message and continue to next role_name
            print(f"Role {role_name} does not exist")
            continue

def get_arn_by_role_name(role_name):
    iam = boto3.client("iam")
    return iam.get_role(RoleName=role_name)["Role"]["Arn"]


#if this .py is executed directly on the command line
def main(argv):
    # argv[0] is the script name, print remaining arguments separated by space without the bracket
    print("Running :", " ".join(argv[0:]))
    
    # if no additonal arguments are passed, print usage help
    if len(argv) != 2 or argv[1] not in ["create", "delete", "list"]:
        print(f"Usage: python3 {argv[0]} <create|delete|list>")
        print(f"account_id = {boto3.client('sts').get_caller_identity().get('Account')}")
        return
    else:
        # if additional arguments are passed, proceed with the action
        action = argv[1]
        if action == "create":
            create_roles()
        elif action == "delete":
            delete_roles()
        elif action == "list":
            list_roles()


if __name__ == "__main__":
    main(sys.argv)

