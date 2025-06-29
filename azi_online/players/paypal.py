from .models import DepositWithdrawSettings
from .custom_request import request_post, request_get

def get_payment_detail(payment_id):
    try:
        print(f'GET PAYMENT DETAIL: start test request function -------------------------------------- Payment ID is {payment_id}')
        payment_settings = DepositWithdrawSettings.objects.get(id=1)
        client_id = payment_settings.paypal_client_id
        client_secret = payment_settings.paypal_client_secret
        token_url = payment_settings.paypal_token_url
        order_url = payment_settings.paypal_order_url
        data = {"grant_type": "client_credentials"}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        auth = (client_id, client_secret)
        response = request_post(token_url, data=data, headers=headers, auth=auth)        
        #print(f'GET PAYMENT DETAIL test function: Response is : {response} type is {type(response['data'])}')
        try:
            access_token = response['data']["access_token"]
            print("Bearer token:", access_token)
        except Exception as e:
            print(f'JSON not decoded, token not found...')        
        response_get = request_get(f'{order_url}{payment_id}', access_token=access_token)
        #print(f'Order is: {response_get}, Type is {type(response_get['data'])}')
        return {'status': True, 'data': response_get['data']}
    except Exception as e:
        print(f'GET PAYMENT DETAIL Exception: {e}')
        return {'status': False, 'error': 0}


"""
def get_payment_detail(payment_id):
    try:
        payment_settings = DepositWithdrawSettings.objects.get(id=1)
        client_id = payment_settings.paypal_client_id
        client_secret = payment_settings.paypal_client_secret
        token_url = payment_settings.paypal_token_url
        order_url = payment_settings.paypal_order_url
        #client_id = 'Ac7gdglMG5Up38XcdnAEkmjT7gydWxLgC5mOS-0Ruj8-HmAqwB0aLUZRZBsvg2hukGnOgZSwIrrNCWuH'
        #client_secret = 'EHjD-0YpEv62EBfcmgTYCqcQQxbPi0C52TofcdwZR-_AexNEqICV_Bwl8Bd8uqUdDmLnVxNOOAAFXk5x'
        #token_url = 'https://api-m.paypal.com/v1/oauth2/token'
        #order_url = 'https://api-m.paypal.com/v2/checkout/orders/'
        data = {"grant_type": "client_credentials"}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        auth = (client_id, client_secret)
        response = requests.post(token_url, data=data, headers=headers, auth=auth)
        if response.status_code == 200:
            # Получение Bearer токена из ответа
            access_token = response.json()["access_token"]
            print("Bearer token:", access_token)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
            }
            response = requests.get(f'{order_url}{payment_id}', headers=headers)
            print(f'GET PAYMENT DETAIL - sending request for {order_url}{payment_id} with headers: {headers}')
            if response.status_code == 200:        
                json_data = response.json()
                #print("Response JSON:", json_data)
                return {'status': True, 'data': json_data}
            else:
                print("Failed to get access token:", response.text)
                return {'status': False, 'error': 0}
        else:
            print("Failed to get access token:", response.text)
            return {'status': False, 'error': 0}    
    except Exception as e:
        print(f'GET PAYMENT DETAIL - Exception {e}')
        return {'status': False, 'error': 0}

"""