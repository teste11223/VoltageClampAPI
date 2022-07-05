# A python web api for the artefacts app

## Installation

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Testing

1. Run `./app.py` (inside the virtual environment).
2. Open `html/index.html` in a browser & try it out.

## Preliminary API:

### GET to /

Returns an object:
```
{
    name={
        desc=...,
        default=...,
        choices=...,
    },
    ...
}
```
where
- `name` A string containing the argument name
- `desc` A string containing a user-friendly name
- `default` A float or bool containing the default values
- `choices` A list of suggested values

### POST to /

Should be called with `Content-type` of `application/json`.
Returns 200 only if sim is succesful.
Else expect `responseText` and/or `responseJSON` to be set with an error message.

Data should be a dict which can map any of the `name`s returned by `GET` onto a value.
Can also be empty.

Succesful sim returns an object:
```
{
    time=...,
    voltage=...,
    current=...,
}
```
with the simulation results.
