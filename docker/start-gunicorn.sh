#!/usr/bin/env bash
#
# Start gunicorn, to be called by start.sh
#
cd $VCLAMP
gunicorn --chdir app app:app
