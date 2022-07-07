#!/bin/bash
#
# Start nginx and unicorn.
# As per docker standard, we run gunicorn in the foreground! (the docker will
# exit when the process is done).
#
nginx
touch /var/log/gunicorn/gunicorn.log
chown vclamp:vclamp /var/log/gunicorn/gunicorn.log
su vclamp -c "gunicorn --log-level debug --error-logfile /var/log/gunicorn/gunicorn.log app:app"
