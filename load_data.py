import snowflake.connector
import os

def main():
    conn = snowflake.connector.connect(
        connection_name="default"
    )
    cur = conn.cursor()

    try:
        cur.execute("USE DATABASE ROAD_ACCIDENTS_DB")
        cur.execute("USE SCHEMA ANALYTICS")
        cur.execute("USE WAREHOUSE COMPUTE_WH")

        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "road_accidents.csv")
        csv_path_escaped = csv_path.replace("\\", "/")

        print("Uploading CSV to stage...")
        cur.execute(f"PUT 'file://{csv_path_escaped}' @ACCIDENT_STAGE AUTO_COMPRESS=TRUE OVERWRITE=TRUE")
        for row in cur:
            print(row)

        print("\nLoading into ACCIDENTS table...")
        cur.execute("TRUNCATE TABLE IF EXISTS ACCIDENTS")
        cur.execute("""
            COPY INTO ACCIDENTS
            FROM @ACCIDENT_STAGE
            FILE_FORMAT = CSV_FORMAT
            ON_ERROR = 'CONTINUE'
        """)
        for row in cur:
            print(row)

        cur.execute("SELECT COUNT(*) FROM ACCIDENTS")
        count = cur.fetchone()[0]
        print(f"\nTotal rows loaded: {count}")

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
