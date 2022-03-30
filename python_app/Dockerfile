FROM python:3.11.0a6-alpine3.15
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt
COPY . /usr/src/app
CMD ["python3", "/usr/src/app/scraper.py"]