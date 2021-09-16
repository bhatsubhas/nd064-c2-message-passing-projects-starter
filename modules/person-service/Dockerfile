FROM python:3.8-buster

RUN mkdir /opt/app

WORKDIR /opt/app

#RUN apk add --no-cache gcc musl-dev linux-headers geos libc-dev postgresql-dev
RUN apt-get install gcc libc-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

COPY . .
CMD ["python", "service.py"]
