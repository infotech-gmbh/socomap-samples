FROM python:3.7

RUN pip install requests
RUN mkdir /app
WORKDIR /app
ADD socomap_receiver.py /app

ENTRYPOINT ["python", "/app/socomap_receiver.py"]