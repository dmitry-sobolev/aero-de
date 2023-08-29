import datetime
import csv
import json
from pathlib import Path

import requests
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator


API_URL="https://random-data-api.com/api/cannabis/random_cannabis?size=10"
CONN_ID = "pg_test"
FILE_PATH_TPL = "/data/aero_de_test/{{ ts }}.csv"


def extract_fn(file_path, ts, **kwargs):
    file_path = Path(file_path)
    dir_path = file_path.parent

    if dir_path.exists() and not dir_path.is_dir():
        raise NotADirectoryError(dir_path)

    dir_path.mkdir(exist_ok=True, parents=True)

    res = requests.get(API_URL)
    res.raise_for_status()

    with open(file_path, mode="w") as fp:
        writer = csv.writer(fp)
        writer.writerows((ts, json.dumps(row)) for row in res.json())


with DAG(
    dag_id="aero_de_test",
    start_date=datetime.datetime(2023, 8, 29),
    schedule="* 0,12 * * *",
    catchup=False,
    default_args={
        "depends_on_past": False
    }
):


    create_table = PostgresOperator(
        task_id="create_table",
        postgres_conn_id=CONN_ID,
        sql="""
CREATE TABLE IF NOT EXISTS aero_de_test (
    id BIGSERIAL NOT NULL PRIMARY KEY,
    ts TIMESTAMP WITH TIME ZONE NOT NULL,
    data JSON NOT NULL
)
        """
    )

    extract = PythonOperator(
        task_id="extract_from_api",
        python_callable=extract_fn,
        op_kwargs={
            "file_path": FILE_PATH_TPL
        }
    )

    load = PostgresOperator(
        task_id="load",
        postgres_conn_id=CONN_ID,
        sql=f"""
COPY aero_de_test (ts, data)
FROM '{FILE_PATH_TPL}'
WITH DELIMITER ','
CSV QUOTE '"' ESCAPE '"'
;
"""
    )

    create_table >> extract >> load

