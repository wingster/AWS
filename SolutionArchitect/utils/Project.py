#
# Project.py
#
# Project class to manage the list of AWS configuration objects required to allocate/deallocate the defined resources
#
#

from Config import Config
from IamRole import IamRole
import boto3

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
        self.configs[config_class] = (config_class(config_dict), config_dict)
        return
    
    def create(self, config_class=None):
        # get the config object from the 1st of the tuple
        if config_class is None:
            #size of the config dietionary
            print(f"Number of Config classes in project : {len(self.configs)}")
            for key in self.configs:
                config_object, config_dictionary = self.configs[key]
                config_object.create()
            return
        else:
            config_object, config_dictionary = self.configs[config_class]
            config_object.create()

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
        configObj, _ = self.configs[service]
        return configObj
    

    
