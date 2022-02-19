#!/bin/bash
FLASK_APP="server" poetry run python -m flask run > /dev/null 2>&1 & disown
poetry run python main.py
