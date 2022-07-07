# Docker image

This files in this directory let you create a Docker "image", from which you can create Docker "containers" that run the artefact app as a web server.

If you're new to docker, the stuff in [docker-help.md](./docker-help.md) might be useful.

The stuff that happens inside the container is explained in [design.md](./design.md).

## Development: Building an image and testing locally

This explains how to build and test the docker image.
Note that you don't need docker to test the app: see the `app` directory for instructions on how to do that.

From the directory that `Dockerfile` is in:
```
docker build -t artefact/api .
```
This builds an image called `artefact/api` using the Dockerfile at `.`.

Now run, and map host port 5000 to the container's port 80:
```
docker run -it --rm -p 5000:80 artefact/api
```

Then, in another terminal, on the host machine:
```
cd ../app
python client.py
```
If it works, this should print out a whole bunch of numbers.

## Deployment: Building an image and connecting to Apache

TODO


