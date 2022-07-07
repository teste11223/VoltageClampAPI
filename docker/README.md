# Docker image

This files in this directory let you create a Docker "image", from which you can create Docker "containers" that run the artefact app as a web server.

If you're new to docker, the stuff in [docker-help.md](./docker-help.md) might be useful.

The stuff that happens inside the container is explained in [design.md](./design.md).

## Development: Building an image and testing locally

This explains how to build and test the docker image.
Note that you don't need docker to test the app: see the `app` directory for instructions on how to do that.

From the directory that `Dockerfile` is in:
```
sudo docker build -t artefact/api . && sudo docker image prune --filter=label=stage=artifact-builder -f
```
This builds an image called `artefact/api` using the Dockerfile at `.`.

Now run, and map host port 4242 to the container's port 80:
```
sudo docker run -it --rm -p 4242:80 artefact/api
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
sudo docker build -t artefact/api . && sudo docker image prune --filter=label=stage=artifact-builder -f
```

To be able to access logs set up a docker volume
```
sudo docker volume create artefact_logs
```

You can see where the data will be stored (the Mountpoint) by doing:
```
sudo docker volume inspect artefact_logs
```

To start the component (in detached mode):
```
sudo docker run -d --restart always -v artefact_logs:/var/log/gunicorn -p 4242:80 artefact/api
```

The API is now avaliable on http://localhost:4242 on the host machine you are running the docker component on. If this is a server, you might want to proxy this through the server's webserver. For example on cardiac.nottingham we have proied it through as `https://cardiac.nottingham.ac.uk/artefact-webapp/`

This is achieved with the following config:
```
<Location /artefact-webapp>
   ProxyPass http://localhost:4242
   ProxyPassReverse http://localhost:4242
</Location>