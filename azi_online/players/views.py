from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Players, PlayersData, PlayersStats, BlacklistIP, GreylistIP
from datetime import datetime, timezone
import json
from django.contrib.auth import logout

from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from rest_framework.response import Response

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate, logout

from .serializers import PlayersSerializer, get_player_games_history
import re

from rest_framework.decorators import api_view

import random
import string
from django.core.exceptions import ObjectDoesNotExist

from django.core.mail import send_mail, get_connection
from .models import MailServerSettings, TokenSettings, DepositWithdrawSettings, TransactionsLog, TransactionsError, WithdrawsGold, PaypalTransactionsError, PaypalTransactionsLog

import math

from .paypal import get_payment_detail

from django.db.models import F, Value, IntegerField
from .custom_request import *

# Создание экземпляра Web3

User = get_user_model()

# Создание учетной записи в классе Players
def create_player(name, email, ip_address, ref_code, language):
    if len(name) > 50:
        cutted_name = name[:50]
    else:
        cutted_name = name
    ref_id = 0
    if ref_code !='':
        ref_player = Players.objects.filter(referal_code=ref_code).first()
        ref_id = ref_player.id if ref_player else 0
    if ref_id != 0:
        start_silver = 6000
    else:
        start_silver = 1000
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    unix_time = int(current_time.timestamp())
    player = Players(
        nickname=cutted_name,
        email=email,
        password = '',
        reg_date = datetime.utcnow().replace(tzinfo=timezone.utc),
        ip_address = ip_address,
        phone = '',
        country = 0,
        silvercoin = start_silver,
        goldcoin = 0,
        bonuscoin = 0,
        democoin = 1000,
        active_table = 0,
        reputation = 1000,
        rating = 1400,
        wallet = '',
        django_name = email,
        google_uid = '',
        online_mail = False,
        online_google = False,
        online_metamask = False,
        email_is_verified = False,
        phone_is_verified = False,
        referer_id = ref_id,        
        last_activity = unix_time,
        language = language
        )
    player.save()
    player_data = get_player_data(player.id)
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)    
    action = {
        "date": unix_time,
        "coin": "silvercoin",
        "action": "deposit",
        "value": start_silver,
        "method": "start"
        }
    player_data.coin_activity.append(action)
    player_data.history_silver.append(action)
    player_data.save()


def get_player_data(user_id):
    try:
        player_data = PlayersData.objects.get(user_id=user_id)
    except PlayersData.DoesNotExist:
        player_data = PlayersData.objects.create(user_id=user_id)
    json_fields = [
        'coin_activity',
        'history_silver',
        'history_gold',
        'history_bonus',
        'history_free',
        'bonusgamehistory',
        'comments'
    ]
    for field_name in json_fields:
        if getattr(player_data, field_name) is None:
            setattr(player_data, field_name, [])
    player_data.save()    
    return player_data

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


# Функция обработки запроса /api/get_users
def get_users(request):
    try:
        players_data = Players.objects.values('id', 'nickname', 'email')
        players_list = list(players_data)
        return JsonResponse(players_list, safe=False)
    except:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method', 'code': 500})

# Функция обработки запроса /api/get_auth_status
@csrf_exempt
def user_get_status(request):    
    try:
        user_data = json.loads(request.body)
        print(f'USER GET STATUS: Data recieved successfully - {user_data}')
    except:
        return JsonResponse({'is_auth': False, "detail": "User not found.", 'code': 400})
    try:        
        login_token = user_data['token']
        print(f'USER GET STATUS: Token is {login_token}')
        if login_token == '':
            return JsonResponse({'is_auth': False, "detail": "User not found.", 'code': 400})
        user = User.objects.get(auth_token=login_token)
        print(f'USER GET STATUS: User data - {user}')
        email = user.email
        player = Players.objects.get(django_name=email)
        print(f'USER_GET_STATUS: User django name - {email}, User ID is {player.id}')        
        return JsonResponse({'is_auth': True, 
                             'is_auth_web3': player.online_metamask, 
                             'django_name': player.django_name, 
                             'user_id': player.id, 
                             'nickname': player.nickname, 
                             'wallet': player.wallet, 
                             'active_table': player.active_table,                              
                             'code': 200})
    except User.DoesNotExist:
        try:
            login_token = user_data['token']
            if login_token != '':
                return JsonResponse({'is_auth': False, "detail": "User logged now with other device!!!", 'code': 204})
        except:    
            print('USER_GET_STATUS: User not found')
            return JsonResponse({'is_auth': False, "detail": "User not found.", 'code': 400})

# Функция обработки запроса /api/user_signup
@csrf_exempt
def user_signup(request):
    if request.method == 'POST':
        user_data = json.loads(request.body)
        print(f'USER_SIGNUP: Data loaded successfully: {user_data}')
        if Players.objects.filter(nickname=user_data['name']).exists():
            return JsonResponse({'registred': False, 'message': 'Username already exists'})
        if Players.objects.filter(email=user_data['email']).exists():
            return JsonResponse({'registred': False, 'message': 'Email already exists'})
        if user_data['password'] != user_data['repassword']:
            return JsonResponse({'registred': False, 'message': 'The passwords do not match'})
        ip_address = user_data['ip_address'],
        if 'language' in user_data and user_data['language'] is not None:
            language = user_data['language']
        else:
            language = 1
        if user_signup_django(username=user_data['email'], email=user_data['email'], password=user_data['password']):
            create_player(user_data['name'], user_data['email'], ip_address, user_data['ref_code'], language)
            return JsonResponse({'registred': True, 'message': 'User signed up successfully', 'code': 200})
        else:
            return JsonResponse({'registred': False, 'message': 'Invalid request method', 'code': 400})
    else:
        print(f'USER_SIGNUP ERROR: Data not loaded')
        return JsonResponse({'registred': False, 'message': 'Invalid request method', 'code': 400})

# Функция обработки запроса /api/user_login    
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        user_data = json.loads(request.body)
        try:
            user = User.objects.get(email=user_data['email'])
            print(f'USER LOGIN: User is {user}')
        except User.DoesNotExist:
            print(f'USER LOGIN: User is Except')
            return JsonResponse({'logged_in': False, 'message': 'User does not exist', 'code': 404})
        # Проверка пароля
        if not user.check_password(user_data['password']):
            return JsonResponse({'logged_in': False, 'message': 'Incorrect password', 'code': 401})
        # Удаление предыдущего токена пользователя
        try:
            old_token = Token.objects.get(user=user)
            old_token.delete()
            print(f'USER LOGIN: old token deleted!')
        except Token.DoesNotExist:
            pass        
        print(f'USER LOGIN: Data recieved successfully - {user_data}')
        login_token = user_login_django(request, username=user_data['email'], email=user_data['email'], password=user_data['password'])
        print(f'USER LOGIN: Token is {login_token}')
        if login_token is not None:
            try:
                player = Players.objects.get(django_name=user_data['email'])
                player.online_mail = True
                player.save()
                return JsonResponse({'logged_in': True, 'message': 'User logged successfully', 'token': login_token, 'code': 200, 'user_id': player.id, 'user_language': player.language})
            except:
                return JsonResponse({'logged_in': False, 'status': 'error', 'message': 'Invalid request method', 'token': login_token, 'code': 500})
        else:
            return JsonResponse({'logged_in': False, 'message': 'User login failed', 'code': 500})
    else:
        print(f'USER_LOGIN ERROR: Data not loaded')
        return JsonResponse({'logged_in': False, 'message': 'Invalid request method', 'code': 500})

# Функция обработки запроса /api/user_logout
@csrf_exempt
def user_logout(request):
    user_data = json.loads(request.body)
    print(f'USER LOGOUT: Data recieved successfully - {user_data}')
    try:
        login_token = user_data['token']
        language = user_data['language']
        # Находим пользователя по токену
        user = User.objects.get(auth_token=login_token)
        print(f'USER LOGOUT: Email is {user.email}')
        player = Players.objects.get(django_name=user.email)
        player.online_mail = False
        player.online_google = False
        player.online_metamask = False
        player.language = language
        player.save()
        # Удаляем токен пользователя
        user.auth_token.delete()
        print(f'USER LOGOUT: Token {login_token} deleted successfully')
        return JsonResponse({'logged_out': True})
    except (KeyError, User.DoesNotExist):
        print('USER LOGOUT: Token not provided or user not found')
        return JsonResponse({'logged_out': False})
    except Exception as e:
        print(f'USER LOGOUT: Error during logout: {e}')
        return JsonResponse({'logged_out': False})

# Функция обработки запроса /api/user_login_google
@csrf_exempt
def user_login_google(request):
    try:
        user_data = json.loads(request.body)        
        print(f'USER LOGIN GOOGLE: Data recieved successfully - {user_data}')
        if Players.objects.filter(django_name=user_data['email']).exists():
            return login_google(user_data)
        else:
            print(f'SIGNUP GOOGLE: {user_data}')
            return signup_google(user_data) 
    except:
        return JsonResponse({'logged_in': False, 'message': 'Google auth error', 'access_token': '', 'code': 500})

