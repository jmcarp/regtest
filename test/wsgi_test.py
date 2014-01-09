
PORT = 8080

def launch_django_wsgi():

    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = \
        'django_wsgi.settings'

    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()

    from werkzeug.serving import run_simple
    
    return app
    #run_simple('localhost', PORT, app)
