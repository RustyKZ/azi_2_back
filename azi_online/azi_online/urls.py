from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import render
from .views import *

from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

#import socketio
#sio = socketio.Server(cors_allowed_origins=[settings.CLIENT_URL])

"""
def home(request):
    return render(request, 'home.html')

def socketio_view(request):
    print(f'SOCKETVIEW !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')    
    return HttpResponse("Socket.IO URL is working!")
"""
urlpatterns = [
    #path('', home, name='home'),
    path('admin/', admin.site.urls),
    #path('accounts/', include('allauth.urls')),
    #path('accounts/', include('allauth.socialaccount.urls')),
    re_path(r'^auth/', include('drf_social_oauth2.urls', namespace='drf')),
    path('api/', include('api.urls')),
    #re_path(r'^socket.io/', socketio_view),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


