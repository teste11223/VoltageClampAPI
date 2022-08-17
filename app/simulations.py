#!/usr/bin/env python
#
# Simulations for the flask app.
#
import inspect
import os

import numpy as np

from flask_caching import Cache

import myokit

# Get path of current module
try:
    frame = inspect.currentframe()
    DIR_ROOT = os.path.abspath(os.path.dirname(inspect.getfile(frame)))
finally:
    # Always manually delete frame
    # https://docs.python.org/2/library/inspect.html#the-interpreter-stack
    del(frame)

# Paths
DIR_CACHE = os.path.join(DIR_ROOT, 'cache')
DIR_MMT = os.path.join(DIR_ROOT, 'data')

cache = Cache(config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 0})


class P(object):
    """ Model parameter. """

    def __init__(self, json_name, model_name, description, default,
                 lower, upper, step):
        self.json_name = json_name
        self.model_name = model_name
        self.description = description
        self.default = default
        self.lower = lower
        self.upper = upper
        self.step = step

        self.info = {
            'name': json_name,
            'description': description,
            'default': default,
            'min': self.lower,
            'max': self.upper,
            'step': self.step,
        }

    def fix_bounds(self, value):
        """ Returns ``value`` if in bounds, else nearest limit. """
        return min(self.upper, max(self.lower, value))


class Simulation(object):
    """
    Abstract simulation class.

    Simulations run using precompiled back-ends. These can be created using
    :meth:`initialise`. This can be done before running the main web app.
    """
    filename = None
    name = None
    description = None
    parameters = []

    command_voltage = None
    membrane_voltage = None
    recorded_current = None
    cell_current = None
    ideal_current = None

    duration = None
    log_times = None    # Optional

    def __init__(self):

        # Check that precompiled simulation is available
        self.path = os.path.join(DIR_CACHE, self.filename)
        if not os.path.isfile(self.path):
            raise RuntimeError(f'Simulation {self.name} not initialised.')

        # Create an argument parser and a parameter name mapping
        # We import flask_restful here instead of at the module level so that
        # simulations can be initialised without having flask_restful
        # installed.
        from flask_restful. reqparse import RequestParser
        self.parser = RequestParser()
        for p in self.parameters:
            self.parser.add_argument(
                p.json_name, type=float, default=p.default, required=False)

        self.log = [
            self.time,
            self.command_voltage,
            self.membrane_voltage,
            self.recorded_current,
            self.cell_current,
            self.ideal_current,
        ]

    @classmethod
    def _initialise(cls):
        """
        Initialises this simulation, pre-paces if necessary, and stores a
        re-usable compiled simulation.
        """
        raise NotImplementedError

    @staticmethod
    def initialise():
        """ Initialises all simulation subclasses. """
        # Create cache dir if needed
        os.makedirs(DIR_CACHE, exist_ok=True)

        # Initialise all
        for cls in Simulation.__subclasses__():
            cls._initialise()

    def info(self):
        """
        Returns a (JSON-convertible) dict with information about this
        simulation.
        """
        return {
            'description': self.description,
            'parameters': [p.info for p in self.parameters],
        }

    def run(self, logger):
        # Parse arguments (from the global flask.Request object)
        self.logger = logger
        args = self.parser.parse_args(strict=True)
        return self.perform_simulation(**args)

    @cache.memoize()
    def perform_simulation(self, **kwargs):
        # Create a new simulation back-end
        b = myokit.tools.Benchmarker()
        s = myokit.Simulation.from_path(self.path)

        # Set parameters
        for p in self.parameters:
            s.set_constant(p.model_name, p.fix_bounds(kwargs[p.json_name]))

        # Run and return
        d = s.run(self.duration, log=self.log,
                  log_times=self.log_times)
        self.logger.info(f'Simulation run in {b.format()}')

        return {
            'time': list(d[self.time]),
            'command_voltage': list(d[self.command_voltage]),
            'membrane_voltage': list(d[self.membrane_voltage]),
            'recorded_current': list(d[self.recorded_current]),
            'cell_current': list(d[self.cell_current]),
            'ideal_current': list(d[self.ideal_current]),
        }


