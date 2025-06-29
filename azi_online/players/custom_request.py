import base64
from eventlet.green.urllib.request import Request, urlopen
import urllib.parse
import json


def request_post(url, data, headers=None, auth=None):
    # Encode auth credentials as Basic Auth header
    if auth:
        auth_str = f"{auth[0]}:{auth[1]}"
        encoded_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        if headers is None:
            headers = {}
        headers['Authorization'] = f"Basic {encoded_auth}"    
    # Ensure headers are provided
    if headers is None:
        headers = {}
    # Set default Content-Type header if not provided
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    # Encode data for x-www-form-urlencoded
    encoded_data = urllib.parse.urlencode(data).encode('utf-8')
    # Create the request object
    request = Request(url, data=encoded_data, headers=headers)
    # Send the request and get the response
    try:
        with urlopen(request) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            response_headers = dict(response.getheaders())
            # Attempt to parse response data as JSON
            try:
                response_data = json.loads(response_data)
            except json.JSONDecodeError:
                # If response is not valid JSON, keep it as string
                pass
            return {
                'status_code': status_code,
                'data': response_data,
                'headers': response_headers
            }
    except Exception as e:
        return {'error': str(e)}
    
def request_get(url, access_token):
    # Set up the headers with the access token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    # Create the request object
    request = Request(url, headers=headers)
    # Send the request and get the response
    try:
        with urlopen(request) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            response_headers = dict(response.getheaders())
            # Attempt to parse response data as JSON
            try:
                response_data = json.loads(response_data)
            except json.JSONDecodeError:
                # If response is not valid JSON, keep it as string
                pass
            return {
                'status_code': status_code,
                'data': response_data,
                'headers': response_headers
            }
    except Exception as e:
        return {'error': str(e)}

from django.conf import settings
from web3 import Web3
web3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_OBSERVER_URL))
from .models import TokenSettings
from urllib.parse import urlencode


def get_transaction_data(transaction_hash):
    try:        
        print('GET TRANSACTION DATA custom: start...')
        bsc_token = settings.BSC_TOKEN
        bsc_api_url = settings.BSC_API        
        params = {
            'module': 'proxy',
            'action': 'eth_getTransactionByHash',
            'txhash': transaction_hash,
            'apikey': bsc_token
        }
        token_settings = TokenSettings.objects.get(id=1)        
        # Кодирование параметров в URL
        query_string = urlencode(params)
        url = f"{bsc_api_url}?{query_string}"
        # Создание объекта Request
        request = Request(url)
        # Отправка запроса и получение ответа
        try:
            with urlopen(request) as response:
                status_code = response.getcode()
                response_data = response.read().decode('utf-8')
                response_headers = dict(response.getheaders())
                # Попытка преобразования ответа в JSON
                try:
                    response_data = json.loads(response_data)
                except json.JSONDecodeError:
                    # Если ответ не является валидным JSON, оставить его строкой
                    pass
                print(f'GET TRANSACTION custom result --------------- \nstatus code: {status_code}\ndata: {response_data}\nheaders: {response_headers}')
                input_data = response_data['result']['input']
                print(f'GET TRANSACTION input data: {input_data}')
                transaction = response_data['result']                
                abi = token_settings.abi
                decoded_input = web3.eth.contract(abi=abi).decode_function_input(input_data)
                result = decoded_input[1]                            
                transaction_data = {
                    'from': transaction['from'],
                    'to': result['recipient'],
                    'amount': result['amount'],
                    'contract': transaction['to'],
                    'status': transaction['blockHash'] is not None
                }
                print(f'-----------------------------\nGET TRANSACTION - FINAL RESULT: {transaction_data}')
            return transaction_data
        except Exception as e:
            print(f'GET TRANSACTION custom Exception: {e}')
            return None
    except Exception as e:
        print(f'GET TRANSACTION DATA ERROR 1: {e}')
        return None
    

