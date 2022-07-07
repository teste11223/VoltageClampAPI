# What I did to get docker etc. running

I'm using Fedora. It's probably similar on Ubuntu.

This is useful: https://www.patricksoftwareblog.com/how-to-configure-nginx-for-a-flask-web-application/

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
docker run -it ubuntu bash
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
c3ece3e4d40a   ubuntu    "bash"        6 minutes ago   Exited (0) 6 minutes ago             blissful_turing
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

## Starting a container

To create a container from an image, and run a command on it, use e.g.
```
docker run -it ubuntu bash
```
this `run`s the command `bash` on a container created from the image `ubuntu`.
Because we want to connect to its screen and input, we use the switch `-it`.

To connect to a running container, we use the similar `exec` command:
```
docker exec -it some_word_combo bash
```
where `some_word_combo` is a name returned by `docker ps`.

## First thing to do: write a docker file

A `Dockerfile` is a "recipe for a Docker image".
The syntax is given [here](https://docs.docker.com/engine/reference/builder).

The main bits are:
- `FROM`, which specifies another image to base our image on (this will be downloaded).
- `RUN`, which runs stuff.

First attempt:
```
FROM python:3.10-slim

# Install required packages
RUN apt-get update
RUN apt-get install git -y
RUN apt-get install build-essential -y
RUN apt-get install libsundials-dev -y
RUN apt-get install nginx -y

# Download and install the app
WORKDIR /opt
RUN git clone https://github.com/CardiacModelling/VoltageClampAPI.git
RUN pip install --upgrade
RUN pip install -r /opt/VoltageClampAPI/app/requirements.txt
```

## Create an image

From the directory the Dockerfile is in, run
```
docker build -t michael/artefact-api .
```
here `.` refers to the local directory & Dockerfile, while `-t michael/artefact-api` is just a "tag" to give the resulting image a nice name.

You will see quite a lot of output, which may include this message:
```
debconf: delaying package configuration, since apt-utils is not installed
```
This just means that `apt` can't do its interactive configuration thing, and is [safe to ignore](https://stackoverflow.com/a/51023393/423420).

You can also ignore this message (yes using pip as root is _usually_ a bad idea).
```
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv
```
And this one:
```
WARNING: You are using pip version 22.0.4; however, version 22.1.2 is available.
You should consider upgrading via the '/usr/local/bin/python -m pip install --upgrade pip' command.
```
We will have to make do with the pip version available from the package manager.
(Ubuntu has even modified its system pip to stop you upgrading it.)

Look what you've done, with `docker images`:
```
REPOSITORY             TAG         IMAGE ID       CREATED         SIZE
michael/artefact-api   latest      e254046b2d71   5 minutes ago   1.78GB
python                 3.10-slim   24aa51b1b3e9   12 days ago     125MB
ubuntu                 latest      27941809078c   4 weeks ago     77.8MB
```
Annoyingly, the "tag" we set is called a "repository" here, while `3.10-slim` (which we used in our `FROM`) is a real tag.

## Create a container, to mess around with

```
docker run -it michael/artefact-api bash
```

You can now have a look around.
Interestingly, you can't use `systemctl` to check for running processes, because the whole init/systemctl thing hasn't been isntalled.
There's also no `htop` or `vim` by default.
You can install them if you like: it won't be carried over in the image.

### Trying out the app

In your prompt, just start `app.py` (as a debug server).
Now open a second console, and connect a second prompt to the running container:
```
docker exec -it <container-id> bash
```
where `<container-id>` is some name returned by `docker ps`.
In this one, you should be able to
```
pip install requests
./client.py
```

### Killing a flake app

If, for whatever reason you want to kill the app but can't use `Ctrl+C`, you can use `top`, then `k`, then the pid, then `9` (not 15!).

## Using variables

We can also add [variables](https://docs.docker.com/engine/reference/builder/#from) to our Dockerfile, using `ARG`:
```
ARG repo=https://github.com/CardiacModelling/VoltageClampAPI.git
RUN git clone $repo
```
The value of an `ARG` can also be change at build time with `--build-arg variable=value`.

## Install and configure gunicorn

Gunicorn can be installed via `apt-get`, but this version seems to make some extra assumptions.
Easier to just pip install it:
```
pip install gunicorn
```

[Gunicorn doesn't have a central configuration file](https://docs.gunicorn.org/en/stable/configure.html) in `/etc` or anywhere like that.
Instead, we can add configuration info to environment variables, the command line, or a local file called `gunicorn.conf.py `.
See [here for a list](https://docs.gunicorn.org/en/stable/settings.html).

For now, we'll create a file that looks like this:
```
bind = "127.0.0.1:5000"
workers = 2
```
and update the `Dockerfile` to use it:

```
# Repository URL
ARG repo=https://github.com/CardiacModelling/VoltageClampAPI.git

# Create a central directory to store everything
RUN mkdir /opt/vclamp
WORKDIR /opt/vclamp

# Download and install the app
RUN git clone $repo repo
RUN pip install -r repo/app/requirements.txt

# Create gunicorn.conf.py in working directory
RUN pip install gunicorn
RUN ln -s repo/docker/gunicorn.conf.py
```
This creates a dir `/opt/vclamp` that contains this repo in `/opt/vclamp/repo`.
It then creates a symlink `/opt/vclamp/gunicorn.conf.py` that points to the file in the cloned repo.

We can now start a webserver with `gunicorn`:
```
python -m gunicorn --chdir repo/app app:app
```
This tells python to load the `gunicorn.__main__` module (change `python` to any other executable if you want to use virtualenvs).
Gunicorn then changes its working directory to `repo/app`, loads the `app` module, and runs the `app` object in that module.

So if we'd had a dir in the repo called `myproject` with a `flaskthing.py` that created an object `x`, this would be `python -m gunicorn --chdir repo/myoproject flaskthing:x`.

As before, we can connect a second terminal to the container and test with `client.py`.

If we like, we can even connect a third one to run `top`.
This shows 2 `gunicorn` processes, using almost no CPU until we run a client.

## Configuring nginx

We installed nginx in the container with `apt-get`.
As said before, we don't have `systemctl`, so how do we start it or see its current states?

First thing to note: no pid file:
```
ls /run
total 4
drwxrwxrwt 2 root root 4096 Jun 22 00:00 lock
-rw-rw-r-- 1 root utmp    0 Jun 22 00:00 utmp
```

Now start it manually:
```
nginx
ls /run
total 8
drwxrwxrwt 2 root root 4096 Jun 22 00:00 lock
-rw-r--r-- 1 root root    4 Jul  6 23:23 nginx.pid
-rw-rw-r-- 1 root utmp    0 Jun 22 00:00 utmp
```

We can stop it again with `nginx -s stop`.
See `nginx -h` for more options.

We can have a look at the nginx configuation in `/etc/nginx/nginx.conf`.

To add a site, we add it to `/etc/nginx/sites/enabled`.

I followed [this](https://flask.palletsprojects.com/en/2.1.x/deploying/nginx/) and [this](https://flask.palletsprojects.com/en/2.1.x/deploying/proxy_fix/).

We can check if the overal and site config files are OK with:
```
nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

See `nginx-site.conf`.

Now start everything up, run gunicorn on port 5000, but call on port 80. It works!

## Entry point

Finally, we add an "entry point" script that starts everything:

```
nginx
gunicorn --chdir repo/app app:app
```

## Tidying up

After development, try
```
docker images -a
```
to see all images, including lots of "dangling" ones.
Clean them up with
```
docker images prune
```

See containers with
```
docker ps -a
```

## Run-and-delete

For testing, it's also nice to create containers that are deleted once they are done.
Assuming our container has an entry point, we can do:
```
docker run -it --rm image_name
```
Note the lack of "bash" at the end, which specifies to use the entry point instead.

## Run-and-connect

As a final local test before deploying, we can do:
```
docker run -it --rm -p 5000:80 michael/artefact-api
```
Now we can use a client on the host machine to connect to port 5000!


