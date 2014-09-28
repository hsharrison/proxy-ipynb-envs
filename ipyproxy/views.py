from os import path

from flask import redirect, abort, request

from ipyproxy import app
from ipyproxy.env import IPythonEnvironment, NotAnEnvironment


@app.route('/<env_name>/')
def redirect_to_notebook(env_name):
    env_dir = request.args.get('dir', path.join(app.config.ENVS_DIR, env_name))
    try:
        env = IPythonEnvironment(env_dir, scheme=app.config.PREFERRED_URL_SCHEME, name=env_name)
    except NotAnEnvironment:
        return abort(404)
    return redirect(app.config.PROXY_SERVER + env.url + '/tree')
