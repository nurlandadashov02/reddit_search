import praw
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.helpers import bulk
from requests_aws4auth import AWS4Auth


def lambda_handler(event, context):
    # Set Reddit credentials
    reddit = praw.Reddit(client_id="TM-o8OhRZBUKP42CeyhILQ",
                         client_secret="3MvilBApHioYD5DJ8Q_s0nYRpzaUfw",
                         user_agent="nurlan_reddit_script/1.0")

    # Set the Reddit post ID
    # post_id = "6byls7"
    # query = "I'm try"

    post_id = event["post_id"]
    query = event["query"]

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
