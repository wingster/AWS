# Unit Test folder for utils/Config

PYTHONPATH=/Users/wing/work/AWS/SolutionArchitect/utils

Currently running unit test triggered this deprecationWarning

/Users/wing/work/AWS/.conda/lib/python3.12/site-packages/botocore/auth.py:419: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  datetime_now = datetime.datetime.utcnow()

This is a known issue and it's being tracked under
https://github.com/boto/botocore/pull/3145