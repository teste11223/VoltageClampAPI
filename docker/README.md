# Docker image

If you already know how to use docker, use the steps below to set up a container running the web app.
If not, see [CONTRIBUTING.md](./CONTRIBUTING.md).

## The docker container contains code to run a server:

The artefacts `app` runs as WSGI supporting server (inside a docker container).
It listens for requests from the local machine.
The same docker container contains an NGINX server.
This listens on a port connected to the docker container's host, and passes requests on to the app (via WSGI).

## You can map the container port onto a host port:

TODO

## You can pass external requests on to this port

For example, if you have an Apache server running, it can pass off requests in a certain location to the nginx-in-the-container:

```
<Location /artefact-webapp>
   ProxyPass http://localhost:4321
   ProxyPassReverse http://localhost:4321
</Location>
```
