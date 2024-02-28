#
#
# Note : As specified in this blog: https://aws.amazon.com/blogs/compute/announcing-http-apis-for-amazon-api-gateway/
# There are currently two API Gateway namespaces for managing API Gateway deployments. The API V1 namespace represents REST APIs and API V2 represents WebSocket APIs and the new HTTP APIs.
# The HTTP APIs are cheaper to operate but contains less features than the REST APIs.  A matrix of feature comparsion between the two are listed here : https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html 
#
# As this exercise only deals with REST APIs, we will use the API V1 namespace here
# We will investigate at a later time to unified the two under the same helper function
#

# Task 8: Creating an API with Amazon API Gateway
# In this task, you create a REST API in Amazon API Gateway. The API serves as a communication gateway between your application and the AWS services.
# In the AWS Management Console, search for and open API Gateway.

# On the REST API card with a public authentication, choose Build and configure the following settings:
# Choose the protocol: REST
# Create new API: New API
# API name: POC-API
# Endpoint Type: Regional
# Choose Create API.

# On the Actions menu, choose Create Method.

# Open the method menu by choosing the down arrow, and choose POST. Save your changes by choosing the check mark.

# In the POST - Setup pane, configure the following settings:
# Integration type: AWS Service
# AWS Region: us-east-1
# AWS Service: Simple Queue Service (SQS)
# AWS Subdomain: Keep empty
# HTTP method: POST
# Action Type: Use path override
# Path override: Enter your account ID followed by a slash (/) and the name of the POC queue
# Note: If POC-Queue is the name of the SQS queue that you created, this entry might look similar to the following: /<account ID>/POC-Queue
# Execution role: Paste the ARN of the APIGateway-SQS role
# Note: For example, the ARN might look like the following: arn:aws:iam::<account ID>:role/APIGateway-SQS
# Content Handling: Passthrough
# Save your changes.

# Choose the Integration Request card.
# Scroll to the bottom of the page and expand HTTP Headers.
# Choose Add header.
# For Name, enter Content-Type
# For Mapped from, enter 'application/x-www-form-urlencoded'
# Save your changes to the HTTP Headers section by choosing the check mark.
# Expand Mapping Templates and for Request body passthrough, choose Never.
# Choose Add mapping template and for Content-Type , enter application/json
# Save your changes by choosing the check mark.

# For Generate template, do not choose a default template from the list. Instead, enter the following command: Action=SendMessage&MessageBody=$input.body in a box.
# Choose Save.

import boto3, sys
import json
import time
from datetime import date, datetime
from poc_sqs import get_sqs_queue_arn
from poc_iam_role import get_arn_by_role_name


api_gateway_definitions = {
    "POC1-API": {
        "endpoint_type": "REGIONAL",
        "resources" : {
            "/" : {
                "POST" : {
                    "method_request" : {
                    },
                    "integration_request" : {
                        "type" : "AWS",
                        "service" : "sqs",
                        "region" : "us-east-1",     ## required to construct the URI
                        "subdomain" : "",           ## Part of the console screen but not populated in this example
                        "http_method" : "POST",    ## this is the http_method to to backend. Does not necessary have to be the same as the request method
                        # Need to include additonal parameters to synthesize the URI
                        # pick the last two components from the sqs arn
                        "service_path" : get_sqs_queue_arn("POC1-Queue").split(':')[-2:],
                        "execution_role" : get_arn_by_role_name("POC1-APIGateway-SQS"),
                        #"contentHandling" : "PASS_THROUGH",
                        "timeoutInMillis" : 29000,
                        "passthroughBehavior" : "NEVER",
                        "requestParameters" : {
                            "integration.request.header.Content-Type" : "'application/x-www-form-urlencoded'"
                        },
                        "requestTemplates" : {
                            "application/json" : "Action=SendMessage&MessageBody=$input.body"
                        },
                        "integrationResponses" : {
                            "200" : {
                                "statusCode" : "200",
                                "responseTemplates" : {
                                    "application/json" : ""
                                },
                            }
                        },
                    },
                }
            }
        }
    }


}

# create api_gateway based on definitions
def create_api_gateway():
    # stick with apigateway v1 here as this exercsie called for REST, create api_gateway resources based on definition
    api_gateway_client = boto3.client('apigateway')

    # create api_gateway based on definition
    for api_name, definition in api_gateway_definitions.items():
        # create websocket API gateway
        rest_api = api_gateway_client.create_rest_api(
            name=api_name,
            endpointConfiguration={
                'types': [definition['endpoint_type']]
            }
        )
        # get api_gateway id
        api_gateway_id = rest_api['id']
        for path, resource in definition['resources'].items():
            # create api_gateway resource
            if path == '/':
                resourceId = rest_api['rootResourceId']
            else:
                print (f"creating resource for {api_gateway_id}, under root resource {rest_api['rootResourceId']}")
                response = api_gateway_client.create_resource(
                    restApiId=api_gateway_id,
                    parentId=rest_api['rootResourceId'],
                    pathPart=path
                )
                resourceId = resourceId = response['id']

            print (f"resourceId = {resourceId}")
            # create api_gateway method integration
            for method, method_definition in resource.items():
                response = api_gateway_client.put_method(
                    restApiId=api_gateway_id,
                    resourceId=resourceId,
                    httpMethod=method,
                    authorizationType='NONE' # this is a required parameter and isn't optional :-(
                )
                # create api_gateway method integration
                # gets really complicated -> see this example on github : https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code/api-gateway/aws_service/aws_service.py

                # service URI needs to be synthesized.....from the below template ...
                service_uri = (f"arn:aws:apigateway:{method_definition['integration_request']['region']}:{method_definition['integration_request']['service']}:path/{'/'.join(method_definition['integration_request']['service_path'])}")
                # first print the content of the method_definition[integration_request]
                print (f"method_definition[integration_request] = {method_definition['integration_request']}")
                print (f"service_uri = {service_uri}")

                response = api_gateway_client.put_integration(
                    restApiId=api_gateway_id,
                    resourceId=resourceId,
                    httpMethod=method,
                    type=method_definition['integration_request']['type'],
                    integrationHttpMethod=method_definition['integration_request']['http_method'],
                    uri=service_uri,
                    credentials=method_definition['integration_request']['execution_role'],
                    #contentHandling=method_definition['integration_request']['contentHandling'],
                    timeoutInMillis=method_definition['integration_request']['timeoutInMillis'],
                    passthroughBehavior=method_definition['integration_request']['passthroughBehavior'],
                    requestParameters=method_definition['integration_request']['requestParameters'],
                    requestTemplates=method_definition['integration_request']['requestTemplates'],
                    #integrationResponses=method_definition['integration_request']['integrationResponses'],
                )
                #time.sleep(5)
                response = api_gateway_client.put_integration_response(
                    restApiId=api_gateway_id,
                    resourceId=resourceId,
                    httpMethod=method,
                    statusCode='200',
                    responseTemplates={
                        'application/json': '' 
                    }
                )

                # add method response

                response = api_gateway_client.put_method_response(
                    restApiId=api_gateway_id,
                    resourceId=resourceId,
                    httpMethod=method,
                    statusCode='200',
                    responseModels={
                        'application/json': 'Empty'
                    }
                )


