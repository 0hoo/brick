from fabric.api import env, run, cd, sudo


env.user = 'tmb'
env.hosts = ['trackmybrick.com']
app_directory = '/home/tmb/brick'
django_project_directory = app_directory + '/bricksite'

def deploy():
    with cd(app_directory):
        run('git pull origin master')
        with cd(django_project_directory):
            run('python3 manage.py migrate')
            sudo('systemctl restart nginx')
            sudo('systemctl restart uwsgi')
