import ibis

def get_client(c, p, dataset_id="development"):
   return ibis.bigquery.connect(
              project_id=p,
              dataset_id=dataset_id,
              credentials=c)

