import logging
import os
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def setup():
    top = os.path.split(os.getcwd())[0]
    bricksite = top + '/bricksite'
    sys.path.append(bricksite)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    import django
    django.setup()


def ebay_history():
    from products.utils import update_record_from_ebay
    logger.info('START: ebay_history')
    update_record_from_ebay()
    logger.info('END: ebay_history')

if __name__ == '__main__':
    setup()
    ebay_history()
