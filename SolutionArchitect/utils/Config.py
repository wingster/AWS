#
# config.py
#
# Base class for AWS config related functions via boto3
# * Define the standard member functions to allow naming and behaviors across all config classes
# * Add boto3 session support - allow the code to run as a specific role 
#

import logging
import boto3
from botocore.exceptions import ClientError
import pandas as pd

# TODO: look into logger configurations & identify log locations
logger = logging.getLogger(__name__)

class Config:

    def __init__(self, botoName, inputMap=None, session=None):
        self.session = session
        self.botoClient = boto3.client(botoName) if session is None else session.client(botoName)
        self.configMap = inputMap
        self.resourceMap = {}
        
    # common attributes
    def accountId(self):
        if self.accountId is None:
            self.accountId = boto3.client('sts').get_caller_identity().get('Account')
        return self.accountId
    
    def region(self):
        if self.region is None:
            self.region = boto3.session.Session().region_name
        return self.region
    

    def addResource(self, name, arn):
        self.resourceMap[name] = arn

    def getArn(self, name):
        if name not in self.resourceMap.keys():
            print(f"Resource name not found: {name}, re-populating list")
            self.list()
        return self.resourceMap[name]['Arn']

    def list(self):
        """
        Determine to list all the resources in the running account, 
        or list just the "scoped" resources defined in dict

        :return: The list of resources based on the context of the object
        """
        if self.configMap is not None:
            ## filter by the items in dict  
            filtered_list = self.configMap.keys()
        else:
            filtered_list = None

        resources = self.do_list()

        ret = resources
        if filtered_list is not None:
            ret = [item for item in resources if item in filtered_list]
        
        df = pd.DataFrame(self.resourceMap)
        print(df.transpose())

        #for key, value in self.resourceMap.items():
        #    print(key, value) 
        return ret

    def do_create(self, client, configMap):
        logger.error("do_create not implemented for the base class")
        return
                  
    def create(self):
        """
        Create Resources for the given service based on input dictionary

        """
        if self.configMap is None:
            print("No resource definition to create")
            return
        return self.do_create(self.botoClient, self.configMap)
    

    def do_delete(self, botoClient, configMap):
        logger.error("do_delete not implemented for this class")
        return
    
    def delete(self):
        """
        delete Resources for the given service based on input dictionary
        """
        if self.configMap is None:
            print("No resource definition to delete")
            return
        return self.do_delete(self.botoClient, self.configMap)


    
if __name__ == "__main__":
    print("This is the base class for AWS config related functions via boto3")
    #logging.exception("Something went wrong with the demo!")

