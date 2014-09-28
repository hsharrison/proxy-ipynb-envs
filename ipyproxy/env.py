from os import path
import subprocess
import re

from flask import render_template

from ipyproxy import app, nginx


class IPythonEnvironment:
    def __init__(self, env_dir, port=None, scheme='http', name=None, profile_args=None):
        self.dir = env_dir.rstrip('/')
        self.name = name or path.basename(self.dir)
        self.ipython_bin = path.join(self.dir, 'bin', 'ipython')

        self.port = port
        self.scheme = scheme
        self.profile_args = list(profile_args) if profile_args else []

        self.resolve_invariants()

    @property
    def url(self):
        return '{}{}/'.format(app.config.BASE_URL, self.name)

    @property
    def pid_path(self):
        return path.join(app.instance_path, self.name, 'pid')

    @property
    def location_path(self):
        return path.join(app.instance_path, self.name, 'location')

    def get_pid(self):
        try:
            with open(self.pid_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            raise RuntimeError('{] assumed to exist but does not'.format(self.pid_path))

    def get_profile_path(self):
        try:
            return str(subprocess.check_output(
                [self.ipython_bin, 'profile', 'locate', self.name],
                universal_newlines=True
            )).strip()
        except subprocess.CalledProcessError:
            raise RuntimeError(
                '{} profile locate {} failed: The profile was assumed to exist and does not'.format(
                    self.ipython_bin, self.name))

    def location_file_exists(self):
        return path.exists(self.location_path)

    def write_location(self):
        with open(self.location_path, 'r') as file:
            file.write(render_template('ipython_location', app=app, env=self))
        nginx.reload()

    def create_profile(self):
        subprocess.check_call(
            [self.ipython_bin, 'profile', 'create', self.name]
            + self.profile_args
        )

        with open(path.join(self.get_profile_path(), 'ipython_notebook_config.py'), 'r') as file:
            file.write(render_template('ipython_notebook_config.py', app=app, env=self))

    def launch_server(self, *args):
        proc = subprocess.Popen(
            [self.ipython_bin, 'notebook',
             '--profile', self.name,
             '--no-browser',
             '--port={}'.format(self.port),
             ] + list(args),
            stderr=subprocess.PIPE,
        )

        for line in proc.stderr.readline():
            port_match = re.match(r'The IPython Notebook is running at: https?://[\da-z\.-]+:(\d*)/', line)
            if port_match:
                self.port = port_match.group(1)
                break

        with open(self.pid_path, 'w') as f:
            f.write(str(proc.pid))

    def get_port(self):
        try:
            notebook_list = str(subprocess.check_output(
                [self.ipython_bin, 'notebook', 'list', '--profile', self.name],
                universal_newlines=True
            ))
        except subprocess.CalledProcessError:
            raise RuntimeError(
                '{} notebook list --profile {} failed: The server was assumed to be running and it was not'.format(
                    self.ipython_bin, self.name)
            )

        return re.match(r'https?://[\da-z\.-]+:(\d*)/', notebook_list.split()[1]).group()