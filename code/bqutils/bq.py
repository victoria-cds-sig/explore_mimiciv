from google.cloud import bigquery


def get_client(c,p):
    return bigquery.Client(project=p, credentials=c)


