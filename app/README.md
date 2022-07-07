# Flask-based REST API for the artefact model

To install for local development:

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

To test, run 

1. Run `python app.py` inside the virtual environment (this starts a development server).
2. Open `../html/index.html` in a browser and try it out.

For development you might want to use a Python client instead of a JS one.
To do this, `pip install requests` and run `python client.py`.

## How the app bit works

The app is built using 

- [FlaskRESTful](https://flask-restful.readthedocs.io/en/latest/), which is a tool to build [REST](https://en.wikipedia.org/wiki/Representational_state_transfer)ful APIS using
  - [Flask](https://flask.palletsprojects.com/en/2.1.x/), which is a tool to build web applications, built on
    - [Werkzeug](https://palletsprojects.com/p/werkzeug/), which is a tool to write web servers (handling HTTP requests) using the
      - [WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface), or Web Server Gateway Interface, which is a calling convention to let web servers interact.
      
What all this means is that we'll create a tiny `app.py` that can either run a tiny server (for development) or be used by an application server such as `gunicorn`.
This application server can then be connected to proper servers (Apache, NGINX, etc.) via the WSG interface.
So when a user makes a HTTP request, it goes to the proper server, which then passes it on to our app via the WSG interface. 

The bits you need to know about to make changes to the app are FlaskRESTful and Flask.

The API itself is defined in [API.md](../API.md).

## How the simmulations work

Simulations are defined in `simulations.py`.

Each simulation has a name, description, and a list of parameters.
Each parameter maps to a model variable, and has an API name, default value, and a range defined with `lower`, `upper` and `step`.

Simulations define an `_initialise()` method that handles things like loading a model, creating a protocol, and pre-pacing.
The final step in this process is to create a **precompiled simulation object**.
These are a new addition to Myokit, and make it possible to run simulations without compiling.
To do this, you need to (1) bring your model into the initial state you want your simulation to have, (2) get a protocol ready, and (3) create a simulation with a `path` argument.
See the `DefaultSimulation` for an example.

When the app is deployed on the server, it will automatically call all the `_initialise` methods to compile the simulations.
When a request is made to the app's API it will load the compiled sim and use that.


These are run using Myokit.
To make things fast, we compile simulations and store them to disk.
Each call to the server then loads a simulation and runs it.
