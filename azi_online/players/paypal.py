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
