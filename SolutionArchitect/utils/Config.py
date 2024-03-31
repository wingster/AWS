#
# config.py
#
# Base class for AWS config related functions via boto3
# * Define the standard member functions to allow naming and behaviors across all config classes
# * Add boto3 session support - allow the code to run as a specific role 
#

import sys
import logging
import boto3
from botocore.exceptions import ClientError
import pandas as pd

from enum import Enum

class Status(Enum):
    FAILED = -1  # Action failed - unexpected result
    SUCCESS = 0  # Action carried out and successful
    NO_OP = 1  # Action didn't carry out due to expected state

class Action(Enum):
    CREATE = "create"
    DELETE = "delete"

# TODO: look into logger configurations & identify log locations
logger = logging.getLogger(__name__)

class Config:
    _accountId = None
    _region = None

    def __init__(self, botoName, inputMap=None, session=None):
        self.session = session
        self.botoClient = boto3.client(botoName) if session is None else session.client(botoName)
        self.configMap = inputMap
        self.resourceMap = {}
        self.dirty = True  # set dirty to true to refresh the resource map on the next op
        
    # class static function to get accountId()
    @staticmethod
    def accountId():
        if Config._accountId is None:
            Config._accountId = boto3.client('sts').get_caller_identity().get('Account')
        return Config._accountId
    
    # class static function to get region()
    @staticmethod
    def region():
        if Config._region is None:
            Config._region = boto3.session.Session().region_name
        return Config._region
    
    # Add the list of attributes assoicated with names to the internal resource map
    def addResource(self, name, attributes):
        self.resourceMap[name] = attributes

    # retreive the Arn for the input resource name from the internal resource map
    def getArn(self, name):
        # or if the resource map is empty
        if name not in self.resourceMap.keys():
            print(f"Resource name not found: {name}, re-populating list")
            self.list()
        return self.resourceMap[name]['Arn']

    def do_list(self):
        logger.info("Calling Config.do_list")
        warnMsg = "Config.do_create not implemented for the base class"
        logger.warning(warnMsg)
        status = Status.FAILED
        return status, warnMsg


        
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
        # Delegate to the child class to select the attributes for the given resource to be included in the resource map
        # Once this is more mature we can have the child class to identify the list of tags to extract from the response structure
        # i.e. once we have implemented and observed similarity with the extraction logic
        self.dirty = False

        ret = resources
        if filtered_list is not None:
            ret = [item for item in resources if item in filtered_list]

        
        df = pd.DataFrame(self.resourceMap)
        # Display the tranposed dataframe without skipping and data
        df.transpose().to_csv(sys.stdout, index=False, header=False)
        print(df.transpose())
        # TODO: define what should be returned for list ? the internal resource map or the transposed DF ?
        return ret


    def action(self, action, do_action):
        """
        Action on Resources for the given service based on input dictionary

        """
        if self.configMap is None:
            warnMsg = "No input resource definition"
            logger.warning(warnMsg)
            return Status.No_OP, warnMsg
        
        # Refresh the internal map if dirty
        if self.dirty:
            self.list()

        overall_status = Status.NO_OP
        successKeys = []
        successResponses = []
        noopKeys = []
        resultMap = {}
    
        # Iterate through the configMap and call do_action for each item in the configMap
        for key, config in self.configMap.items():

            proceed = key in self.resourceMap.keys()
            if action==Action.CREATE:
                proceed = not proceed  # create only if the key doesn't exist in the resource map
            elif action==Action.DELETE:
                pass
            else:
                errorMsg = f"Unknown action {action}"
                logger.error(errorMsg)
                overall_status = Status.FAILED
                resultMap["ErrorKey"] = key
                resultMap["ErrorMessage"] = errorMsg
                return overall_status, resultMap

            if proceed:
                status, result = do_action(self.botoClient, key, config)
                if status == Status.FAILED:
                    logger.error(f"Failed to {action.value} resource {key} with message {result}")
                    overall_status = Status.FAILED
                    resultMap["ErrorKey"] = key
                    resultMap["ErrorMessage"] = result
                    break
                elif status == Status.SUCCESS:
                    logger.info(f"Successfully {action.value}d resource {key}")
                    successKeys.append(key)
                    successResponses.append(result)
                    self.dirty = True  # set dirty to true to refresh the resource map on the next op
                else:
                    logger.error(f"Unknown status for resource {key} with message {result}")
                    overall_status = Status.FAILED
                    resultMap["ErrorKey"] = key
                    resultMap["ErrorMessage"] = result
                    break
            else:  # key already exists in the resource map
                logger.info(f"No-op for resource {key}")
                noopKeys.append(key)
            
        if overall_status == Status.SUCCESS or overall_status == Status.NO_OP:
            logger.info(f"executed {action.value} resources for {successKeys}")
            resultMap["SuccessKeys"] = successKeys
            resultMap["SuccessResponses"] = successResponses
            resultMap["NoopKeys"] = noopKeys

        return overall_status, resultMap
        
    def do_create(self, client, key, config):
        logger.info(f"Calling Config.do_create with {key}, {config}")
        warnMsg = "Config.do_create not implemented for the base class"
        logger.warning(warnMsg)
        status = Status.FAILED
        return status, warnMsg
    
    def create(self):
        """
        Create Resources for the given service based on input dictionary
        """
        return self.action(Action.CREATE, self.do_create)
                  

    
    def do_delete(self, botoClient, key, config):
        logger.info(f"Calling Config.do_delete with {key}, {config}")
        warnMsg = "Config.do_delete not implemented for the base class"
        logger.warning(warnMsg)
        status = Status.FAILED
        return status, warnMsg
    
    def delete(self):
        """
        delete Resources for the given service based on input dictionary
        """
        return self.action(Action.DELETE, self.do_delete)



def unitTest():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    std_definition = {
        "key1" : {
            "tag1": "value1",
            "accountId": Config.accountId(),
            "region": Config.region(),
        },
        "key2" : {
            "tag1": "value3",
            "accountId": "12345678",
            "region": "us-east-1",
        }
    }
    
    print("Dummy Test Config")
    testConfig = Config("s3", std_definition)
    print("Dummy Test Config - list ")
    testConfig.list()
    print("Dummy Test Config - create ")
    status, result = testConfig.create()
    print(f"create status: {status}, result: {result}")
    print("Dummy Test Config - delete ")
    status, result = testConfig.delete()
    print(f"delete status: {status}, result: {result}")
    return True


def main(argv):
      # argv[0] is the script name, print remaining arguments separated by space without the bracket
    print("Running :", " ".join(argv[0:]))
    
    # if no additonal arguments are passed, print usage help
    if len(argv) != 2 or argv[1] not in ["unit"]:
        print("Usage: python3 Config.py <unit> ")
        return
    else:
        # if additional arguments are passed, proceed with the action
        action = argv[1]
        if action == "unit":
            unitTest()
        else:
            print(f"Unknown action: '{action}'" )


if __name__ == "__main__":
    main(sys.argv)

