#
# config.py
#
# Base class for AWS config related functions via boto3
# Define the standard member functions to allow naming and behaviors across all config classes
#

import logging
import boto3
from botocore.exceptions import ClientError

# TODO: look into logger configurations & identify log locations
logger = logging.getLogger(__name__)

class Config:

    def __init__(self, boto_name, dict=None):
        self.boto_client = boto3.client(boto_name)
        self.dict = dict
        
    # common attributes
    def accountId(self):
        if self.accountId is None:
            self.accountId = boto3.client('sts').get_caller_identity().get('Account')
        return self.accountId
    
    def region(self):
        if self.region is None:
            self.region = boto3.session.Session().region_name
        return self.region

    def list(self):
        """
        Determine to list all the resources in the running account, 
        or list just the "scoped" resources defined in dict

        :return: The list of resources based on the context of the object
        """
        if self.dict is not None:
            ## filter by the items in dict  
            filtered_list = self.dict.keys()
        else:
            filtered_list = None

        resources = self.do_list()

        if filtered_list is not None:
            return [item for item in resources if item in filtered_list]
        return resources

    def do_create(self, _client, _dict):
        logger.error("do_create not implemented for this class")
        return
                  
    def create(self):
        """
        Decrypts text previously encrypted with a key.

        :param key_id: The ARN or ID of the key used to decrypt the data.
        :param cipher_text: The encrypted text to decrypt.
        """
        if self.dict is None:
            print("No resource definition to create")
            return
        return do_create(self, self.boto_client, self.dict)
    

    def do_delete(self, _client, _dict):
        logger.error("do_delete not implemented for this class")
        return
    
    def delete(self):
        """
        Decrypts text previously encrypted with a key.

        :param key_id: The ARN or ID of the key used to decrypt the data.
        :param cipher_text: The encrypted text to decrypt.
        """
        if self.dict is None:
            print("No resource definition to delete")
            return
        return do_delete(self, self.boto_client, self.dict)


    
if __name__ == "__main__":
    print("This is the base class for AWS config related functions via boto3")
    #logging.exception("Something went wrong with the demo!")

