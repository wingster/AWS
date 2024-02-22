# Task 3: Creating an SQS queue
# In this task, you create an SQS queue. In the architecture for this exercise, 
# the Amazon SQS receives data records from API Gateway, stores them, and then sends 
# them to a database.
#
# In this python script, it will use boto3 to achieve the creation and cleanup of the required resources
#
import sys
import boto3
import json
from poc_iam_role import get_arn_by_role_name

sqs_definitions = {
    "POC1-Queue": {
        "SendRoles" : ["POC1-APIGateway-SQS"],
        "ReceiveRoles" : ["POC1-Lambda-SQS-DynamoDB"],
    },
}


# Create an SQS queue
def create_sqs():
    # create an SQS client
    sqs = boto3.client('sqs')

    for sqs_queue, sqs_param in sqs_definitions.items():
        # create a queue
        response = sqs.create_queue(
            QueueName=sqs_queue,
            Attributes={
                'DelaySeconds': '0',
                'MessageRetentionPeriod': '86400'
            }
        )

        queue_url = response['QueueUrl']
        send_roles = [get_arn_by_role_name(role) for role in sqs_param['SendRoles']]
        recv_roles = [get_arn_by_role_name(role) for role in sqs_param['ReceiveRoles']]
        
        statements = []
        for role_arn in send_roles:
            action = "SQS:SendMessage"
            statement = {
                'Effect': 'Allow',
                'Principal': {'AWS': role_arn},
                'Action': action,
                'Resource': queue_url
            }
            statements.append(statement)
        
        for role_arn in recv_roles:
            action = "SQS:ReceiveMessage"
            statement = {
                'Effect': 'Allow',
                'Principal': {'AWS': role_arn},
                'Action': action,
                'Resource': queue_url
            }
            statements.append(statement)
        
        # Define the policy that grants permission to the IAM role
        policy = {
            'Version': '2012-10-17',
            'Statement': statements
        }

        # Convert the policy to JSON string
        policy_json = json.dumps(policy)

        # Add the IAM role policy to the SQS queue
        sqs.set_queue_attributes(
            QueueUrl=queue_url,
            Attributes={
                'Policy': policy_json
        }
)

def delete_sqs():
    # create an SQS client
    sqs = boto3.client('sqs')

    # iterate through the queue definitions and delete the queues
    for sqs_queue in sqs_definitions.keys():
        # get the queue URL for the queue named "POC1-Queue"
        queue_url = sqs.get_queue_url(QueueName=sqs_queue)
        #print(queue_url)
        # delete the queue
        response = sqs.delete_queue(
            QueueUrl=queue_url['QueueUrl']
        )

        # print the response
        print(response)


# list the SQS queues
def list_sqs():
    # create an SQS client
    sqs = boto3.client('sqs')
    num_queues = 0
    # list the queues
    response = sqs.list_queues()

    # print the queue URLs
    for queue_url in response['QueueUrls']:
        # map the queue_url to the queue name
        queue_name = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['QueueArn'])['Attributes']['QueueArn'].split(':')[-1]
        if queue_name in sqs_definitions.keys():
            print(f"{queue_name}: {queue_url}")
            num_queues+=1
        else:
            print(queue_url)
    
    print(f"Total number of queues: {len(response['QueueUrls'])}")
    print(f"Total number of queues defined by this module : {len([queue for queue in response['QueueUrls'] if queue.split('/')[-1].startswith('POC1')])}")
    

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
            create_sqs()
        elif action == "delete":
            delete_sqs()
        elif action == "list":
            list_sqs()


if __name__ == "__main__":
    main(sys.argv)

