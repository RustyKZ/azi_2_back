"""
WSGI config for azi_online project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

from django.conf import settings
import socketio
import eventlet
from django.core.wsgi import get_wsgi_application

from games.sockets import sio, minute_scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

# Настройка eventlet
#eventlet.monkey_patch()
eventlet.monkey_patch(socket=False, os=False)

# Создание исполнителя для пула потоков
executor = ThreadPoolExecutor()

# Создание планировщика задач
scheduler = BackgroundScheduler(executors={"default": executor})

scheduler.add_job(minute_scheduler, 'interval', minutes=1)

# Запуск планировщика
scheduler.start()

# Создание WSGI-приложения Django
app = get_wsgi_application()

# Создание WSGI-приложения SocketIO
application = socketio.WSGIApp(sio, app)

#Запуск WSGI сервера eventlet
eventlet.wsgi.server(eventlet.listen(('', 8000)), application)