# Voltage-artefact simulator API

Everything works by making HTTP requests to some address, e.g. `http://localhost/` or `https://my-real-server/artefact-app/`.
**We will refer to this base URL as `/`.**

All requests should have `Content-Type: application/json`.

## Querying available simulators

To get a list of available simulators, make a `GET` request to `/`.
The result will be a [JSON](https://en.wikipedia.org/wiki/JSON) object:
```
{
    "simulations": [
        "default",
        ...
    ]
}
```
where `simulations` contains a list of simulation names.

## Using a simulator

A simulation is used by making request to `/simulator-name`.
For example, to use the simulation called `default` you make requests to `/default`.

To run a simulation with the default parameters, make a `POST` request.
This returns a JSON object with the simulation results:
```
{
    "time": [0, 1, 2, ...],
    "voltage": [-80, -80, -80, ...],
    "current": [0, 0, 0, ...]
}
```

To run a simulation with changed simulation parameters, send a JSON object in the `POST` request that maps parameter names to values.
For example:
```
{
    "membrane_capacitance": 10
}
```
All parameters not set in the `POST` request are left at their defaults (the API is stateless).

To get information about the available parameters, make a `GET` request.
This will return a JSON object:
```
{
    "parameters": [
        {
            "name": ...,
            "description": ...,
            "default_value": ...,
            "min": ...,
            "max": ...,
            "step", ...
        },
        ...
    ]
}
```
Here `name` contains the parameter name used in the API, while `description` is a user friendly name including units.
The default value is given in `default_value`, along with a `minimum` and `maximum` allowed value (anything outside this range will be clipped to the boundaries of the allowed range).
A suggested `step` for e.g. slider controls is given in `step`.

All parameter values are floating point numbers.

### Simulation errors

POST requests return status 200 only if the simulation was succesful.
For any other status code, you can use `responseText` or `responseJSON` to obtain an error message.
