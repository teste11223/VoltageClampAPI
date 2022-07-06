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

## Why'd we have to go and make things so complicated

The simplest set-up would be to have the `app` run on a dedicated machine, listening to port 80, and without any other servers.
But if you want to share with other things, e.g. have websites running over port 80 too, it makes sense to have a second server.
So that's where apache (in the above example) comes in.

It should be possible for apache to talk directly to the `app` inside the container, via WSGI (and using e.g. `mod-wsgi`).
However, to be a bit more future-proof we are adding NGINX in between, so that we can also e.g. serve static files, should this become necessary.
It also means we can use any other NGINX features (e.g. for access control) without implementing them in our app, or having to mess with the main Apache server.

Finally having everything (except the big apache server) in a container means we can use system packages to set everything up.
This is the easiest (only?) way to go, because server software has historically been designed under the assumption of a dedicated server.

