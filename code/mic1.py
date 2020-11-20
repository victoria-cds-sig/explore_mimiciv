import bqutils.auth as auth
import bqutils.ibis as iq


def main():
    client = iq.get_client(*auth.get_gcreds())
    db = client.database("physionet-data.mimic_core")
    expression = db.table("patients").limit(5)

    df = expression.execute()
    for _, r in df.iterrows():
        print(r)


if __name__ == "__main__":
    main()
