#
# First, create an image to build simulations
#
FROM python:3.10-slim AS compile_image

# Install  packages required for build
RUN apt-get update -y
RUN apt-get install build-essential -y --no-install-recommends
RUN apt-get install libsundials-dev -y --no-install-recommends
RUN pip install configparser numpy; pip install myokit --no-deps

# Copy and install the app
ARG vclamp=/opt/vclamp
COPY app $vclamp

# Initialise the simulations (as root)
RUN python $vclamp/simulations.py

#
# Now start a new image with just the runtime stuff
#
FROM python:3.10-slim AS runtime_image

# Install nginx and flask
RUN apt-get update -y; apt-get install nginx -y --no-install-recommends
RUN pip install flask-cors flask-limiter flask-restful gunicorn configparser numpy; pip install myokit --no-deps

# Configure nginx
RUN rm /etc/nginx/sites-enabled/*
COPY docker/nginx-site.conf /etc/nginx/sites-enabled/gunicorn-site.conf

# Create a user to run gunicorn, create logdirs, and install
RUN useradd -m -s /bin/bash vclamp
RUN mkdir /var/log/gunicorn
RUN chown vclamp /var/log/gunicorn

# Copy and install the app
ARG vclamp=/opt/vclamp
COPY app $vclamp

# Copy in gunicorn configuration file
COPY docker/gunicorn.conf.py gunicorn.conf.py

# Set the entry point
COPY docker/start.sh start.sh
CMD ./start.sh
