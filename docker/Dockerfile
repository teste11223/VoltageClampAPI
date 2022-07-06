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

# Repository URL
# Can be customised at build time using --build-arg variable=value
# Note: we define this _after_ all the apt-get installs, so that we don't need
# to reinstall if the arg changes.
ARG repo=https://github.com/CardiacModelling/VoltageClampAPI.git

# Create a central directory to store everything
RUN mkdir /opt/vclamp
WORKDIR /opt/vclamp

# Download and install the app
RUN git clone $repo repo
RUN pip install -r repo/app/requirements.txt

# Install and configure gunicorn
RUN pip install gunicorn
RUN ln -s repo/docker/gunicorn.conf.py