def login_google(data):
    print(f'LOGIN GOOGLE: {data}')
    try:
        user = User.objects.get(email=data['email'])
        print(f'LOGIN GOOGLE: user is {user}')
        try:            
            old_token = Token.objects.get(user=user)
            old_token.delete()
            print(f'LOGIN GOOGLE: old token deleted!')
        except:
            print(f'LOGIN GOOGLE: old token not detected!')
        auth_token = user_login_wp(data['email'])
        print(f'LOGIN GOOGLE: Token is {auth_token}')
        if auth_token is not None:            
            try:
                player = Players.objects.get(django_name=data['email'])
                player.online_google = True
                player.save()
                return JsonResponse({'logged_in': True, 'message': 'User logged successfully', 'access_token': auth_token, 'code': 200, 'user_id': player.id, 'user_language': player.language})
            except:
                return JsonResponse({'logged_in': False, 'message': 'Google auth error', 'access_token': auth_token, 'code': 500})
    except Exception as e:
        print(f'LOGIN GOOGLE: Creating user ERROR {e}')
        return JsonResponse({'logged_in': False, 'message': 'Google auth error', 'access_token': '', 'code': 500})
    

def signup_google(data):
    print(f'SIGNUP GOOGLE: {data}')    
    try:
        print(f'SIGNUP GOOGLE: Creating user {data}')
        if 'language' in data and data['language'] is not None:
            language = data['language']
        else:
            language = 1
        create_player(data['email'], data['email'], data['ip_address'], data['ref_code'], language)
        player = Players.objects.get(django_name=data['email'])
        player.email_is_verified = True
        player.save()
        user_signup_wp(data['email'])
        auth_token = user_login_wp(data['email'])
        player.online_google = True
        player.save()
        print(f'SIGNUP GOOGLE: Token is {auth_token}')
        return JsonResponse({'logged_in': True, 'message': 'User logged successfully', 'access_token': auth_token, 'code': 200, 'user_id': player.id})
    except Exception as e:
        print(f'SIGNUP GOOGLE: Creating user ERROR {e}')
        return JsonResponse({'logged_in': False, 'message': 'Google auth error', 'access_token': '', 'code': 500})

# Создание нового пользователя Джанго без пароля    
def user_signup_wp(email):    
    user, created = User.objects.get_or_create(email=email, username=email)
    if created:        
        return True  # Регистрация успешно выполнена
    else:
        return False  # Пользователь уже существует

# Получение токена для пользователя Джанго без пароля    
def user_login_wp(email):    
    user = User.objects.filter(email=email).first()    
    if user is not None:        
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        token, created = Token.objects.get_or_create(user=user)
        return token.key
    else:
        return None

# Функция обработки запроса /api/user_login_metamask
@csrf_exempt
def user_login_metamask(request):
    try:
        user_data = json.loads(request.body)
        print(f'USER LOGIN METAMASK: Data recieved successfully - {user_data}')
        mail_server_settings = MailServerSettings.objects.first()
        mail_server = mail_server_settings.user_mail_server
        email = user_data['userAddress'] + mail_server
        print(f'USER LOGIN METAMASK: Email is {email}')
        if Players.objects.filter(django_name=email).exists():
            return login_metamask(user_data)
        else:
            print(f'SIGNUP GOOGLE: {user_data}')
            return signup_metamask(user_data) 
    except:
        return JsonResponse({'logged_in': False, 'message': 'Metamask auth error', 'access_token': '', 'code': 500})

def login_metamask(data):
    print(f'LOGIN METAMASK: {data}')
    try:
        mail_server_settings = MailServerSettings.objects.first()
        mail_server = mail_server_settings.user_mail_server
        email = data['userAddress'] + mail_server
        #email = data['userAddress'] + settings.USER_MAIL_SERVER
        user = User.objects.get(email=email)
        print(f'LOGIN METAMASK: user is {user}')
        try:            
            old_token = Token.objects.get(user=user)
            old_token.delete()
            print(f'LOGIN METAMASK: old token deleted!')
        except:
            print(f'LOGIN METAMASK: old token not detected!')
        auth_token = user_login_wp(email)
        print(f'LOGIN METAMASK: Token is {auth_token}')
        if auth_token is not None:            
            try:
                player = Players.objects.get(django_name=email)
                is_valid = check_password(data['signature'], player.password)
                if not is_valid:
                    return JsonResponse({'logged_in': False, 'message': 'Metamask signature incorrect', 'access_token': '', 'code': 605})
                player.online_metamask = True
                player.save()
                return JsonResponse({'logged_in': True, 'message': 'User logged successfully', 'access_token': auth_token, 'code': 200, 'user_id': player.id, 'user_language': player.language})
            except:
                return JsonResponse({'logged_in': False, 'message': 'Metamask auth error', 'access_token': '', 'code': 600})
    except Exception as e:
        print(f'LOGIN METAMASK: Creating user ERROR {e}')
        return JsonResponse({'logged_in': False, 'message': 'Metamask auth error', 'access_token': '', 'code': 600})
        
def signup_metamask(data):
    print(f'SIGNUP METAMASK: {data}')    
    try:
        print(f'SIGNUP METAMASK: Creating user {data}')
        mail_server_settings = MailServerSettings.objects.first()
        mail_server = mail_server_settings.user_mail_server
        email = data['userAddress'] + mail_server
        #email = data['userAddress'] + settings.USER_MAIL_SERVER
        if 'language' in data and data['language'] is not None:
            language = data['language']
        else:
            language = 1
        create_player(data['userAddress'], email, data['ip_address'], data['ref_code'], language)
        player = Players.objects.get(django_name=email)
        signature = data['signature']
        hashed_signature = make_password(signature)
        player.password = hashed_signature
        player.wallet = data['userAddress']
        player.save()
        user_signup_wp(email)
        return login_metamask(data)
        #auth_token = user_login_wp(email)
        #print(f'SIGNUP METAMASK: Token is {auth_token}')
        #return JsonResponse({'logged_in': True, 'message': 'User logged successfully', 'access_token': auth_token, 'code': 200, 'user_id': 'player.id'})
    except Exception as e:
        print(f'SIGNUP METAMASK: Creating user ERROR {e}')
        return JsonResponse({'logged_in': False, 'message': 'Metamask auth error', 'access_token': '', 'code': 500})

# Функция обработки запроса /api/get_token_settings
@api_view(['GET'])
def api_get_token_settings(request):
    print('GET TOKEN SETTINGS')
    try:
        token = TokenSettings.objects.get(cointype=1)
        token_data = {
            'contract': token.contract,
            'host_wallet': token.host_wallet,
            'abi': token.abi,
            'gas': token.gas,
            'cointype': token.cointype
        }
        return JsonResponse({"status": True, "token": token_data})
    except Exception as e:
        print(f'GET TOKEN SETTINGS exception: {e}')
        return JsonResponse({"status": False, "error": 602})
    
# Функция обработки запроса /api/get_payment_settings
@api_view(['GET'])
def api_get_payment_settings(request):
    print('GET TOKEN SETTINGS')
    try:
        account = DepositWithdrawSettings.objects.get(id=1)
        account_data = {
            'withdraw_min_limit': account.withdraw_min_limit,
            'deposit_min_limit_gold': account.deposit_min_limit_gold,
            'deposit_min_limit_silver': account.deposit_min_limit_silver,
            'paypal_account': account.paypal_account,
            'gold_transfer_rate': account.gold_transfer_rate
        }
        return JsonResponse({"status": True, "payment_settings": account_data})
    except Exception as e:
        print(f'GET TOKEN SETTINGS exception: {e}')
        return JsonResponse({"status": False, "error": 602})

# Функция обработки запроса /api/get_user_profile_data
@csrf_exempt
def api_get_user_profile_data(request):
    data = json.loads(request.body)
    print(f'GET USER PROFILE DATA: Data recieved successfully - {data}')
    player_id = data['user_id']
    token = data['token']
    user = User.objects.get(auth_token=token)
    player = Players.objects.get(id=player_id)
    formatted_date_string = player.reg_date.strftime("%Y-%m-%d")
    code_is_active = player.verification_code != None and player.verification_code != ''
    stats = get_player_stats(player_id)
    if user.username == player.django_name:
        player_info = {
            'owner': True,
            'nickname': player.nickname,
            'email': player.email,
            'reg_date': formatted_date_string,
            'phone': player.phone,
            'country': player.country,
            'silvercoin': player.silvercoin,
            'goldcoin': player.goldcoin,
            'bonuscoin': player.bonuscoin,
            'democoin': player.democoin,
            'reputation': player.reputation,
            'rating': stats.rate,
            'games_played_silver': stats.games_silver,
            'games_played_gold': stats.games_gold,
            'games_played_bonus': stats.games_bonus,
            'wins_silver': stats.wins_silver,
            'wins_gold': stats.wins_gold,
            'wins_bonus': stats.wins_bonus,
            'wallet': player.wallet,
            'email_is_verified': player.email_is_verified,
            'phone_is_verified': player.phone_is_verified,
            'referal_code': player.referal_code,
            'active_table': player.active_table,
            'verification_code': code_is_active,
            'verification_time': player.verification_time + 3600,
            'verification_try': player.verification_try
        }
        return JsonResponse(player_info, safe=False)
    else:
        player_info = {
            'owner': False,
            'nickname': player.nickname,
            'reg_date': formatted_date_string,
            'country': player.country,
            'reputation': player.reputation,
            'rating': stats.rate,
            'games_played_silver': stats.games_silver,
            'games_played_gold': stats.games_gold,
            'games_played_bonus': stats.games_bonus,
            'wins_silver': stats.wins_silver,
            'wins_gold': stats.wins_gold,
            'wins_bonus': stats.wins_bonus
        }
        print(f'GET USER PROFILE DATA response - {player_info}')
        return JsonResponse(player_info, safe=False)

