import praw
import boto3
import json
import logging
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.helpers import bulk
from requests_aws4auth import AWS4Auth

logger = logging.getLogger('reddit_fetch_log')
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    # Set Reddit credentials
    reddit = praw.Reddit(client_id="TM-o8OhRZBUKP42CeyhILQ",
                         client_secret="3MvilBApHioYD5DJ8Q_s0nYRpzaUfw",
                         user_agent="nurlan_reddit_script/1.0")

    # Set the Reddit post ID
    # post_id = "6byls7"
    # query = "I'm try"

    post_id = json.loads(event['body'])["post_id"]
    query = json.loads(event['body'])["query"]

    logger.info(f"post_id: {post_id}, query: {query}")
    # Fetch comments from Reddit post
    submission = reddit.submission(post_id)

    submission.comments.replace_more(limit=None)

    credentials = {
        "access_key": "AKIA3UCKDXR5U54W65PC",
        "secret_key": "YjkG4Y2yTixYfLTSD6lCu0iHW3uZvjIg9exLlPnv",
    }
    region = "us-east-1"
    service = "es"
    host = "search-testcloud-ngwddno7nqnjlqlvwyatfygfa4.us-east-1.es.amazonaws.com"
    awsauth = AWS4Auth(credentials["access_key"],
                       credentials["secret_key"], region, service)

    client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    logger.info(f"comments: {submission.comments.list()}")
    bulk_data = []
    for i, comment in enumerate(submission.comments.list()):
        if comment.body:
            bulk_data.append(
                {
                    "_index": post_id,
                    "_id": i,
                    "_source": {
                        "text": comment.body
                    }
                }
            )

    bulk(client, bulk_data)

    logger.info(f"Success!")

    import boto3

    # Create an AWS session
    session = boto3.Session(
        aws_access_key_id=credentials["access_key"],
        aws_secret_access_key=credentials["secret_key"],
        region_name=region
    )

    # Create an AWS Lambda client using the session
    lambda_client = session.client('lambda')

    # Invoke the Lambda function
    response = lambda_client.invoke(
        FunctionName='redditsearcher-RedditCommentSearcherFunction-A2fCPbynDhoK',  # name of the Lambda function
        InvocationType='RequestResponse',  # synchronous execution
        Payload=json.dumps({"body": event['body']})  # JSON input for the function
    )
    logger.info(response)
    # Get the function's output
    output = json.loads(response['Payload'].read())
    logger.info(output)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True
        },
        "body": output['body']
    }

    # resp = client.search(
    #     index=post_id,
    #     body={
    #         "query": {
    #             "query_string": {
    #                 "default_field": "text", 
    #                 "query": f"*{query}*"
    #             }
    #         }
    #     }
    # )
    # for i, hit in enumerate(resp["hits"]["hits"]):
    #     print(i, hit["_source"]["text"])
