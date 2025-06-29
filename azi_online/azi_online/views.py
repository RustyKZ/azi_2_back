from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from urllib.parse import urlencode

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.sessions.models import Session
from django.utils import timezone

from rest_framework.authtoken.models import Token

from rest_framework.response import Response

"""
def run_function_view(request):
    # Здесь вы можете выполнить вашу функцию
    # Пример: Вернем JSON-ответ
    response_data = {'result': 'Функция успешно выполнена'}
    return JsonResponse(response_data)

def run_signup_view(request):
    name = 'testuser_05'
    password = 'testpassword@1'    
    email = 'testuser_05@ryba.com'
    # Создание нового пользователя
    user, created = User.objects.get_or_create(username=name, email=email)
    if created:
        user.set_password(password)
        print('RUN_SIGNUP_VIEW: password updated!')
        user.save()
        print('RUN_SIGNUP_VIEW: user saved!')
        # Аутентификация пользователя после регистрации
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        print('RUN_SIGNUP_VIEW: user logged')
        response_data = {'result': 'Регистрация успешно выполнена'}
    else:
        response_data = {'result': 'Ошибка: Пользователь уже существует'}
    return JsonResponse(response_data)

   
def run_login_view(request):
    # Тестовые данные
    name = 'info'
    email = 'info@rusty.kz'
    password = ''

    # Попытка аутентификации пользователя по email
    user = authenticate(request, username=name, email=email, password=None)

    if user is not None:
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        response_data = {'result': 'Авторизация успешно выполнена'}
    else:
        # Неверные учетные данные
        response_data = {'result': 'Ошибка: Неверные учетные данные'}

    return JsonResponse(response_data)    

def run_logout_view(request):
    logout(request)
    response_data = {'result': 'Выход успешно выполнен'}
    return JsonResponse(response_data)

def run_google_view(request):
    # URL для перенаправления пользователя на страницу аутентификации Google
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount"
#    google_auth_url = reverse('socialaccount_signup', args=['google'])
    params = {
        'client_id': '746578585810-cl1hd0s6kvde9dqq4u39gbpb68mmrpib.apps.googleusercontent.com',
        'redirect_uri': 'http://127.0.0.1:8000/accounts/google/login/callback/',
        'scope': 'profile',
        'response_type': 'code',
        'state': 'wZZkUfwR5rQujArp',
        'service': 'lso',
        'o2v': '2',
        'theme': 'glif',
        'flowName': 'GeneralOAuthFlow'
    }    
    # Подготовка URL для перенаправления
    redirect_url = f"{google_auth_url}?{urlencode(params)}"
    print(redirect_url)
    response_data = {'url': redirect_url}
    # Выполнение перенаправления
    return JsonResponse(response_data)


def user_signup_django(username, password, email):
    # Создание нового пользователя
    user, created = User.objects.get_or_create(username=username, email=email)
    if created:
        user.set_password(password)
        user.save()
        return True  # Регистрация успешно выполнена
    else:
        return False  # Пользователь уже существует

def user_login_django(request, username, password, email):
    user = authenticate(request, username=username, email=email, password=password)
    if user is not None:
        print(f'USER LOGIN DJANGO: user is not None')
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        print(f'USER LOGIN DJANGO: user is logged')
        # Создаем или получаем токен для пользователя
        token, created = Token.objects.get_or_create(user=user)
        # Возвращаем токен на фронтенд
        return token.key
    else:
        return None

def user_login_wp(request, username, email):
    user = authenticate(request, username=username, email=email)
    if user is not None:
        print(f'USER LOGIN DJANGO: user is not None')
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        print(f'USER LOGIN DJANGO: user is logged')
        # Создаем или получаем токен для пользователя
        token, created = Token.objects.get_or_create(user=user)
        # Возвращаем токен на фронтенд
        return token.key
    else:
        return None


def user_logout_django(request):
    # Получаем токен пользователя
    try:
        token = request.auth
    except AttributeError:
        return Response({"detail": "Authentication credentials were not provided."}, status=401)
    # Удаляем токен из базы данных
    token.delete()
    # Выходим пользователя
    logout(request)
    return Response({"detail": "Successfully logged out."})

"""