FROM python:3.8-slim-buster
WORKDIR /usr/app
COPY requirements.txt .
COPY /cleaner ./cleaner
COPY /main.py .

RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "main.py" ]