FROM apache/airflow

COPY --chown=airflow:root --chmod=0700 entrypoint.sh /usr/bin/entrypoint.sh
COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt

ENTRYPOINT ["/usr/bin/entrypoint.sh"]