class DefaultSimulation(Simulation):
    """
    Default simulation: voltage clamp artefact model in a cell without any
    currents except a leak current.

    """
    filename = 'default.zip'
    name = 'default'
    description = (
        'A cell with no ionic currents except leak, held at 0mV and'
        ' stimulated with a 20mV pulse for 50ms (0mV for 50ms, then 20mV for'
        ' 50ms, then 0mV for 50ms again).'
    )

    parameters = [
        P('membrane_conductance', 'membrane.gm', 'Membrane conductance (nS)', 10, 0, 40, 0.5),  # noqa
        P('membrane_capacitance', 'cell.Cm', 'Membrane capacitance (pF)', 20, 10, 150, 5),  # noqa
        P('esimated_membrane_capacitance', 'voltage_clamp.Cm_est', 'Estimated membrane capacitance (pF)', 25, 10, 150, 5),  # noqa
        P('pipette_capacitance', 'voltage_clamp.C_prs', 'Pipette capacitance (pF)', 5, 0, 10, 0.1),  # noqa
        P('esimated_pipette_capacitance', 'voltage_clamp.C_prs_est', 'Estimated pipette capacitance (pF)', 4, 0, 10, 0.1),  # noqa
        P('series_resistance', 'voltage_clamp.R_series_MOhm', 'Series resistance (MOhm)', 10, 0.5, 100, 0.5),  # noqa
        P('esimated_series_resistance', 'voltage_clamp.R_series_est_MOhm', 'Estimated series resistance (MOhm)', 10, 0.5, 100, 0.5),  # noqa
        P('series_resistance_compensation', 'voltage_clamp.alpha_percentage', 'Percentage series resistance (%)', 70, 0, 100, 1),  # noqa
        P('effective_voltage_offset', 'voltage_clamp.V_offset_eff', 'Effective voltage offset (mV)', 0, -10, 10, 0.5),  # noqa
        P('seal_resistance', 'voltage_clamp.R_seal_MOhm', 'Seal resistance (MOhm)', 500, 10, 10000, 1),  # noqa
        P('estimated_seal_resistance', 'voltage_clamp.R_seal_est_MOhm', 'Estimated seal resistance (MOhm)', 1000, 10, 10000, 1),  # noqa
        P('leak_reversal_potential', 'voltage_clamp.E_leak', 'Leak reversal potential (mV)', -80, -150, 150, 0.5),  # noqa
        P('estimated_leak_reversal_potential', 'voltage_clamp.E_leak_est', 'Estimated leak reversal potential (mV)', -80, -150, 150, 0.5),  # noqa
    ]

    time = 'engine.time'
    command_voltage = 'voltage_clamp.V_c'
    membrane_voltage ='membrane.V'
    recorded_current = 'voltage_clamp.I_out_pA'
    cell_current = 'membrane.I_ion'
    ideal_current = 'membrane.I_ideal'

    duration = 150.1
    log_times = np.arange(0, duration, 0.01)

    @classmethod
    def _initialise(cls):

        # Load model
        path = os.path.join(DIR_MMT, 'voltage-clamp.mmt')
        m = myokit.load_model(path)

        # Pre-pace at 0mV, and update model
        x = m.clone()
        x.binding('pace').set_rhs(0)
        x.binding('pace').set_binding(None)
        s = myokit.Simulation(x)
        s.run(100 * 1000, log=myokit.LOG_NONE)
        m.set_state(s.state())

        # Create protocol
        p = myokit.Protocol()
        p.add_step(level=0, duration=50)
        p.add_step(level=20, duration=50)
        p.add_step(level=0, duration=50)

        # Create and store a simulation back-end
        path = os.path.join(DIR_CACHE, cls.filename)
        myokit.Simulation(m, p, path=path)


if __name__ == '__main__':
    print('Initialising simulations...')
    Simulation.initialise()
    print('Done.')
