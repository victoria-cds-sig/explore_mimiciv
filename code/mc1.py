import bqutils.auth as auth
import bqutils.bq as bq

query_string3 = """SELECT * FROM `physionet-data.mimic_core.patients` LIMIT 5"""

def main():
    client = bq.get_client(*auth.get_gcreds())
    query_job3 = client.query(query_string3)
    for r in query_job3.result():
        print(r)


if __name__ == "__main__":
    main()
