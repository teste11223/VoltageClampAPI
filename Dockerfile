FROM python:3.10-slim

# Install required packages
RUN apt-get update
RUN apt-get install build-essential -y
RUN apt-get install libsundials-dev -y
RUN apt-get install nginx -y

# Just for ease of development
COPY docker/bashrc root/.bashrc

# Configure nginx
RUN rm /etc/nginx/sites-enabled/*
COPY docker/nginx-site.conf /etc/nginx/sites-enabled/gunicorn-site.conf

# Create a user to run gunicorn, create logdirs, and install
RUN useradd -m -s /bin/bash vclamp
RUN mkdir /var/log/gunicorn
RUN chown vclamp /var/log/gunicorn
RUN pip install gunicorn

# Copy and install the app
ARG vclamp=/opt/vclamp
COPY app $vclamp
WORKDIR $vclamp
RUN pip install -r requirements.txt

# Copy in gunicorn configuration file
COPY docker/gunicorn.conf.py gunicorn.conf.py

# Initialise the simulations (as root)
RUN python simulations.py

# Tidy up
#RUN apt-get remove build-essential -y
#RUN apt-get remove libsundials-dev -y
#RUN apt-get autoremove -y

# Set the entry point
COPY docker/start.sh start.sh
CMD ./start.sh
