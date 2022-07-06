#
# This file will be read by gunicorn when it is run.
#
# It does not get placed in any central location: it only affects gunicorn when
# run from a working directory containing this file.
#
# See: https://docs.gunicorn.org/en/stable/configure.html
#
# Listen here
bind = "127.0.0.1:5000"

# Number of worker processes
workers = 1

# Number of threads per process
threads = 2

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"

