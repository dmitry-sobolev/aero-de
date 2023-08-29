#!/usr/bin/env bash

set -x

airflow db check-migrations -t 1
NEED_INIT=$?

if [[ $NEED_INIT != 0 ]]; then
  airflow db init

  airflow users create \
    --username airflow \
    --password airflow \
    --firstname FIRST_NAME \
    --lastname LAST_NAME \
    --role Admin \
    --email airflow@example.org

  # Соединение добавил исключительно в тестовых целях;
  # в проде нельзя мешать БД с метаданными Airflow и с данными
fi

CONN_IS_EXISTS=`grep -i pg_test`

if [[ -z $CONN_IS_EXISTS ]]; then
  airflow connections add --conn-uri "postgresql://postgres:postgres@postgres/airflow" pg_test
fi

exec airflow "$@"