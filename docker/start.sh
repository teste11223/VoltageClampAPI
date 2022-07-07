#!/usr/bin/env bash
#
# Start nginx and unicorn.
# To be called from the working directory.
#
nginx
gunicorn --chdir repo/app app:app
