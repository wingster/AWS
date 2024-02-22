Task 1. Setup: Creating IAM policies and roles

When you first create an account on AWS, you become a root user, or an account owner. We don’t recommend that you use the account root user for daily operations and tasks. Instead, you should use an IAM user or IAM roles to access specific services and features. IAM policies, users, and roles are offered at no additional charge.

In this task, you create custom IAM policies and roles to grant limited permissions to specific AWS services.

Step 1.1: Creating custom IAM policies

Sign in to the AWS Management Console.

In the search box, enter IAM.

From the results list, choose IAM.

In the navigation pane, choose Policies.

Choose Create policy.

The Create policy page appears. You can create and edit a policy in the visual editor or use JSON. In this exercise, we provide JSON scripts to create policies. In total, you must create four policies.

In the JSON tab, paste the following code:

{
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
}
Copy to clipboard
This JSON script grants permissions to put items into the DynamoDB table. The asterisk (*) indicates that the specified actions can apply to all available resources.

Choose Next: Tags and then choose Next: Review.

For the policy name, enter Lambda-Write-DynamoDB.

Choose Create policy.

After you create the Lambda-Write-DynamoDB policy, repeat the previous steps to create the following policies:

A policy for Amazon SNS to get, list, and publish topics that are received by Lambda:

Name: Lambda-SNS-Publish
JSON:
{
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
 }
Copy to clipboard
A policy for Lambda to get records from DynamoDB Streams:

Name: Lambda-DynamoDBStreams-Read
JSON:
{
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
}
Copy to clipboard
A policy for Lambda to read messages that are placed in Amazon SQS:

