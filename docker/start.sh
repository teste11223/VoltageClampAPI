#!/usr/bin/env bash
#
# Start nginx and unicorn.
#
nginx
runuser -l vclamp -s /bin/bash -c "start-gunicorn.sh"