def get_player_stats(user_id):
    try:
        player_stats = PlayersStats.objects.get(user_id=user_id)
    except PlayersStats.DoesNotExist:
        player_stats = PlayersStats.objects.create(user_id=user_id)
        player_stats.games_log = []
        player_stats.save()    
    return player_stats

# Функция обработки запроса /api/change_user_nickname
@csrf_exempt
def api_change_user_nickname(request):
    data = json.loads(request.body)
    print(f'CHANGE USER NICKNAME DATA: Data recieved successfully - {data}')
    new_nickname = data['new_nickname']
    player_id = data['user_id']
    token = data['token']
    user = User.objects.get(auth_token=token)
    player = Players.objects.get(id=player_id)    
    if user.username == player.django_name:
        if Players.objects.filter(nickname=new_nickname).exists():
            return JsonResponse({'result': False, 'message': 'User nickname already exists', 'code': 460})
        elif not len(new_nickname) in range(5, 51):
            return JsonResponse({'result': False, 'message': 'User nickname already exists', 'code': 464})
        else:
            player.nickname = new_nickname
            player.save()
            print(f'CHANGE USER NICKNAME: User nickname changed successfully')
            return JsonResponse({'result': True, 'message': 'User nickname changed successfully', 'code': 200})
    else:
        print(f'CHANGE USER NICKNAME: User nickname change error')
        return JsonResponse({'result': False, 'message': 'User nickname already exists', 'code': 0})
    
# Функция обработки запроса /api/change_user_email
@csrf_exempt
def api_change_user_email(request):
    data = json.loads(request.body)
    print(f'CHANGE USER NICKNAME DATA: Data recieved successfully - {data}')
    new_email = data['new_email']
    player_id = data['user_id']
    token = data['token']
    user = User.objects.get(auth_token=token)
    player = Players.objects.get(id=player_id)    
    if user.username == player.django_name:
        if Players.objects.filter(nickname=new_email).exists():
            return JsonResponse({'result': False, 'message': 'User nickname already exists', 'code': 461})
        else:
            player.email = new_email
            player.save()
            print(f'CHANGE USER NICKNAME: User nickname changed successfully')
            return JsonResponse({'result': True, 'message': 'User nickname changed successfully', 'code': 200})
    else:
        print(f'CHANGE USER NICKNAME: User nickname change error')
        return JsonResponse({'result': False, 'message': 'User nickname already exists', 'code': 0})
    
# Функция обработки запроса /api/change_user_phone
@csrf_exempt
def api_change_user_phone(request):
    data = json.loads(request.body)
    print(f'CHANGE USER PHONE DATA: Data recieved successfully - {data}')
    new_phone = phone_format(data['new_phone'])
    player_id = data['user_id']
    token = data['token']
    user = User.objects.get(auth_token=token)
    player = Players.objects.get(id=player_id)
    if (user.username == player.django_name) and is_phone_correct(new_phone):
        if Players.objects.filter(phone=new_phone).exists():
            return JsonResponse({'result': False, 'message': 'User phone number already exists', 'code': 461})
        else:
            player.phone = new_phone
            player.save()
            print(f'CHANGE USER PHONE: User phone changed successfully')
            return JsonResponse({'result': True, 'message': 'User phone number changed successfully', 'code': 200})
    else:
        print(f'CHANGE USER PHONE: User phone change error')
        return JsonResponse({'result': False, 'message': 'User phone change error', 'code': 0})

def phone_format(data: str) -> str:
    """Форматирует строку телефонного номера, оставляя только цифры и символ '+'."""
    return ''.join(filter(lambda x: x.isdigit() or x == '+', data))

def is_phone_correct(data: str) -> bool:
    """Проверяет соответствие строки формату телефонного номера."""    
    if not data.startswith('+'):
        return False        
    digits = data[1:]
    if not digits.isdigit():
        return False
    if not 9 <= len(digits) <= 15:
        return False    
    return True

# Функция обработки запроса /api/change_user_country
@csrf_exempt
def api_change_user_country(request):
    data = json.loads(request.body)
    print(f'CHANGE USER COUNTRY DATA: Data recieved successfully - {data}')
    new_country = data['new_country']
    player_id = data['user_id']
    token = data['token']
    user = User.objects.get(auth_token=token)
    player = Players.objects.get(id=player_id)
    if (user.username == player.django_name):
        player.country = new_country
        player.save()
        print(f'CHANGE USER COUNTRY: User country changed successfully')
        return JsonResponse({'result': True, 'message': 'User country changed successfully', 'code': 200})
    else:
        print(f'CHANGE USER COUNTRY: User phone change error')
        return JsonResponse({'result': False, 'message': 'User country change error', 'code': 0})

@api_view(['GET'])
def api_get_user_review_data(request, userID):
    try:
        player = Players.objects.get(id=userID)
        try:
            player_data = PlayersData.objects.get(user_id=userID)
            comments_array = player_data.comments
        except:
            response_data = {"username": player.nickname, "comments": []
            }
            return JsonResponse(response_data)
        print(f'API GET USER REVIEW DATA - {comments_array}')
        response_data = {
            "username": player.nickname,
            "comments": comments_array
        }
        for comment in comments_array:
            author_data = Players.objects.get(id=comment['author'])
            comment['author_nickname'] = author_data.nickname        
        return JsonResponse(response_data)
    except:
        return JsonResponse({'result': False, 'message': 'User country change error', 'code': 0})
    
@csrf_exempt
def api_get_user_history_data(request):
    print(f'GET USER HISTORY DATA: Data recieved successfully - Start')
    try:
        data = json.loads(request.body)
        print(f'GET USER HISTORY DATA: Data recieved successfully - {data}')
        player_id = data['user_id']
        token = data['token']
        user = User.objects.get(auth_token=token)
        player = Players.objects.get(id=player_id)        
        if user.username == player.django_name:
            player_games = get_player_games_history(player.id)
            response_data = {
                "result": True,
                "games": player_games
                }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'result': False, 'message': 'User getting games history error', 'code': 0})            
    except:
        return JsonResponse({'result': False, 'message': 'User getting games history error', 'code': 0})

# Функция обработки запроса /api/create_ref_code
@csrf_exempt
def api_create_ref_code(request):
    data = json.loads(request.body)
    print(f'CREATE REF CODE DATA: Data recieved successfully - {data}')    
    player_id = data['user_id']
    token = data['token']
    user = User.objects.get(auth_token=token)
    player = Players.objects.get(id=player_id)
    if (user.username == player.django_name):
        if player.email_is_verified or (player.wallet != None and player.wallet != ''):
            print(f'CREATE REF CODE: User referal code created successfully')
            if create_ref_code(player.id):
                return JsonResponse({'result': True, 'message': 'User referal code created successfully', 'code': 200})
            else:
                return JsonResponse({'result': False, 'message': 'Player with this ID not found', 'code': 0})
        else:
            print(f'CREATE REF CODE: User has not confirmed email!!!')
            return JsonResponse({'result': False, 'message': 'User has not confirmed email!!!', 'code': 467})
    else:
        print(f'CREATE REF CODE: User phone change error')
        return JsonResponse({'result': False, 'message': 'User referal code creation error', 'code': 0})
    

def generate_unique_ref_code():
    """
    Генерирует уникальный реферальный код.
    """
    length = 8
    characters = string.ascii_letters + string.digits
    while True:
        ref_code = ''.join(random.choice(characters) for i in range(length))
        if not Players.objects.filter(referal_code=ref_code).exists():
            return ref_code

def create_ref_code(player_id):
    try:
        player = Players.objects.get(id=player_id)
        nickname = player.nickname
        # Удаление недопустимых символов из никнейма
        valid_characters = string.ascii_letters + string.digits
        nickname = ''.join(char for char in nickname if char in valid_characters)        
        # Генерация реферального кода на основе никнейма
        ref_code = nickname.lower()[:8]  # Предполагаемая длина кода - 8 символов
        # Проверка уникальности реферального кода
        while True:
            try:
                existing_player = Players.objects.get(referal_code=ref_code)
                if existing_player.id == player_id:
                    break  # Код уже принадлежит этому игроку, выходим из цикла
                # Код уже занят, нужно сгенерировать новый
                ref_code += random.choice(string.ascii_letters + string.digits)
            except ObjectDoesNotExist:
                # Код уникален
                break
        # Сохранение уникального реферального кода в объект игрока
        print(f'Unique Ref code is: {ref_code}')    
        player.referal_code = ref_code
        player.save()
        return True
    except Players.DoesNotExist:
        print("Player with this ID not found")
        return False

