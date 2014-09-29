import subprocess
from os import path

import nginxparser

from ipyproxy import app


def reload():
    subprocess.check_call(('service', 'nginx', 'reload'))


def env_location_block(env):
    return nginxparser.dumps([
        ['location', env.url + '/'], [
            ['proxy_pass', '{0.scheme}://127.0.0.1:{0.port}/'.format(env)],
            ['proxy_redirect', 'default'],
            ['proxy_http_version', '1.1'],
            ['include', app.instance_path + '/proxy_headers.conf'],
            ['proxy_set_header', 'Upgrade', '$http_upgrade'],
            ['proxy_set_header', 'Connection', '"Upgrade"'],
        ],
        ['location', '^~', env.url + '/static/'], [
            ['alias', env.static_dir],
        ],
    ])


def write_nginx_conf():
    with app.open_instance_resource('ipyproxy.conf', 'r') as file:
        nginxparser.dump([
            ['location', app.config.BASE_URL], [
                ['proxy_pass', '{PREFERRED_URL_SCHEME}://{{SERVER_NAME}}/'.format(**app.config)],
                ['proxy_redirect', 'default'],
                ['include', app.instance_path + '/proxy_headers.conf']
            ],
            ['include', app.instance_path + '/ipython-locations/*'],
        ], file)


def server_block_include():
    return nginxparser.dumps([
        ['include', path.join(app.instance_path, 'ipyproxy.conf')]
    ])
