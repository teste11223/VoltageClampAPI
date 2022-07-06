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

# Add limiter
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
class Sim(Resource):
    """ Provides access to a simulation. """
    def __init__(self, sim):
        print(f'I GOT A SIM f{sim}')
        self.sim = sim

    def post(self):
        """ Run a simulation. """
        return self.sim.run(app.logger)

    def get(self):
        """ Return settings info. """
        return self.sim.info()


# Set up API resource routing
api = Api(app)
api.add_resource(Sim, '/default', resource_class_kwargs={'sim': sim_default})


# Start method for debugging
if __name__ == '__main__':
    app.run(debug=True)
