import google.auth


def get_gcreds(scopes = None):
    if scopes == None:
        scopes = ["https://www.googleapis.com/auth/bigquery"]
    return google.auth.default(
          scopes = scopes )


