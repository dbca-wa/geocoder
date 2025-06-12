#!/bin/bash
gunicorn 'geocoder:create_app()' --config gunicorn.py
