import json
import logging
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

logger = logging.getLogger('reddit_fetch_log')
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)
    # Set the Reddit post ID
    post_id = json.loads(event['body'])["post_id"]
    query = json.loads(event['body'])["query"]

    logger.info(f"post_id: {post_id}, query: {query}")

    credentials = {
        "access_key": "AKIA3UCKDXR5U54W65PC",
        "secret_key": "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",
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

    resp = client.search(
        index=post_id,
        body={
            "query": {
                "query_string": {
                    "default_field": "text", 
                    "query": f"*{query}*"
                }
            }
        }
    )

    logger.info(resp)

    filtered_comments = []
    for hit in resp["hits"]["hits"]:
        filtered_comments.append(hit["_source"]["text"])

    logger.info(filtered_comments)

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True
        },
        "body": json.dumps({
            "comments": filtered_comments
        })
    }