# Функция обработки запроса /api/user_confirm_email - получение запроса верификации адреса и отправка кода
@csrf_exempt
def user_confirm_email(request):
    try:
        data = json.loads(request.body)
        player_id = data['user_id']
        token = data['token']
        user = User.objects.get(auth_token=token)
        player = Players.objects.get(id=player_id)        
        if user.username != player.django_name:
            return JsonResponse({'result': False, 'message': 'CONFIRM EMAIL: User authentifacation error', 'code': 0})        
        # Получение настроек почтового сервера из базы данных
        print(f'USER CONFIRM EMAIL ----------------- {data}')
        mail_server_settings = MailServerSettings.objects.first()  # Получаем первый объект настроек, но лучше сделать более точный запрос
    
        if mail_server_settings:
            current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
            unix_time = int(current_time.timestamp())
            generated_code = str(random.randint(0, 999999))        
            generated_code = generated_code.zfill(6)
            player.verification_code = generated_code
            player.verification_time = unix_time
            player.verification_try = 5
            player.save()
            # Формирование письма
            subject = mail_server_settings.mail_subject
            message = mail_server_settings.mail_text_before + generated_code + mail_server_settings.mail_text_after
            sender_email = mail_server_settings.username  # Ваш адрес электронной почты
            recipient_list = [mail_server_settings.admin_mail, player.email]  # Список адресов получателей
            print(f'MAIL SERVER PARAMS: {mail_server_settings}')
            try:
                connection = get_connection(
                    host=mail_server_settings.host,
                    port=mail_server_settings.port,
                    username=mail_server_settings.username,
                    password=mail_server_settings.password,
                    use_ssl=mail_server_settings.use_ssl,
                    use_tls=mail_server_settings.use_tls,
                )
            except:
                return JsonResponse({'result': False, 'message': 'User email confirming error', 'code': 0})
            try:
                send_mail(
                    subject=subject,                    
                    from_email=sender_email,
                    recipient_list=recipient_list,
                    fail_silently=False,
                    html_message=message,
                    message='',
                    connection=connection
                    )
                print('SENDING MAIL OK')
                return JsonResponse({'result': True, 'message': 'User email confirmed successfully', 'code': 468})
            except Exception as e:
                print(f'SENDING MAIL FAILED {e}')
                return JsonResponse({'result': False, 'message': 'User email confirming error', 'code': 0})
        else:
            return JsonResponse({'result': False, 'message': 'User email confirming error', 'code': 0})
    except Exception as e:
        print(f'USER CONFIRM EMAIL ERROR: {e}')
        return JsonResponse({'result': False, 'message': 'User email confirming error', 'code': 0})
    
# Функция обработки запроса /api/user_confirm_code
@csrf_exempt
def user_confirm_code(request):
    try:
        data = json.loads(request.body)
        player_id = data['user_id']
        token = data['token']
        code = data['code']
        user = User.objects.get(auth_token=token)
        player = Players.objects.get(id=player_id)        
        if user.username != player.django_name:
            return JsonResponse({'result': False, 'message': 'CONFIRM EMAIL witn CODE: User authentifacation error', 'code': 0})
        if player.verification_code == None or player.verification_code == '':
            return JsonResponse({'result': False, 'message': 'CONFIRM EMAIL witn CODE: User authentifacation error', 'code': 0})        
        print(f'USER CONFIRM CODE: Player {player.nickname} sending code {code}')
        if code != player.verification_code:
            if player.verification_try > 1:
                player.verification_try -= 1
                player.save()
                return JsonResponse({'result': False, 'message': 'User verification code is wrong', 'code': 471})
            else:
                player.verification_try = 0
                player.verification_code = None
                player.verification_time = 0
                player.save()
                return JsonResponse({'result': False, 'message': 'User verification code is wrong', 'code': 472})
        else:
            player.email_is_verified = True
            player.verification_code = None
            player.verification_time = 0
            player.verification_try = 0
            player.save()
            return JsonResponse({'result': True, 'message': 'User email confirmed successfully', 'code': 473})        
    except Exception as e:
        print(f'USER CONFIRM EMAIL ERROR: {e}')
        return JsonResponse({'result': False, 'message': 'User virification code error', 'code': 0})
    
# Функция обработки запроса /api/user_deposit_demo
@csrf_exempt
def user_deposit_demo(request):
    try:
        data = json.loads(request.body)
        player_id = data['user_id']
        token = data['token']        
        user = User.objects.get(auth_token=token)
        player = Players.objects.get(id=player_id)        
        if user.username != player.django_name:
            return JsonResponse({'result': False, 'message': 'USER DEPOSIT DEMOCOIN: User authentifacation error', 'code': 0})        
        if player.democoin >= 1000:
            return JsonResponse({'result': False, 'message': 'USER DEPOSIT DEMOCOIN: - not necessary', 'code': 475})
        else:            
            player.democoin += 1000
            player.save()
            try:
                player_data = get_player_data(player_id)
                print(f'PLAYERS DATA is {player_data}')
                current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
                unix_time = int(current_time.timestamp())
                action = {
                    "date": unix_time,
                    "coin": "freecoin",
                    "action": "deposit",
                    "value": 1000,
                    "method": "self"
                }
                player_data.coin_activity.append(action)
                player_data.history_free.append(action)
                player_data.save()
            except Exception as e:
                print(f'USER DEPOSIT FREE COIN ERROR - players data: {e}')                
            return JsonResponse({'result': True, 'message': 'USER DEPOSIT DEMOCOIN: - OK', 'code': 476})
    except Exception as e:
        print(f'USER DEPOSIT FREE COIN ERROR: {e}')
        return JsonResponse({'result': False, 'message': 'USER DEPOSIT DEMOCOIN: unkmown error', 'code': 0})
    
# Функция обработки запроса /api/user_deposit_gold
@csrf_exempt
def user_deposit_gold(request):
    try:
        data = json.loads(request.body)
        print(f'USER DEPOSIT GOLD: incoming data - {data}')
        player_id = data['user_id']
        token = data['token']        
        gold_value = data['gold_value']
        transaction_hash = data['transaction_hash']
        ip_address = data['ip_address']
        player = Players.objects.get(id=player_id)
        token_settings = TokenSettings.objects.get(id=1)
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        try:            
            transaction_data = get_transaction_data(transaction_hash)            
            token_value = int(math.floor(transaction_data['amount'] / 10**18))            
            if transaction_data['status'] and transaction_data['from'].lower() == player.wallet.lower() and transaction_data['to'].lower() == token_settings.host_wallet.lower() and transaction_data['contract'].lower() == token_settings.contract.lower() and token_value == gold_value:
                try:
                    transaction_log = TransactionsLog.objects.get(transaction_hash=transaction_hash)
                    transaction_error = TransactionsError(
                        date = current_time,
                        user_id = player_id,
                        sender = player.wallet,
                        transaction_hash = transaction_hash,
                        amount = gold_value,
                        ip_address = ip_address,
                        type = 1, #Goldcoin
                        message = 'USER DEPOSIT GOLDCOIN: Transaction dublicated'
                    )
                    transaction_error.save()
                    return JsonResponse({'status': False, 'message': 'USER DEPOSIT GOLDCOIN: transaction already exists', 'error': 483})
                except Exception as transaction_not_found:
                    print(f'USER DEPOSIT GOLD: # 6 - Except: {transaction_not_found}')
                    player.goldcoin += gold_value
                    player.save()                    
                    player_data = get_player_data(player.id)
                    action = {
                        "date": unix_time,
                        "coin": "goldcoin",
                        "action": "deposit",
                        "value": gold_value,
                        "method": "self",
                        "transaction_hash": transaction_hash,
                        "ip_address": ip_address
                    }
                    player_data.coin_activity.append(action)
                    player_data.history_gold.append(action)
                    player_data.save()                    
                    transaction_log = TransactionsLog(
                        transaction_hash = transaction_hash,
                        sender = transaction_data['from'],
                        recipient = transaction_data['to'],
                        date = current_time,
                        contract = transaction_data['contract'],
                        amount = token_value
                    )
                    transaction_log.save()
                    
                    try:
                        referer = Players.objects.get(id=player.referer_id)
                        if referer:
                            ref_data = get_player_data(referer.id)
                            ref_data.ref_bonus += gold_value
                            ref_action = {
                                "date": unix_time,
                                "coin": "bonuscoin",
                                "action": "deposit",
                                "value": gold_value,
                                "method": "referal",
                                "transaction_hash": transaction_hash
                            }
                            ref_data.coin_activity.append(ref_action)
                            ref_data.history_bonus.append(ref_action)
                            ref_data.save()
                            print('Referer got bonuscoins!')
                    except:
                        print('Referer not found!')
                        pass
                    return JsonResponse({'status': True, 'message': 'USER DEPOSIT GOLDCOIN: - OK', 'code': 482})
            else:
                transaction_error = TransactionsError(
                    date = current_time,
                    user_id = player_id,
                    sender = player.wallet,
                    transaction_hash = transaction_hash,
                    amount = gold_value,
                    ip_address = ip_address,
                    type = 1, #Goldcoin
                    message = 'USER DEPOSIT GOLDCOIN: Transaction not verified'
                )
                transaction_error.save()
                return JsonResponse({'status': False, 'message': 'USER DEPOSIT GOLDCOIN: Transaction not verified', 'error': 484})        
        except Exception as e:
            print(f'USER DEPOSIT GOLDCOIN ERROR - players data: {e}')
            error_message = str(e)
            transaction_error = TransactionsError(
                date = current_time,
                user_id = player_id,
                sender = player.wallet,
                transaction_hash = transaction_hash,
                amount = gold_value,
                ip_address = ip_address,
                type = 1, #Goldcoin
                message = 'USER DEPOSIT GOLDCOIN: Transaction not found - ' + error_message
            )
            transaction_error.save()
            return JsonResponse({'status': False, 'message': 'USER DEPOSIT GOLDCOIN: Transaction not found', 'error': 484})
    except Exception as e:
        print(f'USER DEPOSIT GOLDCOIN ERROR: {e}')
        error_message = str(e)
        transaction_error = TransactionsError(
            date = current_time,
            user_id = player_id,
            sender = player.wallet,
            transaction_hash = transaction_hash,
            amount = gold_value,
            ip_address = ip_address,
            type = 1, #Goldcoin
            message = 'USER DEPOSIT GOLDCOIN: unkmown error - ' + error_message
        )
        transaction_error.save()
        return JsonResponse({'status': False, 'message': 'USER DEPOSIT GOLDCOIN: unkmown error', 'error': 484})
