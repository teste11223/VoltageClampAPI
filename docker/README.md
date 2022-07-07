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

Build the image, and delete all stopped, dangling etc. things:

```
docker build -t artefact/api .
```

TODO: SOMEHOW RUN THIS, BUT ROUTE STDOUT AND STDERR TO /VAR/LOG/VCLAMP, AND DAEMONIZE
```
docker run -it --rm -p 5000:80 artefact/api
```

TODO: SOMEHOW CONNECT OTHER SERVER TO THIS

## Tidying up

Especially after development, you may have a lot of unwanted images and containers lying around.

To do this carefully, you can delete unwanted containers by first getting a list of container names with `docker ps -a`, and then using `docker rm name1 name2 name3` etc.
Note that (on linux at least) you can autocomplete so you don't need to type the full names.

You can delete unneeded images with
```
docker image prune
```
This works especially well if you make sure you've stopped & removed any unneeded containers first.

If you don't need to be safe / careful, you can delete *lots* of stuff, with:
```
docker system prune -f
```
