FROM python:3.10-slim

# Install required packages
RUN apt-get update
RUN apt-get install build-essential -y
RUN apt-get install libsundials-dev -y
RUN apt-get install nginx -y

# Just for ease of development
COPY docker/bashrc root/.bashrc

# Create a central directory to store everything
ENV VCLAMP=/opt/vclamp
RUN mkdir $VCLAMP
WORKDIR $VCLAMP

# Copy and install the app
COPY app $VCLAMP/app
RUN pip install -r $VCLAMP/app/requirements.txt

# Install gunicorn, link to config file in working dir, create log dirs
RUN pip install gunicorn
COPY docker/gunicorn.conf.py $VCLAMP/gunicorn.conf.py
RUN mkdir /var/log/gunicorn
RUN chown www-data /var/log/gunicorn

# Configure nginx
RUN rm /etc/nginx/sites-enabled/*
COPY docker/nginx-site.conf /etc/nginx/sites-enabled/gunicorn-site.conf

# Initialise the simulations
RUN python app/simulations.py

# Set the entry point
COPY docker/start.sh start.sh
ENTRYPOINT start.sh

