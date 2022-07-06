FROM python:3.10-slim

# Install required packages
RUN apt-get update
RUN apt-get install git -y
RUN apt-get install build-essential -y
RUN apt-get install libsundials-dev
RUN apt-get install nginx -y

# Download and install the app
WORKDIR /opt
RUN git clone https://github.com/CardiacModelling/VoltageClampAPI.git
RUN pip install -r /opt/VoltageClampAPI/app/requirements.txt




RUN mkdir /opt/django
WORKDIR /opt/django

