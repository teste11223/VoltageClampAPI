#!/usr/bin/env python
#
# Flask app for voltage clamp simulations
#
import os

import myokit
import numpy as np

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Resource, Api, reqparse


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
duration_1 = None


# Parameters
class P(object):
    """ Model parameter class. """
    _params = {}

    def __init__(self, json_name, model_name, description, default,
                 lower, upper, step, multiplier=1):
        self.json_name = json_name
        self.model_name = model_name
        self.description = description
        self.default = default
        self.choices = list(np.arange(lower, upper + step, step, dtype=float))

    @staticmethod
    def r(*args):
        """ Register a parameter. """
        P._params[args[0]] = P(*args)

    def add_to_parser(parser):
        """ Add all parameters to a req parser. """
        for p in P._params.values():
            parser.add_argument(p.json_name, type=float, default=p.default,
                                required=False)

    @staticmethod
    def by_json(json):
        return P._params[json]

    @staticmethod
    def info_dict():
        info = {}
        for p in P._params.values():
            info[p.json_name] = dict(
                desc=p.description,
                default=p.default,
                choices=p.choices,
            )
        return info


#P.r('membrane_conductance', '', 'Membrane conductance (ns)', 10, (0, 40, 0.5))  # noqa
P.r('membrane_capacitance', 'cell.Cm', 'Membrane capacitance (pF)', 20, 10, 150, 5)  # noqa
P.r('pipette_capacitance', 'voltage_clamp.C_prs', 'Pipette capacitance (pF)', 5, 0, 10, 0.1)  # noqa
#P.r('series_resistance', 'voltage_clamp.R_series', 'Series resistance (MOhm)', 30, 0.5, 100, 0.5)  # noqa
P.r('esimated_membrane_capacitance', 'voltage_clamp.Cm_est', 'Estimated membrane capacitance (pF)', 25, 10, 150, 5)  # noqa
P.r('esimated_pipette_capacitance', 'voltage_clamp.C_prs_est', 'Estimated pipette capacitance (pF)', 4, 0, 10, 0.1)  # noqa
#P.r('esimated_series_resistance', 'voltage_clamp.R_series_est', 'Estimated series resistance (MOhm)', 25, 0.5, 100, 0.5)  # noqa
#P.r('series_resistance_compensation_enabled', '', 'Enable series resistance compensation', 0, (0, 1, 1))  # noqa
#P.r('series_resistance_compensation', '', 'Percentage series resistance (%)', 0, (0, 100, 5))  # noqa
P.r('effective_voltage_offset', 'voltage_clamp.V_offset_eff', 'Effective voltage offset (mV)', 0, -10, 10, 0.5)  # noqa


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

    global duration_1
    duration_1 = p1.characteristic_time()

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

# Set up argument parsing
# https://flask-restful.readthedocs.io/en/latest/api.html#module-reqparse
parser = reqparse.RequestParser()
P.add_to_parser(parser)


# Create a single resource
class VoltageClampRun(Resource):
    """ Returns simulation results. """

    def post(self):
        """ Run a simulation. """

        args = parser.parse_args(strict=True)

        b = myokit.tools.Benchmarker()
        s = myokit.Simulation.from_path(sim_1)
        app.logger.info(f'Simulation loaded in {b.format()}')

        b.reset()
        for k, v in args.items():
            print(v)
            s.set_constant(P.by_json(k).model_name, v)
        app.logger.info(f'Parameters applied in {b.format()}')

        b.reset()
        d = s.run(duration_1, log=log_vars)
        app.logger.info(f'Simulation run in {b.format()}')

        return {
            'time': list(d[t_var]),
            'voltage': list(d[v_var]),
            'current': list(d[i_var])
        }

    def get(self):
        """ Return settings info. """
        return P.info_dict()



# Set up API resource routing
api = Api(app)
api.add_resource(VoltageClampRun, '/')

# Make sure simulation is created (after app is created)
app.before_first_request(create_simulation)


# Start method for debuggin
if __name__ == '__main__':
    app.run(debug=True)
