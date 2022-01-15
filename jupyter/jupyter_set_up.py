import os
import sys

PWD = os.path.dirname(os.getcwd())


def init_django():
    os.chdir(PWD)
    sys.path.insert(0, PWD)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    import django
    django.setup()