Name: Lambda-Read-SQS
JSON:
{
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
Copy to clipboard
Step 1.2: Creating IAM roles and attaching policies to the roles

Because AWS follows the principle of least privilege, we recommend that you provide role-based access to only the AWS resources that are required to perform a task. In this step, you create IAM roles and attach policies to the roles.

In the navigation pane of the IAM dashboard, choose Roles.

Choose Create role and in the Select trusted entity page, configure the following settings:
Trusted entity type: AWS service
Common use cases: Lambda
Choose Next.

On the Add permissions page, select Lambda-Write-DynamoDB and Lambda-Read-SQS.

Choose Next

For Role name, enter Lambda-SQS-DynamoDB.

Choose Create role.

Follow the previous steps to create two more IAM roles:

An IAM role for AWS Lambda: This role grants permissions to obtain records from the DynamoDB streams and send the records to Amazon SNS. Use the following information to create the role.
IAM role name: Lambda-DynamoDBStreams-SNS
Trusted entity type: AWS service
Common use cases: Lambda
Attach policies: Lambda-SNS-Publish and Lambda-DynamoDBStreams-Read
An IAM role for Amazon API Gateway: This role grants permissions to send data to the SQS queue and push logs to Amazon CloudWatch for troubleshooting. Use the following information to create the role.
IAM role name: APIGateway-SQS
Trusted entity type: AWS service
Common use cases: API Gateway
Attach policies: AmazonAPIGatewayPushToCloudWatchLogs
Task 2: Creating a DynamoDB table

In this task, you create a DynamoDB table that ingests data that’s passed on through API Gateway.

In the search box of the AWS Management Console, enter DynamoDB.

From the list, choose the DynamoDB service.

On the Get started card, choose Create table and configure the following settings:
Table: orders
Partition key: orderID
Data type: Keep String
Keep the remaining settings at their default values, and choose Create table.

Task 3: Creating an SQS queue

In this task, you create an SQS queue. In the architecture for this exercise, the Amazon SQS receives data records from API Gateway, stores them, and then sends them to a database.

In the AWS Management Console search box, enter SQS and from the list, choose Simple Queue Service.

On the Get started card, choose Create queue.

The Create queue page appears.

Configure the following settings:
Name: POC-Queue
Access Policy: Basic
Define who can send messages to the queue:
Select Only the specified AWS accounts, IAM users and roles
In the box for this option, paste the Amazon Resource Name (ARN) for the APIGateway-SQS IAM role
Note: For example, your IAM role might look similar to the following: arn:aws:iam::<account ID>:role/APIGateway-SQS.
Define who can receive messages from the queue:
Select Only the specified AWS accounts, IAM users and roles.
In the box for this option, paste the ARN for the Lambda-SQS-DynamoDB IAM role.
Note: For example, your IAM role might look similar to the following: arn:aws:iam::<account_ID>:role/Lambda-SQS-DynamoDB
Choose Create queue.

Task 4: Creating a Lambda function and setting up triggers

In this task, you create a Lambda function that reads messages from the SQS queue and writes an order record to the DynamoDB table.

Step 4.1: Creating a Lambda function for the Lambda-SQS-DynamoDB role

In the AWS Management Console search box, enter Lambda and from the list, choose Lambda.

Choose Create function and configure the following settings:
Function option: Author from scratch
Function name: POC-Lambda-1
Runtime: Python 3.9
Change default execution role: Use an existing role
Existing role: Lambda-SQS-DynamoDB
Choose Create function.

Step 4.2: Setting up Amazon SQS as a trigger to invoke the function

If needed, expand the Function overview section.

Choose Add trigger.

For Trigger configuration, enter SQS and choose the service in the list.

For SQS queue, choose POC-Queue.

Add the trigger by choosing Add.

Step 4.3: Adding and deploying the function code

On the POC-Lambda-1 page, in the Code tab, replace the default Lambda function code with the following code:

import boto3, uuid

client = boto3.resource('dynamodb')
table = client.Table("orders")

def lambda_handler(event, context):
    for record in event['Records']:
        print("test")
        payload = record["body"]
        print(str(payload))
        table.put_item(Item= {'orderID': str(uuid.uuid4()),'order':  payload})
Copy to clipboard
Choose Deploy.

The Lambda code passes arguments to a function call. As a result, when a trigger invokes a function, Lambda runs the code that you specify.

When you use Lambda, you are responsible only for your code. Lambda manages the memory, CPU, network, and other resources to run your code.

Step 4.4: Testing the POC-Lambda-1 Lambda function

In the Test tab, create a new event that has the following settings:
Event name: POC-Lambda-Test-1
Template-Optional: SQS
The SQS template appears in the Event JSON field.

Save your changes and choose Test.

After the Lambda function runs successfully, the “Execution result: succeeded” message appears in the notification banner in the Test section. This means that the Lambda function sent a test message “Hello from SQS!” from the SQS template to the DynamoDB table.

Step 4.5: Verifying that the Lambda function adds the test message to a database

In the AWS Management Console search box, enter DynamoDB and from the list, choose DynamoDB.

In the navigation pane, choose Explore items.

Select the orders database. Under Items returned, the orders table returns “Hello from SQS!” from the Lambda function test.

Task 5: Enabling DynamoDB Streams

In this task, you enable DynamoDB Streams. A DynamoDB stream captures information about every modification to data items in the table.

In the DynamoDB console, in the Tables section of the navigation pane, choose Update settings.

In the Tables card, make sure that the orders table is selected.

Choose the Exports and streams tab.

In the DynamoDB stream details section, choose Enable.

For View type, choose New image.

Choose Enable stream.

After the Lambda function reads messages from the SQS queue and writes an order record to the DynamoDB table, DynamoDB Streams captures the primary key attributes from the record.

Task 6: Creating an SNS topic and setting up subscriptions

In this task, you create an SNS topic and set up subscriptions. Amazon SNS coordinates and manages delivering or sending messages to subscriber endpoints or clients.

Step 6.1: Creating a topic in the notification service

In the AWS Management Console, search for SNS and choose Simple Notification Service.

On the Create topic card, enter POC-Topic and choose Next step.

In the Details section, keep the Standard topic type selected and choose Create topic.

On the POC-Topic page, copy the ARN of the topic that you just created and save it for your reference.

You will need the ARN for the SNS topic later in this exercise.

Step 6.2: Subscribing to email notifications

On the Subscriptions tab, choose Create subscription.

For Topic ARN, make sure that the box contains the ARN for POC-Topic.

To receive notifications, for Protocol, choose Email.

For Endpoint, enter your email address.

Choose Create subscription.

The confirmation message is sent to the email address that you specified.

After you receive the confirmation email message, confirm the subscription. If you don’t receive an email message within a few minutes, check the spam folder.

Task 7: Creating an AWS Lambda function to publish a message to the SNS topic

In this task, you create a Lambda function for the Lambda-DynamoDBStreams-SNS role. The second Lambda function uses DynamoDB Streams as a trigger to pass the record of a new entry to Amazon SNS.

Step 7.1: Creating a POC-Lambda-2 function

In the AWS Management Console, search for and open AWS Lambda.

Create a new Lambda function by choosing Create function, and configure the following settings:
Function option: Author from scratch
Function name: POC-Lambda-2
Runtime: Python 3.9
Change default execution role: Use an existing role
Existing role: Lambda-DynamoDBStreams-SNS
This role grants permissions to get records from DynamoDB Streams and send them to Amazon SNS.

Choose Create function.

Step 7.2: Setting up DynamoDB as a trigger to invoke a Lambda function

In the Function overview section, choose Add trigger and configure the following settings:
Trigger configuration: Enter DynamoDB and from the list, choose DynamoDB.
DynamoDB table: orders
Keep the remaining default settings and choose Add.

In the Configuration tab, make sure that you are in the Triggers section and that the DynamoDB state is “Enabled.”

Step 7.3: Configuring the second Lambda function

Choose the Code tab and replace the Lambda function code with the following code:

import boto3, json

client = boto3.client('sns')

def lambda_handler(event, context):

    for record in event["Records"]:

        if record['eventName'] == 'INSERT':
            new_record = record['dynamodb']['NewImage']    
            response = client.publish(
                TargetArn='<Enter Amazon SNS ARN for the POC-Topic>',
                Message=json.dumps({'default': json.dumps(new_record)}),
                MessageStructure='json'
            )
Copy to clipboard
Note: In the function code, replace the TargetArn value with the ARN for the Amazon SNS POC-Topic. Make sure that you remove the placeholder angle brackets (<>).

Your ARN might look similar to the following: arn:aws:sns:us-east-1:<account ID>:POC-Topic.

Choose Deploy.

Step 7.4: Testing the POC-Lambda-2 Lambda function

On the Test tab, create a new event and for Event name, enter POC-Lambda-Test-2.

For Template-optional, enter DynamoDB and from the list, choose DynamoDB-Update.

The DynamoDB template appears in the Event JSON box.

Save your changes and choose Test.

After the Lambda function successfully runs, the “Execution result: succeeded” message should appear in the notification banner in the Test section.

In a few minutes, an email message should arrive at the email address that you specified in the previous task.

Confirm that you received the subscription email message. If needed, check both your inbox and spam folder.

Task 8: Creating an API with Amazon API Gateway

In this task, you create a REST API in Amazon API Gateway. The API serves as a communication gateway between your application and the AWS services.

In the AWS Management Console, search for and open API Gateway.

On the REST API card with a public authentication, choose Build and configure the following settings:
Choose the protocol: REST
Create new API: New API
API name: POC-API
Endpoint Type: Regional
Choose Create API.

On the Actions menu, choose Create Method.

Open the method menu by choosing the down arrow, and choose POST. Save your changes by choosing the check mark.

In the POST - Setup pane, configure the following settings:
Integration type: AWS Service
AWS Region: us-east-1
AWS Service: Simple Queue Service (SQS)
AWS Subdomain: Keep empty
HTTP method: POST
Action Type: Use path override
Path override: Enter your account ID followed by a slash (/) and the name of the POC queue
Note: If POC-Queue is the name of the SQS queue that you created, this entry might look similar to the following: /<account ID>/POC-Queue
Execution role: Paste the ARN of the APIGateway-SQS role
Note: For example, the ARN might look like the following: arn:aws:iam::<account ID>:role/APIGateway-SQS
Content Handling: Passthrough
Save your changes.

Choose the Integration Request card.

Scroll to the bottom of the page and expand HTTP Headers.

Choose Add header.

For Name, enter Content-Type

For Mapped from, enter 'application/x-www-form-urlencoded'

Save your changes to the HTTP Headers section by choosing the check mark.

Expand Mapping Templates and for Request body passthrough, choose Never.

Choose Add mapping template and for Content-Type , enter application/json

Save your changes by choosing the check mark.

For Generate template, do not choose a default template from the list. Instead, enter the following command: Action=SendMessage&MessageBody=$input.body in a box.

Choose Save.

Task 9: Testing the architecture by using API Gateway

In this task, you use API Gateway to send mock data to Amazon SQS as a proof of concept for the serverless solution.

In the API Gateway console, return to the POST - Method Execution page and choose Test.

In the Request Body box, enter:

{  "item": "latex gloves",
"customerID":"12345"}
Copy to clipboard
Choose Test.

If you see the “Successfully completed execution” message with the 200 response in the logs on the right, you will receive an email notification with the new entry. If you don’t receive an email, but the new item appears in the DynamoDB table, troubleshoot the exercise instructions starting from after you set up DynamoDB. Ensure that you deploy all of the resources in the us-east-1 Region.

After API Gateway successfully processes the request that you pasted in the Request Body box, it places the request in the SQS queue. Because you set up Amazon SQS as a trigger in the first Lambda function, Amazon SQS invokes the function call. The Lambda function code places the new entry into the DynamoDB table. DynamoDB Streams captures this change to the database and invokes the second AWS Lambda function. This function gets the new record from DynamoDB Streams and sends it to Amazon SNS. Amazon SNS, in turn, sends you an email notification.

Task 10: Cleaning up

In this task, you delete the AWS resources that you created for this exercise.

Delete the DynamoDB table.
Open the DynamoDB console.
In the navigation pane, choose Tables.
Select the orders table.
Choose Delete and confirm your actions.
Delete the Lambda functions.
Open the Lambda console.
Select the Lambda functions that you created in this exercise: POC-Lambda-1 and POC-Lambda-2.
Choose Actions, Delete.
Confirm your actions and close the dialog box.
Delete the SQS queue.
Open the Amazon SQS console.
Select the queue that you created in this exercise.
Choose Delete and confirm your actions.
Delete the SNS topic and subscriptions.
Open the Amazon SNS console.
In the navigation pane, choose Topics.
Select POC-Topic.
Choose Delete and confirm your actions.
In the navigation pane, choose Subscriptions.
Select the subscription that you created in this exercise and choose Delete.
Confirm your actions.
Delete the API that you created.
Open the API Gateway console.
Select POC-API.
Choose Actions, Delete.
Confirm your actions.
Delete the IAM roles and policies.
Open the IAM console.
In the navigation pane, choose Roles.
Delete the following roles and confirm your actions:
APIGateway-SQS
Lambda-SQS-DynamoDB
Lambda-DynamoDBStreams-SNS
In the navigation pane, choose Policies.
Delete the following custom policies and confirm your actions:
Lambda-DynamoDBStreams-Read
Lambda-SNS-Publish
Lambda-Write-DynamoDB
Lambda-Read-SQS
Congratulations! You have successfully completed the exercise.