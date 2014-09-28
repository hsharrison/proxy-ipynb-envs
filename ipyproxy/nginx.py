import subprocess


def reload():
    subprocess.check_call(('service', 'nginx', 'reload'))
