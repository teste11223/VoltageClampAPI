#!/usr/bin/env python
#
# Flask app for voltage clamp simulations
#
import os

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Resource, Api, reqparse
import myokit

# Paths
dir_cache = 'cache'
dir_mmt = 'mmt'
os.makedirs(dir_cache, exist_ok=True)

# Model settings
model_path = os.path.join(dir_mmt, 'voltage-clamp.mmt')
t_var = 'engine.time'
v_var = 'membrane.V'
i_var = 'voltage_clamp.I_out'
log_vars = [t_var, v_var, i_var]

# First protocol
proto_1 = os.path.join(dir_mmt, 'step-1.mmt')
sim_1 = os.path.join(dir_cache, 'test.zip')


# Simulation engine
def create_simulation():

    # Load model
    m = myokit.load_model(model_path)

    # Load first protocol, pre-pace simulation and update model
    m1 = m.clone()
    p1 = myokit.load_protocol(proto_1)
    m.binding('pace').set_rhs(p1.head().level())
    m.binding('pace').set_binding(None)

    b = myokit.tools.Benchmarker()
    s1 = myokit.Simulation(m1, p1)
    app.logger.info(f'Simulation created in {b.format()}')
    b.reset()
    s1.run(10000, log=myokit.LOG_NONE)
    app.logger.info(f'Simulation pre-paced in {b.format()}')
    m1.set_state(s1.state())
    b.reset()
    s1 = myokit.Simulation(m1, p1, path=sim_1)
    app.logger.info(f'Simulation stored in {b.format()}')


# Create app and api
app = Flask(__name__)
api = Api(app)

# Add limiter
# https://flask-limiter.readthedocs.io/en/stable/
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=['2 per second', '30 per minute'],
)

# Set up argument parsing
# https://flask-restful.readthedocs.io/en/latest/api.html#module-reqparse
parser = reqparse.RequestParser()
parser.add_argument('one', type=int, required=False)


# Create a single resource
class VoltageClampRun(Resource):
    """ Returns simulation results. """

    def post(self):
        args = parser.parse_args(strict=False)

        b = myokit.tools.Benchmarker()
        s = myokit.Simulation.from_path(sim_1)
        app.logger.info(f'Simulation loaded in {b.format()}')

        b.reset()
        d = s.run(1000, log=log_vars)
        app.logger.info(f'Simulation run in {b.format()}')

        return {
            'time': list(d[t_var]),
            'voltage': list(d[v_var]),
            'current': list(d[i_var])
        }


# Set up API resource routing
api = Api(app)
api.add_resource(VoltageClampRun, '/')


# Make sure simulation is created (after app is created)


app.before_first_request(create_simulation)


# Start method for debuggin
if __name__ == '__main__':
    app.run(debug=True)
