# In this task, you create a Lambda function that reads messages from the SQS queue and writes an order record to the DynamoDB table.
#
# Step 4.1: Creating a Lambda function for the Lambda-SQS-DynamoDB role
# In the AWS Management Console search box, enter Lambda and from the list, choose Lambda.

# Choose Create function and configure the following settings:
# Function option: Author from scratch
# Function name: POC-Lambda-1
# Runtime: Python 3.9
# Change default execution role: Use an existing role
# Existing role: Lambda-SQS-DynamoDB
# Choose Create function.

# Step 4.2: Setting up Amazon SQS as a trigger to invoke the function
# If needed, expand the Function overview section.
# Choose Add trigger.
# For Trigger configuration, enter SQS and choose the service in the list.
# For SQS queue, choose POC-Queue.
# Add the trigger by choosing Add.

# Step 4.3: Adding and deploying the function code
# On the POC-Lambda-1 page, in the Code tab, replace the default Lambda function code with the following code:
# import boto3, uuid

# client = boto3.resource('dynamodb')
# table = client.Table("orders")

# def lambda_handler(event, context):
#     for record in event['Records']:
#         print("test")
#         payload = record["body"]
#         print(str(payload))
#         table.put_item(Item= {'orderID': str(uuid.uuid4()),'order':  payload})
# Copy to clipboard
# Choose Deploy.

# The Lambda code passes arguments to a function call. As a result, when a trigger invokes a function, Lambda runs the code that you specify.

import boto3
import sys
from poc_iam_role import get_arn_by_role_name
from poc_sqs import get_sqs_queue_arn
from utils.zip import create_zip_content

lambda_definitions = {
    "POC-Lambda-1": {  
        "FunctionName": "POC-Lambda-1",
        "Runtime": "python3.9",
        "Role": "POC1-Lambda-SQS-DynamoDB",
        "Handler": "save_order_record.lambda_handler",
        "Trigger": {
            "SQS_Trigger" : {
                "Principal": "sqs.amazonaws.com",
                "SourceArn": get_sqs_queue_arn("POC1-Queue"),
            },
        },
        "Destination": [],
        "zip_content":  {
            "save_order_record.py" : 
"""        
import boto3, uuid
client = boto3.resource('dynamodb')
table = client.Table("POC1_orders")

def lambda_handler(event, context):
    for record in event['Records']:
        print("test")
        payload = record["body"]
        print(str(payload))
        table.put_item(Item= {'orderID': str(uuid.uuid4()), 'order':  payload})
"""}
    }
}

# When defining the Code parameter for the create_function method in Lambda, there are a few different keys you can specify depending on where your function code is stored: [1]
# ZipFile - Used to define code stored directly in a zip file. The value should be the zip file contents.
# S3Bucket - The S3 bucket name where the code zip file is stored.
# S3Key - The S3 object (zip file) key name.
# S3ObjectVersion - The S3 object version of the zip file.
# ImageUri - The URI of a Docker image containing your function code. This should be a string like the ECR repository path.
# So in summary, the Code parameter accepts zip file contents directly via ZipFile, or references to code stored in S3 or a Docker image. The appropriate key depends on where your Lambda function code is located. [2]

def create_lambda():
    lambda_client = boto3.client('lambda')
    for lambda_def in lambda_definitions:

        # get arn for role name
        role_arn = get_arn_by_role_name(lambda_definitions[lambda_def]["Role"])
        zip_content = create_zip_content(lambda_definitions[lambda_def]["zip_content"])

        lambda_client.create_function(
            FunctionName=lambda_def,
            Runtime=lambda_definitions[lambda_def]["Runtime"],
            Role=role_arn,
            Handler=lambda_definitions[lambda_def]["Handler"],
            Code={ "ZipFile" : zip_content }
        )
        print(f"Lambda function {lambda_def} created")

        # Now add triggers to the lambda function
        for trigger, trigger_param in lambda_definitions[lambda_def]["Trigger"].items():
            lambda_client.add_permission(
                FunctionName=lambda_def,
                StatementId=f"{lambda_def}-{trigger}",
                Action="lambda:InvokeFunction",
                Principal=trigger_param["Principal"],
                SourceArn=trigger_param["SourceArn"],
            )
            lambda_client.create_event_source_mapping(
                EventSourceArn=trigger_param["SourceArn"],
                FunctionName=lambda_def,
                Enabled=True
            )
            print(f"Event source mapping created for {trigger} to Lambda function {lambda_def}")


# Rapid creation and deletion may throw this annoying error
# botocore.errorfactory.ResourceInUseException: An error occurred (ResourceInUseException) when calling the DeleteEventSourceMapping operation: Cannot delete the event source mapping because it is in use.

def delete_lambda():
    lambda_client = boto3.client('lambda')
    for lambda_def in lambda_definitions:
        # remove event source mappings associated with this function
        mappings = lambda_client.list_event_source_mappings(FunctionName=lambda_def)['EventSourceMappings']
        for m in mappings:
            lambda_client.delete_event_source_mapping(UUID=m['UUID'])

        lambda_client.delete_function(FunctionName=lambda_def)
        print(f"Lambda function {lambda_def} deleted")


def list_lambda():
    lambda_client = boto3.client('lambda')
    response = lambda_client.list_functions()
    for function in response["Functions"]:
        print(f"Function {function['FunctionName']} with ARN {function['FunctionArn']}")
        # print the event source mappings associated with this function
        mappings = lambda_client.list_event_source_mappings(FunctionName=function["FunctionName"])['EventSourceMappings']
        for m in mappings:
            print(f"  Event source mapping {m['UUID']} with {m['EventSourceArn']}")




  
        


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
            create_lambda()
        elif action == "delete":
            delete_lambda()
        elif action == "list":
            list_lambda()


if __name__ == "__main__":
    main(sys.argv)