def get_transaction_data_usdt(transaction_hash):
    try:        
        print('GET TRANSACTION DATA custom: start...')
        bsc_token = settings.BSC_TOKEN
        bsc_api_url = settings.BSC_API        
        params = {
            'module': 'proxy',
            'action': 'eth_getTransactionByHash',
            'txhash': transaction_hash,
            'apikey': bsc_token
        }    
        # Кодирование параметров в URL
        query_string = urlencode(params)
        url = f"{bsc_api_url}?{query_string}"
        # Создание объекта Request
        request = Request(url)
        # Отправка запроса и получение ответа
        try:
            with urlopen(request) as response:
                status_code = response.getcode()
                response_data = response.read().decode('utf-8')
                response_headers = dict(response.getheaders())
                # Попытка преобразования ответа в JSON
                try:
                    response_data = json.loads(response_data)
                except json.JSONDecodeError:
                    # Если ответ не является валидным JSON, оставить его строкой
                    pass
                print(f'GET TRANSACTION custom result --------------- \nstatus code: {status_code}\ndata: {response_data}\nheaders: {response_headers}')
                input_data = response_data['result']['input']
                print(f'GET TRANSACTION input data: {input_data}')
                transaction = response_data['result']                
                abi = [{"inputs":[],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"owner","type":"address"},{"indexed":True,"internalType":"address","name":"spender","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":True,"inputs":[],"name":"_decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"_name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"_symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"getOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"}]
                decoded_input = web3.eth.contract(abi=abi).decode_function_input(input_data)
                result = decoded_input[1]                            
                transaction_data = {
                    'from': transaction['from'],
                    'to': result['recipient'],
                    'amount': result['amount'],
                    'contract': transaction['to'],
                    'status': transaction['blockHash'] is not None
                }
                print(f'-----------------------------\nGET TRANSACTION - FINAL RESULT: {transaction_data}')
            return transaction_data
        except Exception as e:
            print(f'GET TRANSACTION custom Exception: {e}')
            return None
    except Exception as e:
        print(f'GET TRANSACTION DATA ERROR 1: {e}')
        return None

def get_transaction_data_bnb(transaction_hash):
    try:        
        print('GET TRANSACTION DATA custom: start...')
        bsc_token = settings.BSC_TOKEN
        bsc_api_url = settings.BSC_API        
        params = {
            'module': 'proxy',
            'action': 'eth_getTransactionByHash',
            'txhash': transaction_hash,
            'apikey': bsc_token
        }        
        # Кодирование параметров в URL
        query_string = urlencode(params)
        url = f"{bsc_api_url}?{query_string}"
        # Создание объекта Request
        request = Request(url)
        # Отправка запроса и получение ответа
        try:
            with urlopen(request) as response:
                status_code = response.getcode()
                response_data = response.read().decode('utf-8')
                response_headers = dict(response.getheaders())
                # Попытка преобразования ответа в JSON
                try:
                    response_data = json.loads(response_data)
                except json.JSONDecodeError:
                    # Если ответ не является валидным JSON, оставить его строкой
                    pass
                print(f'GET TRANSACTION custom result --------------- \nstatus code: {status_code}\ndata: {response_data}\nheaders: {response_headers}')
                input_data = response_data['result']['input']
                print(f'GET TRANSACTION input data: {input_data}')
                transaction = response_data['result']
                print(f'GET BNB TRANSACTION: response data (transaction) \n{transaction}')                
                transaction_data = {
                    'from': transaction['from'],
                    'to': transaction['to'],
                    'amount': int(transaction['value'], 16),
                    'chain_id': int(transaction['chainId'], 16),
                    'status': transaction['blockHash'] is not None
                }
                print(f'-----------------------------\nGET TRANSACTION - FINAL RESULT: {transaction_data}')                
            return transaction_data
        except Exception as e:
            print(f'GET TRANSACTION custom Exception: {e}')
            return None
    except Exception as e:
        print(f'GET TRANSACTION DATA ERROR 1: {e}')
        return None