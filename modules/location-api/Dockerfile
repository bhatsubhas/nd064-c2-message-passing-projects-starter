FROM python:3.8-buster

WORKDIR . 

RUN apt-get install gcc libc-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

COPY . .
CMD ["flask", "run", "--host", "0.0.0.0"]
