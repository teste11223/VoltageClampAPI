# A python web api for the artefacts app

This repository contains

- `app` A Python app that uses `flask` to present a web API for running simulations.
- `docker` A bunch of files to let you run the app in a web server in in a Docker container.
- `html` A very primitive HTML client used to test the API during development.

If you want to **deploy** the app, look at [docker/README.md](./docker/README.md).

If you want to **modify** the app, or just play around with it locally, look at [app/README.md](./app/README.md).

If you want to **build a client**, look at the API docs (link below) or the examples in [html](./html) and [client.py](./app/client.py).

The API itself is documented in [API.md](./API.md).
