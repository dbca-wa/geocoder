# Geocoder

Minimal Flask WSGI application to provide an API for geocoding cadastre data.

## Installation

The recommended way to set up this project for development is using
[uv](https://docs.astral.sh/uv/)
to install and manage a Python virtual environment.
With uv installed, install the required Python version (see `pyproject.toml`). Example:

    uv python install 3.13

Change into the project directory and run:

    uv sync

Activate the virtualenv like so:

    source .venv/bin/activate

To run Python commands in the activated virtualenv, thereafter run them like so:

    ipython

Manage new or updated project dependencies with uv also, like so:

    uv add newpackage==1.0

## Environment variables

This project uses **python-dotenv** to set environment variables (in a `.env` file).
The following variables are required:

    DATABASE_URI

## Usage

To run a local copy of the application:

    flask --app geocoder run --debug --port 8080 --reload
    # Serve via Gunicorn:
    gunicorn 'geocoder:create_app()' --config gunicorn.py --reload

The application runs on port 8080 by default. To change this, modify `gunicorn.py`.

## Testing

Set up a test database (if required), and run unit tests using `pytest`:

    pytest --dburl postgresql+psycopg://user:password@hostname/dbname

## Docker image

To build a new Docker image from the `Dockerfile`:

    docker image build -t ghcr.io/dbca-wa/geocoder .

To run a Docker container locally, publishing container port 8080 to a local port:

    docker container run --rm --publish 8080:8080 --env-file .env ghcr.io/dbca-wa/geocoder

## Pre-commit hooks

This project includes the following pre-commit hooks:

- TruffleHog: <https://docs.trufflesecurity.com/docs/scanning-git/precommit-hooks/>

Pre-commit hooks may have additional system dependencies to run. Optionally
install pre-commit hooks locally like so:

    pre-commit install

Reference: <https://pre-commit.com/>
