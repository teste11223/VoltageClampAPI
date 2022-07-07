#!/usr/bin/env python
#
# Initialises all simulations.
# Should be called once before running a server.
#
import simulations

print('Initialising simulations...')
simulations.Simulation.initialise()
print('Done.')
