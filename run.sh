#!/bin/bash
FLASK_APP="server" poetry run python -m flask run --host=0.0.0.0.0 > /dev/null 2>&1 & disown
poetry run python main.py
