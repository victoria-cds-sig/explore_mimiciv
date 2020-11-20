import google.auth


def get_gcreds():
   return google.auth.default(
          scopes=["https://www.googleapis.com/auth/bigquery"]
    )


