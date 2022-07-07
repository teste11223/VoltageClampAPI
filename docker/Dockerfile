FROM python:3.10-slim

# Install most required packages
RUN apt-get update
RUN apt-get install build-essential -y
RUN apt-get install libsundials-dev -y
RUN apt-get install nginx -y

# Install and configure git (make merging the default strategy)
RUN apt-get install git -y
RUN git config --global pull.rebase false

# Just for development
COPY bashrc root/.bashrc

# Create a central directory to store everything
ARG root=/opt/vclamp
RUN mkdir $root
WORKDIR $root

# Download and install the app
ARG repo=https://github.com/CardiacModelling/VoltageClampAPI.git
RUN git clone $repo repo
RUN pip install -r repo/app/requirements.txt

# Install gunicorn, link to config file in working dir, create log dirs
RUN pip install gunicorn
RUN ln -s repo/docker/gunicorn.conf.py
RUN mkdir /var/log/gunicorn
RUN chown www-data /var/log/gunicorn

# Configure nginx
RUN rm /etc/nginx/sites-enabled/*
RUN ln -s $root/repo/docker/nginx-site.conf /etc/nginx/sites-enabled/gunicorn-site.conf
