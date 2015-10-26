from __future__ import unicode_literals
from fabric.api import env, put, roles, run
from fabric.tasks import execute
from fabric.contrib.project import rsync_project
import os


project_dir = os.path.dirname(__file__)

env.roledefs.update({
    'webserver': (
        'root@renass-web1.u-strasbg.fr',
    )
})


@roles('webserver')
def uwsgi():
    put('upstart/gissmo.conf', '/etc/init')
    run('service gissmo restart')


@roles('webserver')
def deploy():
    rsync_project(
        local_dir=project_dir + '/',
        remote_dir='/srv/app/gissmo',
        exclude=('.git', '.gitignore', '*.pyc'),
        delete=True
    )

    run('/srv/env/gissmo/bin/pip install -r /srv/app/gissmo/requirements.txt')
    run('mkdir -p /srv/app/gissmo/static')
    run('/srv/env/gissmo/bin/python \
/srv/app/gissmo/manage.py collectstatic --noinput --clear')


def all():
    execute(deploy)
    execute(uwsgi)
