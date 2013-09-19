from fabric.api import env, put, roles, run
from fabric.tasks import execute
from fabric.contrib.project import rsync_project
import os


project_dir = os.path.dirname(__file__)

env.roledefs.update({
    'webserver': (
        'root@renass-web1.u-strasbg.fr',
        'root@renass-web2.u-strasbg.fr',
    )
})


@roles('webserver')
def uwsgi():
    put('upstart/renass.conf', '/etc/init')
    run('service renass restart')


@roles('webserver')
def deploy():
    rsync_project(
        local_dir=project_dir+'/',
        remote_dir='/srv/app/gissmo',
        exclude=('.git', '.gitignore', '*.pyc'),
        delete=True
    )

    run('/srv/env/gissmo/bin/pip install -r /srv/app/gissmo/requirements.txt')


def all():
    execute(deploy)
    #execute(uwsgi)
