#!/usr/bin/env python
#
# Flask app for voltage clamp simulations
#
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Resource, Api

import simulations


# Create app and api
app = Flask(__name__)
CORS(app)
api = Api(app)

# Running in production? Then assume we're behind a proxy (e.g. nginx)
if __name__ != '__main__':
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

# Add limiter (note that nginx etc. should handle this too).
# https://flask-limiter.readthedocs.io/en/stable/
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=['10 per second', '30 per minute'],
)

# In debug mode? Then initialise simulations
if __name__ == '__main__':
    simulations.Simulation.initialise()

# Create simulation objects
sim_default = simulations.DefaultSimulation()


# Create the "resources" this API provides
class Overview(Resource):
    """ Provides a list of simulations. """
    def get(self):
        return {
            'simulations': [
                'default',
            ]
        }


class Sim(Resource):
    """ Provides access to a simulation. """
    def __init__(self, sim):
        self.sim = sim

    def post(self):
        return self.sim.run(app.logger)

    def get(self):
        return self.sim.info()


# Set up API resource routing
api = Api(app)
api.add_resource(Overview, '/')
api.add_resource(Sim, '/default', resource_class_kwargs={'sim': sim_default})


# Start method for debugging
if __name__ == '__main__':
    app.run(debug=True)
