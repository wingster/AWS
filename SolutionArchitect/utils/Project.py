#
# Project.py
#
# Project class to manage the list of AWS configuration objects required to allocate/deallocate the defined resources
#
#

import sys
import os
import boto3

from Config import Config, Status
from IamRole import IamRole

# additional classes required for unit test
from IamPolicy import IamPolicy
from Kms import Kms


class Project:

    def __init__(self, name, roleName=None):
        self.name = name
        self.session = None if roleName is None else self.getSessionByRole(roleName)
        self.configs = {}   ## dictionary to maintain the list of AWS configuration objects - as it usally tracks additional information & cache objects


    def getSessionByRole(self, roleName):
        # get the session object for the role
        roleArn = IamRole().getArn(roleName)

        # Do something simple for now
        if roleArn is None:
            print(f"Role {roleName} not found")
            return None
        
        # Create STS client
        sts_client = boto3.client('sts')

        # Call the assume_role method 
        response = sts_client.assume_role(
            RoleArn=roleArn,
            RoleSessionName=self.name
        )

        # Get the temporary credentials
        credentials = response['Credentials']

        # Pass the temporary credentials to the boto3 session
        session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        return session


    def addConfig(self, config_class, config_dict=None):
        self.configs[config_class] = (config_class(inputMap=config_dict, session=self.session), config_dict)
        return
    
    def create(self, config_class=None):
        # get the config object from the 1st of the tuple
        status = Status.NO_OP
        result_map = {}
        if config_class is None:
            #size of the config dietionary
            print(f"Number of Config classes in project : {len(self.configs)}")
            for key in self.configs:
                config_object, config_dictionary = self.configs[key]
                sub_status, sub_results = config_object.create()
                if sub_status == Status.FAILED:
                    status = Status.FAILED
                    result_map[key] = sub_results
                    print(f"Error creating config {key}")
                    print(sub_results)
                elif sub_status == Status.NO_OP:
                    continue
                elif sub_status == Status.SUCCESS:
                    status = Status.SUCCESS
                    result_map[key] = sub_results
                    print(f"Success creating config {key}")
                else:
                    status = Status.FAILED
                    result_map[key] = sub_results
                    print(f"Unknown status while creating config {key}")
                
                # break if any of the config subclass creation failed
                if status == Status.FAILED:
                    break

            return status, result_map
        else:
            config_object, config_dictionary = self.configs[config_class]
            return config_object.create()

    def delete(self, config_class=None):
        # get the config object from the 1st of the tuple
        if config_class is None:
            #size of the config dietionary
            print(f"Number of Config classes in project : {len(self.configs)}")
            for key in self.configs:
                config_object, config_dictionary = self.configs[key]
                config_object.delete()
            return
        else:
            config_object, config_dictionary = self.configs[config_class]
            config_object.delete()
        return


    def list(self, config_class=None):
        # get the config object from the 1st of the tuple
        if config_class is None:
            #size of the config dietionary
            print(f"Number of Config classes in project : {len(self.configs)}")
            for key in self.configs:
                config_object, config_dictionary = self.configs[key]
                config_object.list()
            return
        else:
            config_object, config_dictionary = self.configs[config_class]
            config_object.list()
    
    

    def printConfigs(self):
        for key in self.configs:
            print(key, self.configs[key])
        return
    
    def getConfig(self, service):
        # get the config object from the 1st of the tuple
        if service not in self.configs:
            print(f"Config {service} not found:")
            for key in self.configs:
                print(f"\t{key}")
            return None
        # get the config object from the 1st of the tuple
        configObj, _ = self.configs[service]
        return configObj
    

    @staticmethod
    def getConfigArn(project, service, name):
        configObj = project.getConfig(service)
        yield configObj.getArn(name)
    

def unitTest():
    # create a project object
    project = Project("Unit-Test")

    # TODO: find ways to reference this sample kms_definition from KMS instead of value-copy
    kms_definition = {  
        "Common-UnitTest-Kms-001": {
            "Description": "UnitTest KMS Test Key 001",
            "KeyUsage": "ENCRYPT_DECRYPT",
            "Origin": "AWS_KMS",  # AWS_KMS, EXTERNAL, or AWS_CLOUDHSM
            "KeySpec": "SYMMETRIC_DEFAULT",  # RSA_2048, RSA_3072, RSA_4096, ECC_NIST_P256, ECC_NIST_P384, ECC_NIST_P521, or SYMMETRIC_DEFAULT
            "Tags" : [
                {   "TagKey"  : "Context",
                    "TagValue": "Common-UnitTest-Kms"},
                {   "TagKey" : "Environment", 
                    "TagValue" : "UnitTest"}
            ],
        },
    }

    policy_definition = {
        "Common-UnitTest-Project-IamPolicy-001" : {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "kms:ListKeys",
                        "kms:Encrypt",
                    ],
                    "Resource": [ # restrict to the below key only - required ARN...
                        Project.getConfigArn(project, Kms, "Common-UnitTest-Kms-001")
                    ]
                }
            ]
        }       
    }

    role_definition = {
        "Common-UnitTest-Project-IamRole-001" : {
            "PrincipalType" : "AWS",
            "AWS" : Config.accountId(),
            "UserPolicies" : ["Common-UnitTest-Project-IamPolicy-001"],
            "AWSPolicies" : [],
        },
    }

    # Now add the config objects
    project.addConfig(IamPolicy, policy_definition)
    project.addConfig(IamRole, role_definition)
    project.addConfig(Kms, kms_definition)

    project.printConfigs()

    status, results = project.create()
    if status == Status.FAILED:
        print(f"Error creating project {project.name}")
        print(results)
        return Status.FAILED

    project.list()
    #project.delete()

    
    

#if this .py is executed directly on the command line
def main(argv):
    # argv[0] is the script name, print remaining arguments separated by space without the bracket
    print("Running :", " ".join(argv[0:]))
    
    # if no additonal arguments are passed, print usage help
    if len(argv) != 2 or argv[1] not in ["create", "delete", "list", "unit"]:
        print(f"Usage: python3 {argv[0]} <create|delete|list|unit> ")
        return
    else:
        # if additional arguments are passed, proceed with the action
        
        action = argv[1]
        if action == "create":
            pass 
        elif action == "delete":
            pass
        elif action == "list":
            pass
        elif action == "unit":
            unitTest()


if __name__ == "__main__":
    main(sys.argv)

    