"""
# Получение данных о транзакции по ее хэшу
def get_transaction_data(transaction_hash):
    try:
        transaction = web3.eth.get_transaction(transaction_hash)
        print('GET TRANSACTIONS: transaction response successfully...')
        try:
            token_settings = TokenSettings.objects.get(id=1)
            abi = token_settings.abi            
            decoded_input = web3.eth.contract(abi=abi).decode_function_input(transaction['input'])
            print('GET TRANSACTIONS: transaction decoding successfully...')
            result = decoded_input[1]
            transaction_data = {
                'from': transaction['from'],
                'to': result['recipient'],
                'amount': result['amount'],
                'contract': transaction['to'],
                'status': transaction['blockHash'] is not None
            }
            return transaction_data
        except Exception as e:
            print(f'GET TRANSACTION DATA ERROR 2: {e}')
            return None
    except Exception as e:
        print(f'GET TRANSACTION DATA ERROR 1: {e}')
        return None
"""

# Функция обработки запроса /api/user_get_airdrop_coins
@csrf_exempt
def user_get_airdrop_coins(request):
    try:
        data = json.loads(request.body)
        print(f'USER GET AIRDROP COINS: incoming data - {data}')
        player_id = data['user_id']
        token = data['token']
        user = User.objects.get(auth_token=token)
        player = Players.objects.get(id=player_id)        
        if user.username != player.django_name:
            return JsonResponse({'status': False, 'message': 'User get airdropcoin error: logging token is not confirmed', 'error': 0})
        else:
            player_data = get_player_data(player_id)
            if player_data.airdrop_gold == 0 and player_data.airdrop_silver == 0 and player_data.airdrop_bonus == 0 and player_data.ref_silver == 0 and player_data.ref_gold == 0 and player_data.ref_bonus == 0:
                print(f'USER GET AIRDROP COINS: incoming data - if')
                return JsonResponse({'status': False, 'message': 'User get airdropcoin error: no coins for bonus or airdrop', 'error': 485})
            else:
                print(f'USER GET AIRDROP COINS: incoming data - else')
                airdrop = [0, 0, 0]
                referal = [0, 0, 0]
                if player_data.airdrop_silver > 0:
                    airdrop[0] = player_data.airdrop_silver
                if player_data.airdrop_gold > 0:
                    airdrop[1] = player_data.airdrop_gold
                if player_data.airdrop_bonus > 0:
                    airdrop[2] = player_data.airdrop_bonus
                if player_data.ref_silver > 0:
                    referal[0] = player_data.ref_silver
                if player_data.ref_gold > 0:
                    referal[1] = player_data.ref_gold
                if player_data.ref_bonus > 0:
                    referal[2] = player_data.ref_bonus
                player.silvercoin += player_data.airdrop_silver + player_data.ref_silver
                player_data.airdrop_silver = 0
                player_data.ref_silver = 0
                player.goldcoin += player_data.airdrop_gold + player_data.ref_gold
                player_data.airdrop_gold = 0 
                player_data.ref_gold = 0
                player.bonuscoin += player_data.airdrop_bonus + player_data.ref_bonus
                player_data.airdrop_bonus = 0 
                player_data.ref_bonus = 0
                player.save()
                player_data.save()
                return JsonResponse({'status': True, 'message': 'User get airdropcoin error: unexpected error', 'code': 1001, 'airdrop': airdrop, 'referal': referal})
    except Exception as e:
        print(f'USER GET AIRDROP COINS: Exception: {e}')
        return JsonResponse({'status': False, 'message': 'User get airdropcoin error: unexpected error', 'error': 0})
    

# Функция обработки запроса /api/user_withdraw_gold
@csrf_exempt
def user_withdraw_gold(request):
    try:
        data = json.loads(request.body)
        print(f'USER WITHDRAW GOLD: incoming data - {data}')
        player_id = data['user_id']
        token = data['token']
        user_address = data['user_address']
        ip_address = data['ip_address']
        gold_value = data['gold_value']
        user = User.objects.get(auth_token=token)
        player = Players.objects.get(id=player_id)
        dw_settings = DepositWithdrawSettings.objects.get(id=1)
        if user.username != player.django_name:
            return JsonResponse({'status': False, 'message': 'User withdraw goldcoin error: logging token is not confirmed', 'error': 0})
        else:
            if player.wallet.lower() != user_address.lower():
                return JsonResponse({'status': False, 'message': 'Metamask signature incorrect', 'error': 606})
            is_valid = check_password(data['signature'], player.password)
            if not is_valid:
                return JsonResponse({'status': False, 'message': 'Metamask signature incorrect', 'error': 605})
            if gold_value > player.goldcoin or gold_value < dw_settings.withdraw_min_limit:
                return JsonResponse({'status': False, 'message': 'Metamask signature incorrect', 'error': 480})
            player_data = get_player_data(player_id)
            current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
            unix_time = int(current_time.timestamp())
            withdraw_log = WithdrawsGold(
                date_request = current_time,
                user_id = player_id,
                user_address = player.wallet,            
                amount_gold = gold_value,
                ip_address = ip_address,
                amount_token = (dw_settings.gold_transfer_rate / 100) * gold_value
            )
            withdraw_log.save()
            action = {
                "date": unix_time,
                "coin": "goldcoin",
                "action": "withdraw_request",
                "value": gold_value,
                "method": "referal",
                "withdraw_id": withdraw_log.id
            }
            player_data.coin_activity.append(action)
            player_data.history_gold.append(action)
            player_data.save()
            player.goldcoin -= gold_value
            player.save()

            mail_server_settings = MailServerSettings.objects.first()  # Получаем первый объект настроек, но лучше сделать более точный запрос
    
            if mail_server_settings:
                # Формирование письма
                subject = f'AZI Online - Withdraw request #{withdraw_log.id}'
                message = f'<p> User {player_id} wants to withdraw <b>{withdraw_log.amount_token}</b> tokens.</p><hr>Wallet address is <b>{player.wallet}</b><br>Withdraw ID is <b>{withdraw_log.id}</b>'
                sender_email = mail_server_settings.username  # Ваш адрес электронной почты
                recipient_list = [mail_server_settings.moderator_mail]  # Список адресов получателей                
                try:
                    connection = get_connection(
                        host=mail_server_settings.host,
                        port=mail_server_settings.port,
                        username=mail_server_settings.username,
                        password=mail_server_settings.password,
                        use_ssl=mail_server_settings.use_ssl,
                        use_tls=mail_server_settings.use_tls,
                    )
                except Exception as e:
                    print(f'USER WINDRAW GOLD - SENDING MAIL CONNECTION FAILED {e}')
                try:
                    send_mail(
                        subject=subject,                    
                        from_email=sender_email,
                        recipient_list=recipient_list,
                        fail_silently=False,
                        html_message=message,
                        message='',
                        connection=connection
                        )
                    print('USER WINDRAW GOLD - SENDING MAIL OK')                    
                except Exception as e:
                    print(f'USER WINDRAW GOLD - SENDING MAIL FAILED {e}')                    
            else:
                print('USER WINDRAW GOLD - mail settings error')
                pass
            return JsonResponse({'status': True, 'message': 'User withdraw goldcoin: successfully', 'code': 607})
    except Exception as e:
        print(f'USER WITHDRAW GOLD - Exception : {e}')
        return JsonResponse({'status': False, 'message': 'User withdraw goldcoin error: unknown error', 'error': 0})
    

