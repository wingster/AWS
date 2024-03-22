## Common Utilites for AWS Configurations & Labs  

* Inspect existing AWS configurations (i.e w/o project specific configurations) 
* Add/Remove/Inspect project specific AWS configurations (i.e. with user specified configurations)
* Ability to chain project related modules to support full project setup and removal (investigate transactional model: exception would rollback any partial setup ?!)
* Execute the setup/removal operations in proper order to allow dependency between modules (e.g. IAM roles first to create and last to remove)
* Based on boto3 Q Chat/CodeWhisperer and github python examples : https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/python/example_code

This code will require the same setup for default credentials and AWS Region configured : https://docs.aws.amazon.com/sdkref/latest/guide/creds-config-files.html

* Investigate (capture/replay) testing strategy since running these services may incur charges 
