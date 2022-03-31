FROM python:3.11.0a6-alpine3.15
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install psycopg2
RUN apk update && apk add libpq-dev
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt
COPY . /usr/src/app
ARG var_user
ARG var_pass
ARG var_host
ARG var_port
ARG var_name
ARG var_table_name

ENV env_user=$var_user
ENV env_pass=$var_pass
ENV env_host=$var_host
ENV env_port=$var_port
ENV env_name=$var_name
ENV env_table_name=$var_table_name
CMD python3 /usr/src/app/scraper.py $env_user $env_pass $env_host $env_port $env_name $env_table_name