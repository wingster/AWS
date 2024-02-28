# Task 6: Creating an SNS topic and setting up subscriptions
#
# In this task, you create an SNS topic and set up subscriptions. Amazon SNS coordinates and manages delivering or sending messages to subscriber endpoints or clients.
# Step 6.1: Creating a topic in the notification service
# In the AWS Management Console, search for SNS and choose Simple Notification Service.
# On the Create topic card, enter POC-Topic and choose Next step.
# In the Details section, keep the Standard topic type selected and choose Create topic.
# On the POC-Topic page, copy the ARN of the topic that you just created and save it for your reference.
# You will need the ARN for the SNS topic later in this exercise.

# Step 6.2: Subscribing to email notifications
# On the Subscriptions tab, choose Create subscription.
# For Topic ARN, make sure that the box contains the ARN for POC-Topic.
# To receive notifications, for Protocol, choose Email.
# For Endpoint, enter your email address.
# Choose Create subscription.
# The confirmation message is sent to the email address that you specified.

# After you receive the confirmation email message, confirm the subscription. If you don’t receive an email message within a few minutes, check the spam folder.

import boto3
import sys

notification_email = "wing.s.chau@gmail.com"  # replace with your email address


sns_definitions = {
    "POC1-Topic" : {
        "Attributes" : {
            #"Policy" : json.dump({/* IAM policy */}),
            #'KmsMasterKeyId': 'abcd1234' 
            #"FifoTopic" : "false",
            #"ContentBasedDeduplication" : "false"
        },
        "Subscriptions" : {
            "email-1" : {
                "Protocol" : "email",
                "Endpoint" : notification_email,
            },
            # Support secondary email address with this dictionary structure
            #"email2" : {
            #    "Protocol" : "email",
            #    "Endpoint" : "secondary_address@email.com"  # 
            #}
        }
    }
}


def create_sns():
    sns_client = boto3.client('sns')

    # iterate through the sns_definitions, create the topic, set the attributes, subscribe to the subscription lists
    for topic_name, topic_definition in sns_definitions.items():
        print(f"Creating topic {topic_name}...")
        
        topic = sns_client.create_topic(Name=topic_name,
                                        Attributes=topic_definition["Attributes"])
        print(f"Topic created: ARN: {topic['TopicArn']}")

        for key, subscription in topic_definition["Subscriptions"].items():
            print(key, subscription)
            print(f"Creating subscription {key} for {subscription['Protocol']}:{subscription['Endpoint']}")
            sns_client.subscribe(
                TopicArn=topic['TopicArn'],
                Protocol=subscription['Protocol'],
                Endpoint=subscription["Endpoint"]
            )
            print(f"Subscription created for {key}:{subscription['Endpoint']}")



def delete_sns():
    sns_client = boto3.client('sns')

    # List all topics and filter by topic names defined in sns_defintions
    sns_topics = sns_client.list_topics()['Topics']
    topics = [t for t in sns_topics if t['TopicArn'].split(':')[-1] in sns_definitions.keys()]
    
    # iterate through the topics, identify the subscriptions, remove the subscriptions then delete the topic
    for topic in topics:
        print(f"Deleting topic {topic['TopicArn']}...")
        subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=topic['TopicArn'])['Subscriptions']
        for subscription in subscriptions:
            subscriptionArn = subscription['SubscriptionArn']
            subscriptionProtocol = subscription['Protocol']
            subscriptionEndpoint = subscription['Endpoint']
            # if the subscription arn is "PendingConfirmation", skip as unsubscribe would fail on pending confirmation
            if subscriptionArn.split(':')[-1] == "PendingConfirmation":
                print(f"Skipping subscription {subscriptionProtocol}:{subscriptionEndpoint} {subscription['SubscriptionArn']} as it is pending confirmation")
                continue
            else:
                print(f"unsubscribe {subscriptionProtocol}:{subscriptionEndpoint} {subscription['SubscriptionArn']}")
                sns_client.unsubscribe(SubscriptionArn=subscription['SubscriptionArn'])

        sns_client.delete_topic(TopicArn=topic['TopicArn'])
        print(f"Topic deleted: {topic['TopicArn']}") 


def list_sns():
    sns_client = boto3.client('sns')

    # List topics and filter by name
    sns_topics = sns_client.list_topics()['Topics']
    topics = [t for t in sns_topics if t['TopicArn'].split(':')[-1] in sns_definitions.keys()]
    # iterate through the topics, identify the subscriptions, remove the subscriptions then delete the topic
    for topic in topics:
        print(f"Topic: {topic['TopicArn']}:")
        subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=topic['TopicArn'])['Subscriptions']
        for subscription in subscriptions:
            # print subscription information
            print(f"\tSubscription: {subscription['Protocol']}:{subscription['Endpoint']}, ARN:{subscription['SubscriptionArn']} ")
            # check to see if the SubscriptionArn is "PendingConfirmation", only invoke get_subscription_attributes if the value isn't "PendingConfirmation"
            # There isn't anything new in the subscription attributes, so disable for now
            # if subscription['SubscriptionArn'].split(':')[-1] != "PendingConfirmation":
                # print subscription attributes
                # print(f"Subscription Attributes: {sns_client.get_subscription_attributes(SubscriptionArn=subscription['SubscriptionArn'])}")

# get SNS topic arn by topic name
def get_sns_topic_arn(topic_name):
    sns_client = boto3.client('sns')
    sns_topics = sns_client.list_topics()['Topics']
    topics = [t for t in sns_topics if t['TopicArn'].split(':')[-1] == topic_name]
    if len(topics) == 0:
        print(f"Topic {topic_name} not found")
        return None
    else:
        return topics[0]['TopicArn']




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
            create_sns()
        elif action == "delete":
            delete_sns()
        elif action == "list":
            list_sns()


if __name__ == "__main__":
    main(sys.argv)