# Функция обработки запроса /api/user_deposit_silver_bnb
@csrf_exempt
def user_deposit_silver_bnb(request):
    try:
        data = json.loads(request.body)
        print(f'USER DEPOSIT SILVER BNB: incoming data - {data}')
        player_id = data['user_id']
        token = data['token']        
        bnb_value = data['bnb_value']
        transaction_hash = data['transaction_hash']
        ip_address = data['ip_address']
        player = Players.objects.get(id=player_id)
        token_settings = TokenSettings.objects.get(id=1)
        payment_settings = DepositWithdrawSettings.objects.get(id=1)
        rate_bnb = payment_settings.silver_bnb_rate
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        try:            
            transaction_data = get_transaction_data_bnb(transaction_hash)            
            blockchain_bnb_value = transaction_data['amount'] / 10**18
            print(f'USER DEPOSIT SILVER: {bnb_value} vs {blockchain_bnb_value} | {type(bnb_value)} vs {type(blockchain_bnb_value)}')
            if transaction_data['status'] and transaction_data['from'].lower() == player.wallet.lower() and transaction_data['to'].lower() == token_settings.host_wallet.lower() and transaction_data['chain_id'] == 56 and bnb_value == blockchain_bnb_value:
                try:
                    transaction_log = TransactionsLog.objects.get(transaction_hash=transaction_hash)
                    transaction_error = TransactionsError(
                        date = current_time,
                        user_id = player_id,
                        sender = player.wallet,
                        transaction_hash = transaction_hash,
                        amount = bnb_value,
                        ip_address = ip_address,
                        type = 0, #Silvercoin
                        message = 'USER DEPOSIT SILVERCOIN (BNB): Transaction dublicated'
                    )
                    transaction_error.save()
                    return JsonResponse({'status': False, 'message': 'USER DEPOSIT SILVERCOIN (BNB): transaction already exists', 'error': 483})
                except Exception as transaction_not_found:
                    print(f'USER DEPOSIT GOLD: # 6 - Except: {transaction_not_found}')
                    player.silvercoin += math.floor(bnb_value * rate_bnb)
                    player.save()                    
                    player_data = get_player_data(player.id)
                    action = {
                        "date": unix_time,
                        "coin": "silvercoin",
                        "action": "deposit",
                        "value": math.floor(bnb_value * rate_bnb),
                        "method": "self",
                        "transaction_hash": transaction_hash,
                        "ip_address": ip_address
                    }
                    player_data.coin_activity.append(action)
                    player_data.history_silver.append(action)
                    player_data.save()                    
                    transaction_log = TransactionsLog(
                        transaction_hash = transaction_hash,
                        sender = transaction_data['from'],
                        recipient = transaction_data['to'],
                        date = current_time,
                        contract = 'bnb native',
                        amount = bnb_value
                    )
                    transaction_log.save()
                    
                    try:
                        referer = Players.objects.get(id=player.referer_id)
                        if referer:
                            ref_data = get_player_data(referer.id)
                            ref_data.ref_silver += math.floor(bnb_value * rate_bnb / 10)
                            ref_data.ref_bonus += math.floor(bnb_value * rate_bnb / 100)
                            ref_action_silver = {
                                "date": unix_time,
                                "coin": "silvercoin",
                                "action": "deposit",
                                "value": math.floor(bnb_value * rate_bnb / 10),
                                "method": "referal",
                                "transaction_hash": transaction_hash
                            }
                            ref_action_bonus = {
                                "date": unix_time,
                                "coin": "bonuscoin",
                                "action": "deposit",
                                "value": math.floor(bnb_value * rate_bnb / 100),
                                "method": "referal",
                                "transaction_hash": transaction_hash
                            }
                            ref_data.coin_activity.append(ref_action_silver)
                            ref_data.coin_activity.append(ref_action_bonus)
                            ref_data.history_silver.append(ref_action_silver)
                            ref_data.history_bonus.append(ref_action_bonus)
                            ref_data.save()
                            print('Referer got silvercoins!')
                    except:
                        print('Referer not found!')
                        pass
                    return JsonResponse({'status': True, 'message': 'USER DEPOSIT SILVERCOIN (BNB):', 'code': 482})
            else:
                transaction_error = TransactionsError(
                    date = current_time,
                    user_id = player_id,
                    sender = player.wallet,
                    transaction_hash = transaction_hash,
                    amount = bnb_value,
                    ip_address = ip_address,
                    type = 0, #Silvercoin
                    message = 'USER DEPOSIT SILVERCOIN (BNB): Transaction not verified'
                )
                transaction_error.save()
                return JsonResponse({'status': False, 'message': 'USER DEPOSIT SILVERCOIN (BNB): Transaction not verified', 'error': 484})        
        except Exception as e:
            print(f'USER DEPOSIT SILVERCOIN (BNB) ERROR - players data: {e}')
            error_message = str(e)
            transaction_error = TransactionsError(
                date = current_time,
                user_id = player_id,
                sender = player.wallet,
                transaction_hash = transaction_hash,
                amount = bnb_value,
                ip_address = ip_address,
                type = 0, #Silvercoin
                message = 'USER DEPOSIT SILVERCOIN (BNB): Transaction not found - ' + error_message
            )
            transaction_error.save()
            return JsonResponse({'status': False, 'message': 'USER DEPOSIT SILVERCOIN (BNB): Transaction not found', 'error': 484})
    except Exception as e:
        print(f'USER DEPOSIT SILVERCOIN (BNB) ERROR: {e}')
        error_message = str(e)
        transaction_error = TransactionsError(
            date = current_time,
            user_id = player_id,
            sender = player.wallet,
            transaction_hash = transaction_hash,
            amount = bnb_value,
            ip_address = ip_address,
            type = 0, #Silvercoin
            message = 'USER DEPOSIT SILVERCOIN (BNB): unkmown error - ' + error_message
        )
        transaction_error.save()
        return JsonResponse({'status': False, 'message': 'USER DEPOSIT SILVERCOIN (BNB): unkmown error', 'error': 484})

"""
def get_transaction_data_bnb(transaction_hash):    
    print(f'CHECKER - GET TRANSACTION DATA (BNB) - {transaction_hash} Type of token - {type(transaction_hash)}')
    # Получение данных о транзакции по ее хэшу
    try: 
        transaction = web3.eth.get_transaction(transaction_hash)
        transaction_data = {
            'from': transaction['from'],
            'to': transaction['to'],
            'amount': transaction['value'],
            'chain_id': transaction['chainId'],
            'status': transaction['blockHash'] is not None
        }
        return transaction_data
    except Exception as e:
        print(f'CHECKER - Error getting transaction data: {e}')
        return None
""" 


# Функция обработки запроса /api/user_deposit_silver_usdt
@csrf_exempt
def user_deposit_silver_usdt(request):
    try:
        data = json.loads(request.body)
        print(f'USER DEPOSIT SILVER: incoming data - {data}')
        player_id = data['user_id']
        token = data['token']        
        usdt_value = data['usdt_value']
        transaction_hash = data['transaction_hash']
        ip_address = data['ip_address']
        player = Players.objects.get(id=player_id)
        token_settings = TokenSettings.objects.get(id=1)
        payment_settings = DepositWithdrawSettings.objects.get(id=1)
        rate_usd = payment_settings.silver_usd_rate
        usdt_contract = '0x55d398326f99059fF775485246999027B3197955'
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        try:            
            transaction_data = get_transaction_data_usdt(transaction_hash)            
            token_value = int(math.floor(transaction_data['amount'] / 10**18))            
            if transaction_data['status'] and transaction_data['from'].lower() == player.wallet.lower() and transaction_data['to'].lower() == token_settings.host_wallet.lower() and transaction_data['contract'].lower() == usdt_contract.lower() and token_value == usdt_value:
                try:
                    transaction_log = TransactionsLog.objects.get(transaction_hash=transaction_hash)
                    transaction_error = TransactionsError(
                        date = current_time,
                        user_id = player_id,
                        sender = player.wallet,
                        transaction_hash = transaction_hash,
                        amount = usdt_value,
                        ip_address = ip_address,
                        type = 0, #Silvercoin
                        message = 'USER DEPOSIT SILVERCOIN (USDT): Transaction dublicated'
                    )
                    transaction_error.save()
                    return JsonResponse({'status': False, 'message': 'USER DEPOSIT SILVERCOIN (USDT): transaction already exists', 'error': 483})
                except Exception as transaction_not_found:                    
                    player.silvercoin += usdt_value * rate_usd
                    player.save()                    
                    player_data = get_player_data(player.id)
                    action = {
                        "date": unix_time,
                        "coin": "silvercoin",
                        "action": "deposit",
                        "value": usdt_value * rate_usd,
                        "method": "self",
                        "transaction_hash": transaction_hash,
                        "ip_address": ip_address
                    }
                    player_data.coin_activity.append(action)
                    player_data.history_silver.append(action)
                    player_data.save()                    
                    transaction_log = TransactionsLog(
                        transaction_hash = transaction_hash,
                        sender = transaction_data['from'],
                        recipient = transaction_data['to'],
                        date = current_time,
                        contract = transaction_data['contract'],
                        amount = token_value
                    )
                    transaction_log.save()
                    
                    try:
                        referer = Players.objects.get(id=player.referer_id)
                        if referer:
                            ref_data = get_player_data(referer.id)
                            ref_data.ref_silver += math.floor(usdt_value * rate_usd / 10)
                            ref_data.ref_bonus += math.floor(usdt_value * rate_usd / 100)
                            ref_action_silver = {
                                "date": unix_time,
                                "coin": "silvercoin",
                                "action": "deposit",
                                "value": math.floor(usdt_value * rate_usd / 10),
                                "method": "referal",
                                "transaction_hash": transaction_hash
                            }
                            ref_action_bonus = {
                                "date": unix_time,
                                "coin": "silvercoin",
                                "action": "deposit",
                                "value": math.floor(usdt_value * rate_usd / 100),
                                "method": "referal",
                                "transaction_hash": transaction_hash
                            }
                            ref_data.coin_activity.append(ref_action_silver)
                            ref_data.history_silver.append(ref_action_silver)
                            ref_data.coin_activity.append(ref_action_bonus)
                            ref_data.history_bonus.append(ref_action_bonus)
                            ref_data.save()
                            print('Referer got silvercoins!')
                    except:
                        print('Referer not found!')
                        pass
                    return JsonResponse({'status': True, 'message': 'USER DEPOSIT SILVERCOIN: - OK', 'code': 488})
            else:
                transaction_error = TransactionsError(
                    date = current_time,
                    user_id = player_id,
                    sender = player.wallet,
                    transaction_hash = transaction_hash,
                    amount = usdt_value,
                    ip_address = ip_address,
                    type = 0, #Silvercoin
                    message = 'USER DEPOSIT SILVERCOIN (USDT): Transaction not verified'
                )
                transaction_error.save()
                return JsonResponse({'status': False, 'message': 'USER DEPOSIT SILVERCOIN (USDT): Transaction not verified', 'error': 484})        
        except Exception as e:
            print(f'USER DEPOSIT SILVERCOIN (USDT) ERROR - players data: {e}')
            error_message = str(e)
            transaction_error = TransactionsError(
                date = current_time,
                user_id = player_id,
                sender = player.wallet,
                transaction_hash = transaction_hash,
                amount = usdt_value,
                ip_address = ip_address,
                type = 0, #Silvercoin
                message = 'USER DEPOSIT SILVERCOIN (USDT): Transaction not found - ' + error_message
            )
            transaction_error.save()
            return JsonResponse({'status': False, 'message': 'USER DEPOSIT SILVERCOIN: Transaction not found', 'error': 484})
    except Exception as e:
        print(f'USER DEPOSIT SILVERCOIN (USDT): {e}')
        error_message = str(e)
        transaction_error = TransactionsError(
            date = current_time,
            user_id = player_id,
            sender = player.wallet,
            transaction_hash = transaction_hash,
            amount = usdt_value,
            ip_address = ip_address,
            type = 0, #Silvrcoin
            message = 'USER DEPOSIT SILVERCOIN (USDT): unkmown error - ' + error_message
        )
        transaction_error.save()
        return JsonResponse({'status': False, 'message': 'USER DEPOSIT SILVERCOIN (USDT): unkmown error', 'error': 484})

