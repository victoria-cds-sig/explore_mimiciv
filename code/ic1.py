import bqutils.auth as auth
import bqutils.ibis as iq


def main():
    client = iq.get_client(*auth.get_gcreds())
    db = client.database("bigquery-public-data.stackoverflow")
    expression = db.table("posts_questions").projection(["creation_date", "answer_count"]).limit(5)

    df = expression.execute()
    for _, r in df.iterrows():
        print(r)


if __name__ == "__main__":
    main()