# delete api_gateway
def delete_api_gateway():
    #iterate through api_gateway_definitions and delete api_gateway and all of the associated resources
    api_gateway_client = boto3.client('apigateway')
    apis = api_gateway_client.get_rest_apis()['items']

    for api_name, definition in api_gateway_definitions.items():
        # find the item inside apis that match the api_name
        api_gateway = [api for api in apis if api['name'] == api_name]
        for item in api_gateway:
            print(f'deleting {item}')
            api_gateway_id = item['id']

            # delete api_gateway
            response = api_gateway_client.delete_rest_api(
                restApiId=api_gateway_id
            )
            print(f"Deleted API Gateway {api_name} with response: {response}")
            # delete all of the associated resources
            for path in definition['resources']:
                # get api_gateway resource id
                if path == '/':
                    resourceId = item['rootResourceId']
                else:
                    response = api_gateway_client.get_resources(restApiId=api_gateway_id, pathPart=path)
                    resourceId = response['items'][0]['id']
                    # delete api_gateway resource
                    response = api_gateway_client.delete_resource(
                        restApiId=api_gateway_id,
                        resourceId=resourceId
                    )
                    print(f"Deleted resource {path} with response: {response}")
    return

#
# helper function to convert python object to json format with default handler for datetime: 
# https://stackoverflow.com/questions/11875770/how-can-i-overcome-datetime-datetime-not-json-serializable
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

# list api_gateway
def list_api_gateway():
    # display a list of api_gateway defined in this account
    api_gateway_client = boto3.client('apigateway')
    apis = api_gateway_client.get_rest_apis()['items']

    # print apis in a formatting json format
    # added default handler to deal with datetime: https://stackoverflow.com/questions/11875770/how-can-i-overcome-datetime-datetime-not-json-serializable
    #print(json.dumps(apis, indent=4, sort_keys=True, default=json_serial))

    for api in apis:
        # print(json.dumps(api, indent=4, sort_keys=True, default=json_serial))
        print("============================================")
        print(f"API Name: {api['name']}, API ID:{api['id']}")
        # show the methods assoicaated with this api
        for resource in api_gateway_client.get_resources(restApiId=api['id'])['items']:
            print(f"Resource: {resource}")
            path = resource['path']
            methods = resource['resourceMethods'] if "resourceMethods" in resource else []
            for method in methods:
                print(f"Path = {path} Method: {method}")
                integration = api_gateway_client.get_method(
                    restApiId=api['id'],
                    resourceId=resource['id'],
                    httpMethod=method)
                if "methodIntegration" in integration:
                    print(json.dumps(integration['methodIntegration'], indent=4, sort_keys=True))
                #print(json.dumps(integration['methodResponses'], indent=4, sort_keys=True))



                # print(f"Integration: {integration}")
                # print(f"Integration type: {integration['methodIntegration']['type']}")
                # print(f"Integration URI: {integration['methodIntegration']['uri']}")
                # print(f"Integration request parameters: {integration['methodIntegration']['requestParameters']}")
                # print(f"Integration request templates: {integration['methodIntegration']['requestTemplates']}")
                # #print(f"Integration response parameters: {integration['methodIntegration']['responseParameters']}")
                # #print(f"Integration response templates: {integration['methodIntegration']['responseTemplates']}")
                # print(f"Integration credentials: {integration['methodIntegration']['credentials']}")
                # print(f"Integration cache namespace: {integration['methodIntegration']['cacheNamespace']}")
                # print(f"Integration cache key parameters: {integration['methodIntegration']['cacheKeyParameters']}")
                # #print(f"Integration content handling: {integration['methodIntegration']['contentHandling']}")
                # print(f"Integration timeout: {integration['methodIntegration']['timeoutInMillis']}")
                # print(f"Integration passthrough behavior: {integration['methodIntegration']['passthroughBehavior']}")
                # print(f"Integration http method: {integration['methodIntegration']['httpMethod']}")
                # #print(f"Integration request headers: {integration['methodIntegration']['requestHeaders']}")





            




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
            create_api_gateway()
        elif action == "delete":
            delete_api_gateway()
        elif action == "list":
            list_api_gateway()


if __name__ == "__main__":
    main(sys.argv)