"""
# Получение данных о транзакции по ее хэшу
def get_transaction_data_usdt(transaction_hash):
    try:
        transaction = web3.eth.get_transaction(transaction_hash)
        print('GET TRANSACTIONS: transaction response successfully...')
        try:
            abi = [{"inputs":[],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"spender","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":True,"inputs":[],"name":"_decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"_name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"_symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"getOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"}]
            decoded_input = web3.eth.contract(abi=abi).decode_function_input(transaction['input'])
            print('GET TRANSACTIONS: transaction decoding successfully...')
            result = decoded_input[1]
            transaction_data = {
                'from': transaction['from'],
                'to': result['recipient'],
                'amount': result['amount'],
                'contract': transaction['to'],
                'status': transaction['blockHash'] is not None
            }
            return transaction_data
        except Exception as e:
            print(f'GET TRANSACTION DATA ERROR 2: {e}')
            return None
    except Exception as e:
        print(f'GET TRANSACTION DATA ERROR 1: {e}')
        return None
"""
         
# Функция обработки запроса /api/user_deposit_silver_paypal
@csrf_exempt
def user_deposit_silver_paypal(request):
    try:
        data = json.loads(request.body)
        print(f'USER DEPOSIT SILVER PAYPAL: incoming data - {data}')
        player_id = data['user_id']
        token = data['token']                
        payment_id = data['payment_id']
        payment_value = data['payment_value']
        ip_address = data['ip_address']
        player = Players.objects.get(id=player_id)
        token_settings = TokenSettings.objects.get(id=1)
        payment_settings = DepositWithdrawSettings.objects.get(id=1)
        rate_usd = payment_settings.silver_usd_rate
        merchant_id = payment_settings.paypal_merchant_id
        #merchant_id = 'R8SMESA3ZFQMG'
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        payment = get_payment_detail(payment_id)
        if payment['status']:
            payment_data = payment['data']['purchase_units'][0]
            payment_value_str = payment_data['payments']['captures'][0]['amount']['value']
            payment_currency = payment_data['payments']['captures'][0]['amount']['currency_code']
            payment_id2 = payment_data['payments']['captures'][0]['id']
            payee_id = payment_data['payee']['merchant_id']
            payer_mail = payment['data']['payer']['email_address']
            payer_id = payment['data']['payer']['payer_id']
            print(f'Payment data: Player {player_id} paid {payment_value_str} {payment_currency} for {payee_id}. Payment ID is {payment_id2}, Payer ID is {payer_id} ({payer_mail})')
            
            if math.floor(payment_value) == math.floor(float(payment_value_str)) and merchant_id == payee_id:                
                print(f'OKAY LETS GO ----------------- {payment_value} = {payment_value_str}')
                try:
                    transaction_log = PaypalTransactionsLog.objects.get(transaction_id=payment_id, payment_id=payment_id2)
                    transaction_error = PaypalTransactionsError(
                        date = current_time,
                        transaction_id = payment_id,
                        user_id = player_id,
                        ip_address = ip_address,
                        type = 0, #Silvercoin
                        message = f'USER DEPOSIT SILVERCOIN (Paypal): Transaction dublicated - payment_is is {transaction_log.payment_id}'
                    )
                    transaction_error.save()
                    return JsonResponse({'status': False, 'message': 'USER DEPOSIT SILVERCOIN (USDT): transaction already exists', 'error': 483})
                except Exception as transaction_not_found:
                    player.silvercoin += payment_value * rate_usd
                    player.save()                    
                    player_data = get_player_data(player.id)
                    action = {
                        "date": unix_time,
                        "coin": "silvercoin",
                        "action": "deposit",
                        "value": payment_value * rate_usd,
                        "method": "self",
                        "transcation_id": payment_id,
                        "payment_id": payment_id2,
                        "ip_address": ip_address
                    }
                    player_data.coin_activity.append(action)
                    player_data.history_silver.append(action)
                    player_data.save()                    
                    transaction_log = PaypalTransactionsLog(
                        transaction_id = payment_id,
                        payment_id = payment_id2,
                        user_id = player_id,
                        payer_mail = payer_mail,
                        payer_id = payer_id,
                        date = current_time,
                        amount = payment_value
                    )
                    transaction_log.save()
                    
                    try:
                        referer = Players.objects.get(id=player.referer_id)
                        if referer:
                            ref_data = get_player_data(referer.id)
                            ref_data.ref_silver += math.floor(payment_value * rate_usd / 10)
                            ref_data.ref_bonus += math.floor(payment_value * rate_usd / 100)
                            ref_action_silver = {
                                "date": unix_time,
                                "coin": "silvercoin",
                                "action": "deposit",
                                "value": math.floor(payment_value * rate_usd / 10),
                                "method": "referal",
                                "transcation_id": payment_id,
                                "payment_id": payment_id2,
                            }
                            ref_action_bonus = {
                                "date": unix_time,
                                "coin": "silvercoin",
                                "action": "deposit",
                                "value": math.floor(payment_value * rate_usd / 100),
                                "method": "referal",
                                "transcation_id": payment_id,
                                "payment_id": payment_id2,
                            }
                            ref_data.coin_activity.append(ref_action_silver)
                            ref_data.history_silver.append(ref_action_silver)
                            ref_data.coin_activity.append(ref_action_bonus)
                            ref_data.history_bonus.append(ref_action_bonus)
                            ref_data.save()
                            print('Referer got silvercoins!')
                    except:
                        print('Referer not found!')
                        pass
                    return JsonResponse({'status': True, 'message': 'USER DEPOSIT SILVERCOIN: - OK', 'code': 488})
                    
            else:
                print(f'OKAY LETS GO ----------------- NOOOOOO {payment_value} <> {payment_value_str}')
                transaction_error = PaypalTransactionsError(
                    date = current_time,
                    transaction_id = payment_id,
                    user_id = player_id,
                    ip_address = ip_address,
                    type = 0, #Silvercoin
                    message = 'USER DEPOSIT SILVERCOIN (Paypal): Transaction not verified'
                )
                transaction_error.save()
                return JsonResponse({'status': False, 'message': 'USER DEPOSIT SILVERCOIN (USDT): Transaction not verified', 'error': 484})            
        else:
            return JsonResponse({'status': False, 'message': 'USER DEPOSIT SILVERCOIN (PAYPAL): unkmown error', 'error': 0})    
    except Exception as e:
        print(f'USER DEPOSIT SILVER PAYPAL: Exception Error - {e}')
        return JsonResponse({'status': False, 'message': 'USER DEPOSIT SILVERCOIN (PAYPAL): unkmown error', 'error': 0})
    

# Функция обработки запроса /api/get_payment_settings_silver
@api_view(['GET'])
def get_payment_settings_silver(request):
    print('GET PAYMENT SETTINGS SILVER')
    try:
        payment_settings = DepositWithdrawSettings.objects.get(id=1)
        settings = {
            'paypal_client_id': payment_settings.paypal_client_id,
            'silver_bnb_rate': payment_settings.silver_bnb_rate,
            'silver_usd_rate': payment_settings.silver_usd_rate,
        }
        return JsonResponse({"status": True, "settings": settings})
    except Exception as e:
        print(f'GET TOKEN SETTINGS exception: {e}')
        return JsonResponse({"status": False, "error": 602})

