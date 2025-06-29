# Импорт зависимостей
from web3 import Web3
import math
# URI для провайдера BSC
#WEB3_PROVIDER_URI = 'https://bsc-dataseed1.binance.org:443'

# Создание экземпляра Web3
web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))

# Создание экземпляра Web3
#web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

abi = [{"inputs": [], "payable": False, "stateMutability": "nonpayable", "type": "constructor"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "spender", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}], "name": "Approval", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"}, {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}], "name": "OwnershipTransferred", "type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "from", "type": "address"}, {"indexed": True, "internalType": "address", "name": "to", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}], "name": "Transfer", "type": "event"}, {"constant": True, "inputs": [{"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "address", "name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False, "inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "payable": False, "stateMutability": "nonpayable", "type": "function"}, {"constant": True, "inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"}, {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False, "inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "subtractedValue", "type": "uint256"}], "name": "decreaseAllowance", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "payable": False, "stateMutability": "nonpayable", "type": "function"}, {"constant": True, "inputs": [], "name": "getOwner", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False, "inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "addedValue", "type": "uint256"}], "name": "increaseAllowance", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "payable": False, "stateMutability": "nonpayable", "type": "function"}, {"constant": False, "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "mint", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "payable": False, "stateMutability": "nonpayable", "type": "function"}, {"constant": True, "inputs": [], "name": "name", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "payable": False, "stateMutability": "view", "type": "function"}, {"constant": True, "inputs": [], "name": "owner", "outputs": [{"internalType": "address", "name": "", "type": "address"}], "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False, "inputs": [], "name": "renounceOwnership", "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"}, {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "payable": False, "stateMutability": "view", "type": "function"}, {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"}, {"constant": False, "inputs": [{"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "transfer", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "payable": False, "stateMutability": "nonpayable", "type": "function"}, {"constant": False, "inputs": [{"internalType": "address", "name": "sender", "type": "address"}, {"internalType": "address", "name": "recipient", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "transferFrom", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "payable": False, "stateMutability": "nonpayable", "type": "function"}, {"constant": False, "inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}], "name": "transferOwnership", "outputs": [], "payable": False, "stateMutability": "nonpayable", "type": "function"}]

# Функция для получения данных о транзакции
def get_transaction_data(transaction_hash):    
    print(f'CHECKER - GET TRANSACTION DATA - {transaction_hash} Type of token - {type(transaction_hash)}')
    # Получение данных о транзакции по ее хэшу
    try: 
        transaction = web3.eth.get_transaction(transaction_hash)
        return transaction
    except Exception as e:
        print(f'CHECKER - Error getting transaction data: {e}')
        return None

# Тестовый хэш транзакции
test_transaction_hash = '0x7571084d18fd2946175ede788053130da780ee6748af9d874fd17dbfed1d57d4'

# Запуск функции для получения данных о транзакции

transaction_data = get_transaction_data(test_transaction_hash)
print(f'TRANSACTION {transaction_data}')
"""
decoded_input = web3.eth.contract(abi=abi).decode_function_input(transaction_data['input'])
result = decoded_input[1]
print('Отправитель токенов:', transaction_data['from'])
print('Получатель токенов:', result['recipient'])
print('Количество токенов:', result['amount']/1000000000000000000)
print('Контракт:', transaction_data['to'])
real_amount = int(math.floor(result['amount'] / 10**18))
print(result['amount'], 'Тип данных:', type(result['amount']))
print('______________________________')
print(transaction_data['blockHash'] is not None)
"""
