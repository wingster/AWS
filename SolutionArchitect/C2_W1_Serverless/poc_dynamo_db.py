# Create DynamoDB table that ingests data that's passed on through API Gateway
# Please refer to the Readme.md file for the architectural diagram and additional details.
# URL for the POC: https://aws-tc-largeobjects.s3.us-west-2.amazonaws.com/DEV-AWS-MO-Architecting/exercise-1-serverless.html
#
# In this python script, it will use boto3 to create & cleanup the DynamoDB resources 
# Step 2: Create table and configure the following settings:
#     Table: POC1_orders
#     Partition key: orderID
#     Data type: String

import boto3
import json
import sys

dynamodb_definitions = {
    "POC1_orders": {
        "PartitionKey":{
            "orderID": {
                "DataType": "S",
                "KeyType": "HASH"
            },
        },
        "Stream": {
            "Enable" : True,
            "ViewType": "NEW_IMAGE",
        },  
    }
}


# create_tables will create the DynamoDB table that ingests data that's passed on through API Gateway
def create_tables():
    # create the DynamoDB resource
    dynamodb = boto3.resource('dynamodb')

    # read the dynamodb_definitions and create the tables as specified
    for table_name, table_definition in dynamodb_definitions.items():
        # Iterate the partitionkey dictionary and append to keySchema
        keySchema = []
        for key, value in table_definition['PartitionKey'].items():
            keySchema.append({
                'AttributeName': key,
                'KeyType': value['KeyType']
            })
        
        # Iterate the partitionkey dictionary and append to attributeDefinitions
        attributeDefinitions = []
        for key, value in table_definition['PartitionKey'].items():
            attributeDefinitions.append({
                'AttributeName': key,
                'AttributeType': value['DataType']
            })

        # create the DynamoDB table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=keySchema,
            AttributeDefinitions=attributeDefinitions,
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            },
            StreamSpecification={
                'StreamEnabled': table_definition['Stream']['Enable'],
                'StreamViewType': table_definition['Stream']['ViewType'],
            },
        )

        # print the table status
        print(f"Table status: {table.table_status}")


# delete_tables will delete the DynamoDB table that ingests data that's passed on through API Gateway
def delete_tables():
    # create the DynamoDB resource
    dynamodb = boto3.resource('dynamodb')

    # delete the DynamoDB tables as specified in the dynamodb_definitions
    for table_name, table_definition in dynamodb_definitions.items():
        # delete the DynamoDB table
        table = dynamodb.Table(table_name)
        table.delete()
    # print the table status
    print(f"Table status: {table.table_status}")

def list_tables():
    # create the DynamoDB resource
    dynamodb = boto3.resource('dynamodb')

    # list the DynamoDB tables
    tables = dynamodb.tables.all()

    # if tables is empty or zero length, print "No tables found"
    if len(list(tables)) == 0:
        print("No tables found")
        return
    
    # print the list of tables
    for table in tables:
        print(table.name)
        print(table.table_status)
        print(table.creation_date_time)
        print(table.item_count)
        print(table.table_size_bytes)
        print(table.table_arn)
        print(table.table_id)
        print(table.billing_mode_summary)
        print(table.key_schema)
        print(table.local_secondary_indexes)
        print(table.global_secondary_indexes)
        print(table.provisioned_throughput)
        print(table.stream_specification)
        print(table.latest_stream_label)


def get_dynamodb_table_arn(table_name):
    # create the DynamoDB resource
    dynamodb = boto3.resource('dynamodb')

    # get the DynamoDB table
    table = dynamodb.Table(table_name)

    # check if the table result is valid  
    if not table:
        print(f"DynamoDB Table {table_name} not found")
        return None

    # return the table arn
    return table.table_arn


def get_dynamodb_stream_arn(table_name):
    # create the DynamoDB resource
    dynamodb = boto3.resource('dynamodb')

    # get the DynamoDB table
    table = dynamodb.Table(table_name)

    # check if the table result is valid
    if not table:
        print(f"DynamoDB Table {table_name} not found")
        return None

    # return the table arn
    return table.latest_stream_arn

 



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
            create_tables()
        elif action == "delete":
            delete_tables()
        elif action == "list":
            list_tables()


if __name__ == "__main__":
    main(sys.argv)