# Функция обработки запроса /api/get_toplist_silver    
@api_view(['GET'])
def api_get_toplist_data(request):
    print(f'GET TOPLIST DATA: Data recieved successfully - Start')
    try:

        players = PlayersStats.objects.annotate(
            total_games=F('games_silver') + F('games_gold') + F('games_bonus')
        ).order_by(
            '-rate', '-total_games', 'user_id'
        )

        export_list = []        
        pos = 1
        for player in players:
            pl = Players.objects.get(id=player.user_id)
            reg_date = pl.reg_date
            current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
            days_difference = current_time - reg_date
            days = days_difference.days
            export_player = {                
                'user_id': player.user_id,
                'pos': pos,
                'nickname': pl.nickname,
                'rating': player.rate,
                'played': player.games_silver + player.games_gold + player.games_bonus,
                'won': player.wins_silver + player.wins_gold + player.wins_bonus,
                'days': days
            }
            pos += 1
            export_list.append(export_player)
            if pos > 100:
                break
        response_data = {
                "result": True,
                "top_list": export_list
                }
        return JsonResponse(response_data)
    except Exception as e:
        print(f'GET TOPLIST DATA - Exception: {e}')
        return JsonResponse({'result': False, 'message': 'Toplist players getting error', 'code': 0})
    
# Функция обработки запроса /api/get_setttings
@api_view(['GET'])
def api_get_settings(request):
    print('API GET SETTINGS')
    try:
        payment_settings = DepositWithdrawSettings.objects.get(id=1)
        paypal_client_id = payment_settings.paypal_client_id
        mail_server_settings = MailServerSettings.objects.first()
        mail_server = mail_server_settings.user_mail_server
        client_url = mail_server_settings.app_client_url
        google_auth_client_id = mail_server_settings.google_auth_client_id
        data_to_send = {
            'result': True,
            'server_mail': mail_server,
            'paypal_client_id': paypal_client_id,
            'google_auth_client_id': google_auth_client_id,
            'code': 0,
            'app_client_url': client_url
        }
        return JsonResponse(data_to_send)
    except Exception as e:
        print(f'API GET SETTINGS - Exception: {e}')
        return JsonResponse({'result': False, 'message': 'Get settings data error', 'code': 0})


# Функция обработки запроса /api/user_password_reset - получение запроса сброса пароля и отправка кода
@csrf_exempt
def user_password_reset(request):    
    try:        
        data = json.loads(request.body)
        print(f'RESET PASSWORD - data {data}')
        email = data['email']
        ip_address = data['ip_address']
        try:
            bad_user = BlacklistIP.objects.get(ip_address=ip_address)
            print(f'PASSWORD RESET - Suspicious activity from IP {bad_user.ip_address}')
            return JsonResponse({'result': False, 'message': 'RESET PASSWORD - error: This user not found', 'code': 499})
        except BlacklistIP.DoesNotExist:
            print('PASSWORD RESET - User is not bad')
        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            return JsonResponse({'result': False, 'message': 'RESET PASSWORD - error: This user not found', 'code': 451})
        try:
            player = Players.objects.get(email=email)
        except Players.DoesNotExist:
            return JsonResponse({'result': False, 'message': 'RESET PASSWORD - error: This user not found', 'code': 451})

        user_greylist = get_user_greylist(ip_address)

        if player.email != player.django_name:
            return JsonResponse({'result': False, 'message': 'RESET PASSWORD - error: This user can not to reset password', 'code': 489})
        elif user.password is None or user.password == '':
            print(f'Password is {user.password}')
            return JsonResponse({'result': False, 'message': 'RESET PASSWORD - error: This user can not to reset password', 'code': 489})
        elif user_greylist.reset_try > 10:
            return JsonResponse({'result': False, 'message': 'RESET PASSWORD - error: Account blocked!!!', 'code': 499})
        else:
            mail_server_settings = MailServerSettings.objects.first()  # Получаем первый объект настроек, но лучше сделать более точный запрос
    
            if mail_server_settings:
                current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
                unix_time = int(current_time.timestamp())
                generated_code = str(random.randint(0, 999999))        
                generated_code = generated_code.zfill(6)
                player.reset_code = generated_code
                player.reset_time = unix_time
                player.reset_try = 3                
                player.save()
                user_greylist.reset_try += 1
                reset_log = {
                    "user_id": player.id,
                    "date": unix_time
                }
                user_greylist.log.append(reset_log)
                user_greylist.save()
                # Формирование письма
                subject = mail_server_settings.reset_subject
                message = mail_server_settings.reset_text_before + generated_code + mail_server_settings.reset_text_after
                sender_email = mail_server_settings.username  # Ваш адрес электронной почты
                recipient_list = [mail_server_settings.admin_mail, player.email]  # Список адресов получателей
                print(f'MAIL SERVER PARAMS: {mail_server_settings}')
                try:
                    connection = get_connection(
                        host=mail_server_settings.host,
                        port=mail_server_settings.port,
                        username=mail_server_settings.username,
                        password=mail_server_settings.password,
                        use_ssl=mail_server_settings.use_ssl,
                        use_tls=mail_server_settings.use_tls,
                    )
                except:
                    return JsonResponse({'result': False, 'message': 'User email confirming error', 'code': 0})
                try:
                    
                    send_mail(
                        subject=subject,                    
                        from_email=sender_email,
                        recipient_list=recipient_list,
                        fail_silently=False,
                        html_message=message,
                        message='',
                        connection=connection
                        )
                    print('SENDING MAIL OK')
                    
                    good_response = {
                        'result': True, 
                        'message': 'User reset password code created successfully', 
                        'code': 491,
                        'reset_time': player.reset_time + 3600,
                        'reset_try': player.reset_try
                    }
                    return JsonResponse(good_response)
                except Exception as e:
                    print(f'SENDING MAIL FAILED {e}')
                    return JsonResponse({'result': False, 'message': 'User reset password error', 'code': 0})
            else:
                return JsonResponse({'result': False, 'message': 'User reset password error', 'code': 0})

    except Exception as e:
        print(f'USER RESET PASSWORD ERROR: {e}')
        return JsonResponse({'result': False, 'message': 'User reset password error', 'code': 0})
    
@csrf_exempt
def user_password_reset_code(request):
    try:        
        data = json.loads(request.body)        
        email = data['email']
        ip_address = data['ip_address']
        reset_code = data['reset_code']
        print(f'USER PASSWORD RESET CODE: Code is {type(reset_code)}')
        player = Players.objects.get(email=email)
        if reset_code != player.reset_code:
            if player.reset_try > 1:
                player.reset_try -= 1
                player.save()
                return JsonResponse({'result': False, 'message': 'User reset code is wrong', 'code': 492, 'reset_try': player.reset_try})
            else:
                player.reset_try = 0
                player.reset_code = None
                player.reset_time = 0
                player.save()
                return JsonResponse({'result': False, 'message': 'User reset code is wrong', 'code': 493})
        else:            
            player.reset_try = 0
            player.reset_code = 'waiting'
            player.reset_time = 0
            player.save()
            good_response = {
                'result': True, 
                'message': 'User reset code confirmed successfully',
            }
            return JsonResponse(good_response)

    except Exception as e:
        print(f'USER PASWORD RESET CODE error: {e}')
        return JsonResponse({'result': False, 'message': 'User reset password error', 'code': 0})
    

@csrf_exempt
def user_password_reset_password(request):
    try:        
        data = json.loads(request.body)        
        email = data['email']
        ip_address = data['ip_address']
        new_password = data['password']        
        player = Players.objects.get(email=email)
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        if player.reset_code != 'waiting':
            bad_user = BlacklistIP.objects.create()
            bad_user.ip_address = ip_address
            bad_user.date = current_time
            bad_user.comment = 'Trying to change password withiot WAITING maarker in the Database'
            bad_user.save()
            return JsonResponse({'result': False, 'message': 'Are you really hacker?', 'code': 499})
        else:
            user_greylist = get_user_greylist(ip_address)
            user_greylist.reset_try = 0
            greylist_log = {
                "date": unix_time,
                "email": email,
                "action": "password reset"
            }
            user_greylist.log.append(greylist_log)
            user_greylist.save()

            player.reset_try = 0
            player.reset_code = ''
            player.reset_time = 0
            player.save()

            user = User.objects.get(username=email)
            user.set_password(new_password)
            user.save()
            good_response = {
                'result': True, 
                'message': 'User password was changed successfully',
                'code': 494
            }
            return JsonResponse(good_response)

    except Exception as e:
        print(f'USER PASWORD RESET CODE error: {e}')
        return JsonResponse({'result': False, 'message': 'User reset password error', 'code': 495})

def get_user_greylist(ip_address):
    try:
        user = GreylistIP.objects.get(ip_address=ip_address)
        return user
    except GreylistIP.DoesNotExist:
        user = GreylistIP.objects.create()
        user.ip_address = ip_address
        user.log = []
        user.save
        return user
