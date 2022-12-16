from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def lambda_handler(event, context):
    # Set the Reddit post ID
    post_id = event["post_id"]
    query = event["query"]

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

    filtered_comments = []
    for hit in resp["hits"]["hits"]:
        filtered_comments.append(hit["_source"]["text"])

    return filtered_comments
