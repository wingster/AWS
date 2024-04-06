import unittest
from Config import Config, Status
# import UnknownServiceError exception from botocore
from botocore.exceptions import UnknownServiceError

class configTest(unittest.TestCase):
    # define static setUp method
    @classmethod
    def setUpClass(cls):
        print("setUpClass")
        # sample config JSON to drive the various functionalities for the
        # config base class
        cls.config_definition = {
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
        cls.testConfig = Config(botoName="s3", inputMap=cls.config_definition)

    def test_config_base(self):
        # supply dummy botoName - config isn't proper to instantiate any service - expects UnknownServiceError
        with self.assertRaises(UnknownServiceError):
            Config(botoName="dummy", inputMap=configTest.config_definition)


    def test_config_creation(self):
        status, result = configTest.testConfig.create()
        self.assertEqual(status, Status.FAILED)
        self.assertEqual(result['ErrorMessage'], "Failure in refreshing resource list")
        self.assertEqual(result['ErrorKey'], "*")


    def test_config_list(self):
        status, listResult = configTest.testConfig.list()
        self.assertEqual(status, Status.FAILED)
        self.assertEqual(listResult, "Config.do_list not implemented for the base class")

if __name__ == "__main__":
    unittest.main()