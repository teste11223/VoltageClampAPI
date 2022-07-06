# What I did to get docker etc. running

I'm using Fedora. It's probably similar on Ubuntu.

## Install docker, add yourself to the docker group

https://docs.docker.com/get-started/overview/
https://docs.docker.com/engine/install/fedora/

As root:
```
dnf install docker
usermod -aG docker $USER
systemctl start docker
```
Reboot.
As user:
```
docker run -i -t ubuntu /bin/bash
```

See running containers:
```
docker ps
```
and all containers:
```
docker ps -a
```
shows
```
CONTAINER ID   IMAGE     COMMAND       CREATED         STATUS                     PORTS     NAMES
c3ece3e4d40a   ubuntu    "/bin/bash"   6 minutes ago   Exited (0) 6 minutes ago             blissful_turing
```

Remove the container we just created:
```
docker rm blissful_turing
```

## Things in docker

https://en.wikipedia.org/wiki/Docker_(software)#Components

- `dockerd`. The daemon that runs all docker containers
- `docker`. The command line program to talk to and manage `dockerd`

Annoyingly, on Fedora et aleast we start `dockerd` with `systemctl start docker`.

- **Container**. It's technically not a vm.
- **Image**. A template for a container.

Above, we used the image `ubuntu`, which seems to come pre-installed:
```
docker images
```
shows
```
REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
ubuntu       latest    27941809078c   4 weeks ago   77.8MB
```

## First thing to do: write a docker file

A `Dockerfile` is a "recipe for a Docker image".
The syntax is given [here](https://docs.docker.com/engine/reference/builder).
