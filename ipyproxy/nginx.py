"""Utilities related to managing nginx."""
import subprocess
import os

from flask import render_template

from ipyproxy import app


def reload():
    subprocess.check_call(('service', 'nginx', 'reload'))
