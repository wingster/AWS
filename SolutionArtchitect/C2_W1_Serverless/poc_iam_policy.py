# Create IAM policies required for serverless solution in week 1 of the course in AWS Cloud
# Please refer to the Readme.md file for the architectural diagram and additional details.
# URL for the POC: https://aws-tc-largeobjects.s3.us-west-2.amazonaws.com/DEV-AWS-MO-Architecting/exercise-1-serverless.html
#
# In this python script, it will use boto3 to achieve the creation and cleanup of the required resources 
# Step 1: Creating custom IAM polices
#       * Lambda-Write-DynamoDB
#       * Lambda-SNS-Publish
#       * Lambda-DynamoDBStreams-Read
#       * Lambda-Read-SQS

import boto3
import sys
import json


policy_definitions = {
    "POC1-Lambda-Write-DynamoDB": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:DescribeTable"
                ],
                "Resource": "*"
            }
        ]
    },

    "POC1-Lambda-SNS-Publish": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "sns:Publish",
                    "sns:GetTopicAttributes",
                    "sns:ListTopics"
                ],
                "Resource": "*"
            }
        ]
    },

    "POC1-Lambda-DynamoDBStreams-Read": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetShardIterator",
                    "dynamodb:DescribeStream",
                    "dynamodb:ListStreams",
                    "dynamodb:GetRecords"
                ],
                "Resource": "*"
            }
        ]
    },

    "POC1-Lambda-Read-SQS": {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "sqs:DeleteMessage",
                    "sqs:ReceiveMessage",
                    "sqs:GetQueueAttributes",
                    "sqs:ChangeMessageVisibility"
                ],
                "Resource": "*"
            }
        ]
    }
}

def create_policies():
    # create a client for IAM
    iam = boto3.client('iam')

    # iterate through the policy definitions and create the policies
    for policy_name, policy_definition in policy_definitions.items():
        # create the policy
        response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_definition)
        )

        # print the policy ARN
        print(f"Created policy {policy_name} with ARN {response['Policy']['Arn']}")

def delete_policies():
    # create a client for IAM
    iam = boto3.client('iam')
    account_id = boto3.client('sts').get_caller_identity().get('Account')

    # iterate through the policy definitions and delete the policies
    for policy_name, policy_definition in policy_definitions.items():
        # delete the policy
        # catch exception while deleting policy
        try:
            response = iam.delete_policy(
                PolicyArn=f"arn:aws:iam::{account_id}:policy/{policy_name}"
            )
            print(f"Deleted policy {policy_name} with response: {response}")
        except iam.exceptions.DeleteConflictException:
            print(f"Policy {policy_name} is in use and cannot be deleted")
        except iam.exceptions.NoSuchEntityException:
            print(f"Policy {policy_name} does not exist")
            

def list_policies():
    # create a client for IAM
    iam = boto3.client('iam')

    # list the policies
    response = iam.list_policies()

    # print the policy ARNs
    for policy in response['Policies']:
        print(f"Policy {policy['PolicyName']} with ARN {policy['Arn']}")
    print(f"Total number of policies: {len(response['Policies'])}")
    print(f"Total number of policies with name starting with POC1: {len([policy for policy in response['Policies'] if policy['PolicyName'].startswith('POC1')])}")
    #print(f"Total number of policies with name starting with POC2: {len([policy for policy in response['Policies'] if policy['PolicyName'].startswith('POC2')])}")
    #print(f"Total number of policies with name starting with POC3: {len([policy for policy in response['Policies'] if policy['PolicyName'].startswith('POC3')])}")


#if this .py is executed directly on the command line
def main(argv):
    # argv[0] is the script name, print remaining arguments separated by space without the bracket
    print("Running :", " ".join(argv[0:]))
    
    # if no additonal arguments are passed, print usage help
    if len(argv) != 2 or argv[1] not in ["create", "delete", "list"]:
        print("Usage: python3 {argv[0]} <create|delete|list>")
        print(f"account_id = {boto3.client('sts').get_caller_identity().get('Account')}")
        return
    else:
        # if additional arguments are passed, proceed with the action
        action = argv[1]
        if action == "create":
            create_policies()
            #print("Policies created successfully")
        elif action == "delete":
            delete_policies()
            #print("Policies deleted successfully")
        elif action == "list":
            list_policies()


if __name__ == "__main__":
    main(sys.argv)
