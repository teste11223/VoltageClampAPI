#!/bin/bash
#
# Start nginx and unicorn.
# As per docker standard, we run gunicorn in the foreground! (the docker will
# exit when the process is done).
#
nginx
su vclamp -c "gunicorn app:app"
