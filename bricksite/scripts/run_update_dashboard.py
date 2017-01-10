import os
import sys


def setup():
    top = os.path.split(os.getcwd())[0]
    bricksite = top + '/bricksite'
    sys.path.append(bricksite)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()


def update_all_users():
    from dashboard.utils import snapshot_latest_dashboard
    from items.utils import update_item_record
    from django.contrib.auth.models import User
    print('START: update_all_dashboard')
    for user in User.objects.all():
        snapshot_latest_dashboard(user)
        update_item_record(user)
    print('END: update_all_dashboard')

if __name__ == "__main__":
    setup()
    update_all_users()