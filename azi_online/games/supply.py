from players.models import Players
from games.models import Tables, Game
from datetime import datetime, timezone

# Преобразование строки в массив
def get_array(income_string):
    outcome_array=[]
    if income_string:
        substrings = income_string.split(',')
        for substring in substrings:
            cleaned_substring = substring.strip()
            if cleaned_substring:
                try:
                    num = int(cleaned_substring)
                    outcome_array.append(num)
                except ValueError:
                    pass
    return outcome_array

# И обратно
def set_array(income_array):
    outcome_string = ''
    if income_array:        
        outcome_string = ', '.join(str(num) for num in income_array)
    return outcome_string

# Преобразование строки в массив Boolean
def get_bool_array(income_string):
    outcome_array = []
    if income_string:
        substrings = income_string.split(',')
        for substring in substrings:
            cleaned_substring = substring.strip()
            if cleaned_substring:
                outcome_array.append(cleaned_substring.lower() == 'true')
    return outcome_array

# И обратно
def set_bool_array(income_array):
    outcome_string = ', '.join(str(val).lower() for val in income_array)
    return outcome_string

# Определение монет у игроков за столом
def get_table_coins(table_id):
    table = Tables.objects.get(number=table_id)
    table_players = table.players
    coins = []
    for id in table_players:
        if id != 0:
            player = Players.objects.get(id=id)
            if table.cointype == 0:
                coins.append(player.silvercoin)
            elif table.cointype == 1:
                coins.append(player.goldcoin)
            elif table.cointype == 2:
                coins.append(player.bonuscoin)
        else:
            coins.append(0)
    return coins


# Счетчик значений статуса игроков за сотлом
def check_table_status(table_id, checking_value):
    table = Tables.objects.get(number=table_id)
    max_players = table.max_players
    players_status = table.status[:max_players]
    return players_status.count(checking_value)

# Проверка достаточности количества монет пользователя для игры за столом
def check_enough_coin(user_id, table_id, value):
    try:        
        player = Players.objects.get(id=user_id)        
        table = Tables.objects.get(number=table_id)
        print(f'CHECK ENOUGH COIN : Try 2 | table cointype is {table.cointype}')
        if table.cointype == 0:
            print(f'CHECK ENOUGH COIN : if 0')
            if player.silvercoin >= value:
                print(f'Player balance is {player.silvercoin} | Bet is {value}')
                return True
        if table.cointype == 1:
            print(f'CHECK ENOUGH COIN : if 1')
            if player.goldcoin >= value:
                return True
        if table.cointype == 2:
            print(f'CHECK ENOUGH COIN : if 2')
            if player.bonuscoin >= value:
                return True
        print(f'CHECK ENOUGH COIN : not if')
        return False
    except:
        print(f'CHECK ENOUGH COIN : Try')
        return False

def table_lastdeal_update(table_id):
    table = Tables.objects.get(number=table_id)        
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    unix_time = int(current_time.timestamp())
    table.lastdeal = unix_time
    table.save()

def player_lastaction_update(user_id):
    player = Players.objects.get(id=user_id)        
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    unix_time = int(current_time.timestamp())
    player.last_activity = unix_time
    player.save()

def cards_quntity(card_array):
    card_count = [0,0,0,0,0,0]
    for i in range(0, 6):
        player_cards = card_array[i*4:(i+1)*4]
        card_count[i] = 4 - player_cards.count(0)
    return card_count

def find_min_missing_natural(arr):
    if not arr:
        return 1  # Если массив пустой, возвращаем 1
    arr_set = set(arr)
    min_num = 1
    while min_num in arr_set:
        min_num += 1
    return min_num





