from players.models import Players, PlayersStats, Airdrops, PlayersData
from games.models import Tables, Game, SandboxGame, BotPlayers
from .supply import *
from datetime import datetime, timezone
import random
import math
from .bot_mind import *
import json


def try_to_start_game(table_id):
    table = Tables.objects.get(number=table_id)
    table_players = table.players
    table_status = table.status
    all_are_ready = True
    ready_players_count = 0
    for i in range(0, table.max_players):
        if table_players[i] != 0:
            if table_status[i] != 1 and table.status[i] != 12:
                all_are_ready = False
            elif table.status[i] != 12:
                ready_players_count += 1
    if all_are_ready and ready_players_count > 1:
        create_new_game(table_id)
        return True
    else:
        print(f'TRY TO START NEW GAME - Not All are ready')
        return False

def create_new_game(table_id):
    print(f'CREATE NEW GAME - Table {table_id}: Creating the new game...')
    table = Tables.objects.get(number=table_id)
    table_players = table.players
    table_status = table.status
    game_players = [0, 0, 0, 0, 0, 0]
    for i in range(0, table.max_players):
        if (table_players[i] != 0) and (table_status[i] == 1):
            game_players[i] = table_players[i]
    betting_model = {
        "players": game_players,
        "dealer": -1,
        "ante": [-1, -1, -1, -1, -1, -1],
        "blind": [-1, -1, -1, -1, -1, -1],
        "trade": [],
        "hodor": -1,
        "cards": []
    }
    gaming_model = {
        "players": [0, 0, 0, 0, 0, 0],
        "cards": [],
        "drop": [0, 0, 0, 0, 0, 0],
        "turn_1_winner": -1,
        "turn_2_winner": -1,
        "turn_3_winner": -1,
        "turn_1": [0, 0, 0, 0, 0, 0],
        "turn_2": [0, 0, 0, 0, 0, 0],
        "turn_3": [0, 0, 0, 0, 0, 0],
        "winner": -1,
        "azi_in": [0, 0, 0, 0, 0, 0],
        "azi_burst": [0, 0, 0, 0, 0, 0],
        "azi_refuse": [0, 0, 0, 0, 0, 0],
        "azi_price": [-1, -1, -1, -1, -1, -1]
    }
    game = Game(
        start_game = datetime.utcnow().replace(tzinfo=timezone.utc),
        table_id = table_id,
        cointype = table.cointype,
        players = game_players,
        min_bet = table.min_bet,
        drop_suit = table.drop_suit,
        lastgame = table.currentgame,
        speaker = 0,
        speaker_id = 0,
        stage = 1,
        betting = betting_model,
        gaming = gaming_model,
        log = []
    )
    game.save()
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    unix_time = int(current_time.timestamp())
    table.currentgame = game.id
    table.lastdeal = unix_time
    table.save()
    set_dealer(game.id)
    set_speaker(game.id)

# Определение дилера
def set_dealer(game_id):
    game = Game.objects.get(id=game_id)
    table = Tables.objects.get(number=game.table_id)
    if game.lastgame != 0:
        lastgame = Game.objects.get(id=game.lastgame)
        table.dealing = lastgame.winner
        table.save()
    else:
        table.dealing = 0
        table.save()
    game_players = game.players
    table_status = table.status
    if not (game_players[table.dealing] != 0 and table_status[table.dealing] == 1):
        for i in range(table.dealing + 1, table.dealing + table.max_players + 1):
            ind = i % table.max_players
            if game_players[ind] != 0 and table_status[ind] == 1:
                table.dealing = ind
                table.save()
                break
    game.betting['dealer'] = table.dealing
    game.save()
    print(f'SET DEALER: Dealer is {table.dealing} - User {game_players[table.dealing]}')

# Определение спикера
def set_speaker(game_id):
    game = Game.objects.get(id=game_id)
    table = Tables.objects.get(number=game.table_id)
    game_players = game.players
    table_status = table.status
    for i in range(table.dealing + 1, table.dealing + table.max_players + 1):
        index = i % table.max_players
        if game_players[index] != 0 and table_status[index] == 1:
            game.speaker = index
            game.speaker_id = game_players[index]
            game.save()
            print(f'SET SPEAKER: Speaker is {index} - User {game_players[index]}')
            break

# Переопределение спикера
def next_speaker(game_id):
    try:
        game = Game.objects.get(id=game_id)
        table = Tables.objects.get(number=game.table_id)
        game_players = game.players
        table_status = table.status
        for i in range(game.speaker + 1, game.speaker + table.max_players + 1):
            index = i % table.max_players
            if game_players[index] != 0 and table_status[index] != 0 and table_status[index] != 8 and table_status[index] != 10 and table_status[index] != 11 and table_status[index] != 12:
                game.speaker = index
                game.speaker_id = game_players[index]
                game.save()
                break
        print('NEXT SPEAKER SUCCESS')
    except:
        print('NEXT SPEAKER EXCEPT')

def ante_betting(game_id):
    try:
        game = Game.objects.get(id=game_id)
        table = Tables.objects.get(number=game.table_id)
        player = Players.objects.get(id=game.speaker_id)
        table_status = table.status
        game_usersays = game.usersays
        usersays_value = game.usersays_value
        no_coin = False
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        if table.cointype == 0:
            if player.silvercoin < table.min_bet:
                no_coin = True
            else:
                player.silvercoin -= table.min_bet
                game.pot += table.min_bet
                table_status[game.speaker] = 2
                game_usersays[game.speaker] = 1
                usersays_value[game.speaker] = table.min_bet
                game.usersays_value = usersays_value
                table.status = table_status
                game.usersays = game_usersays
                table.lastdeal = unix_time                
                game.betting['ante'][game.speaker] = table.min_bet
                player.save()
                game.save()
                table.save()
                print(f'ANTE BETTING: Player {player.nickname} bets Ante {table.min_bet}')
        elif table.cointype == 1:
            if player.goldcoin < table.min_bet:
                no_coin = True
            else:
                player.goldcoin -= table.min_bet
                game.pot += table.min_bet
                table_status[game.speaker] = 2
                game_usersays[game.speaker] = 1
                usersays_value[game.speaker] = table.min_bet
                game.usersays_value = usersays_value
                table.status = table_status
                game.usersays = game_usersays
                table.lastdeal = unix_time                
                game.betting['ante'][game.speaker] = table.min_bet
                player.save()
                game.save()
                table.save()
                print(f'ANTE BETTING: Player {player.nickname} bets Ante {table.min_bet}')
        elif table.cointype == 2:
            if player.bonuscoin < table.min_bet:
                no_coin = True
            else:
                player.bonuscoin -= table.min_bet
                game.pot += table.min_bet
                table_status[game.speaker] = 2
                game_usersays[game.speaker] = 1
                usersays_value[game.speaker] = table.min_bet
                game.usersays_value = usersays_value
                table.status = table_status
                game.usersays = game_usersays
                table.lastdeal = unix_time            
                game.betting['ante'][game.speaker] = table.min_bet
                player.save()
                game.save()
                table.save()
                print(f'ANTE BETTING: Player {player.nickname} bets Ante {table.min_bet}')
        if no_coin:
            table_status[game.speaker] = 12
            game_usersays[game.speaker] = 13
            table.lastdeal = unix_time            
            table.status = table_status
            game.usersays = game_usersays
            player.save()
            game.save()
            table.save()
            print(f'ANTE BETTING: Player {player.nickname} out of coins')
    except:
        print('ANTE BETTING EXCEPT')        

def ante_all_bets_checking(game_id):
    game = Game.objects.get(id=game_id)
    table = Tables.objects.get(number=game.table_id)
    table_status = table.status
    game_players = game.players
    all_bets_are_off = True
    for i in range (0, table.max_players):
        if game_players[i] != 0 and not (table_status[i] == 2 or table_status[i] == 11 or table_status[i] == 12):
            all_bets_are_off = False    
    if all_bets_are_off:
        game.stage = 2
        game.save()
        return all_bets_are_off
    else:
        return False

def blind_betting(user_id, table_id, blind_bet_value):
    try:
        player = Players.objects.get(id=user_id)
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)
        game_players = game.players
        table_status = table.status
        player_index = game_players.index(user_id)
        if not table.blind_game or game.speaker_id != user_id or player_index != game.speaker or table_status[player_index] != 2:
            print(f'gaming.py/BLIND BETTING: something wrong...')
            return False
        else:            
            if table.cointype == 0:
                player.silvercoin -= blind_bet_value
                game.pot += blind_bet_value
            if table.cointype == 1:
                player.goldcoin -= blind_bet_value
                game.pot += blind_bet_value
            if table.cointype == 2:
                player.bonuscoin -= blind_bet_value
                game.pot += blind_bet_value
            game.stage = 3
            game.current_hodor = player_index
            game_players_bet = game.players_bet
            game_players_bet[player_index] += blind_bet_value*2
            game.betting['blind'][player_index] = blind_bet_value
            game_usersays = [0, 0, 0, 0, 0, 0]
            game_usersays_value = [0, 0, 0, 0, 0, 0]
            if blind_bet_value == table.min_bet * 5:
                game.top_bet = True
                game_usersays[player_index] = 5
            else:
                game_usersays[player_index] = 4
            game_usersays_value[player_index] = blind_bet_value*2
            game.usersays = game_usersays
            game.usersays_value = game_usersays_value
            game.players_bet = game_players_bet
            player.save()            
            game.save()
            return True
    except:
        return False

def blind_check(user_id, table_id):
    try:
        player = Players.objects.get(id=user_id)
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)
        game_players = game.players
        table_status = table.status
        player_index = game_players.index(user_id)
        if not table.blind_game or game.speaker_id != user_id or player_index != game.speaker or table_status[player_index] != 2:
            print(f'gaming.py/BLIND CHECK: something wrong...')
            return False
        else:
            game.stage = 3
            game.usersays = [0, 0, 0, 0, 0, 0]
            game.usersays_value = [0, 0, 0, 0, 0, 0]
            game.usersays[player_index] = 14
            game.save()
            return True
    except:
        return False
    
def create_actual_deck(game_id):
    try:
        game = Game.objects.get(id=game_id)        
        if game.drop_suit == 0:
            game.actual_deck = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]
        elif game.drop_suit == 1:
            game.actual_deck = [10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]
        elif game.drop_suit == 2:
            game.actual_deck = [1,2,3,4,5,6,7,8,9,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]
        if game.drop_suit == 3:
            game.actual_deck = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,28,29,30,31,32,33,34,35,36]
        if game.drop_suit == 4:
            game.actual_deck = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]
        game.save()
    except:
        pass

def deal_card(game_id):
    print(f'DEAL CARD: {game_id}')
    try:
        game = Game.objects.get(id=game_id)
        table = Tables.objects.get(number=game.table_id)
        player_card_count = [0,0,0,0,0,0]
        actual_players = [0,0,0,0,0,0]
        first_deal = None
        player_index = -1
        # Находим индекс игрока, которому нужно раздать карту
        for i in range(table.dealing + 1, table.dealing + table.max_players + 1):
            index = i % table.max_players
            if game.players[index] != 0 and table.status[index] == 2:
                first_deal = index
                break
        # Подсчитываем количество карт у каждого игрока
        for i in range(0, 6):
            if table.status[i] == 2 and game.players[i] != 0:
                actual_players[i] = game.players[i]
                this_player_cards = game.card_players[i*4:(i+1)*4]
                player_card_count[i] = 4 - this_player_cards.count(0)
            else:
                player_card_count[i] = 4
        # Если у всех игроков по 4 карты, выбираем козырную карту и сортируем карты
        if all(count == 4 for count in player_card_count):
            trump_card = random.choice(game.actual_deck)
            game.actual_deck.remove(trump_card)
            game.card_players[24] = trump_card
            game.save()
            try:
                game.card_players = sort_cards(game.card_players)
                game.betting['cards'] = game.card_players
                game.save()
            except:
                game.betting['cards'] = game.card_players
                game.save()
                print('DEAL CARDS: Sort cards error')
            return player_index
        else:
            # Находим игрока с минимальным числом карт
            min_cards = min(player_card_count)
            for i in range (first_deal, first_deal + 7):
                index = i % table.max_players
                if actual_players[index] != 0 and player_card_count[index] == min_cards:
                    deal_card = random.choice(game.actual_deck)
                    game.actual_deck.remove(deal_card)
                    game.card_players[index * 4 + min_cards] = deal_card
                    game.save()
                    player_index = index                
                    break
            return player_index
    except:
        return -2

def sort_cards(card_players):
    sort_criteria = [1, 10, 19, 28, 2, 11, 20, 29, 3, 12, 21, 30, 4, 13, 22, 31, 5, 14, 23, 32, 6, 15, 24, 33, 7, 16, 25, 34, 8, 17, 26, 35, 9, 18, 27, 36]
    sort_dict = {num: i for i, num in enumerate(sort_criteria)}
    trump_card = card_players[24]
    trump_offcet = 100
    sorted_cards = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(0, 6):
        temp_array = []
        for c in range(0, 4):
            card = card_players[i*4+c]
            if (1 <= trump_card <= 9) and (1 <= card <= 9):
                card += trump_offcet
            elif (10 <= trump_card <= 18) and (10 <= card <= 18):
                card += trump_offcet
            elif (19 <= trump_card <= 27) and (19 <= card <= 27):
                card += trump_offcet
            elif (28 <= trump_card <= 36) and (28 <= card <= 36):
                card += trump_offcet
            else:
                pass
            temp_array.append(card)
        temp_array.sort()
        temp_temp_array = [num for num in temp_array if num in sort_dict]
        sorted_temp_array = sorted(temp_temp_array, key=sort_dict.get)
        missing_nums = set(temp_array) - set(sort_dict.keys())
        sorted_array = sorted_temp_array + sorted(missing_nums)
                
        if sorted_array == [0]:
            sorted_array = [0, 0, 0, 0]
        for c in range(0, 4):
            sorted_cards[i*4+c] = sorted_array[c] % trump_offcet
        sorted_cards[24] = trump_card
    return sorted_cards

def dealing_is_complete(game_id):
    game = Game.objects.get(id=game_id)
    table = Tables.objects.get(number=game.table_id)
    active_players = 0
    for i in range(0, 6):
        if table.status[i] == 2 and game.players[i] != 0:
            active_players += 1
    count_zero = game.card_players.count(0)
    count_cards = 25 - count_zero
    if count_cards == active_players*4 + 1:
        print(f'DEALING IS COMPLETE: Dealing is complete')       
        return True
    else:
        print(f'DEALING IS COMPLETE: Dealing is not complete - Active players is {active_players} and {count_cards} cards is dealed ')
        return False    

def bet_betting(user_id, table_id, bet_value):
    try:
        player = Players.objects.get(id=user_id)
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)
        game_players = game.players
        table_status = table.status
        player_index = game_players.index(user_id)        
        if game.speaker_id != user_id or player_index != game.speaker or table_status[player_index] != 2:
            print(f'gaming.py/BET BETTING: something wrong...')
            return False
        else:            
            if table.cointype == 0:
                player.silvercoin -= bet_value
                game.pot += bet_value
            if table.cointype == 1:
                player.goldcoin -= bet_value
                game.pot += bet_value
            if table.cointype == 2:
                player.bonuscoin -= bet_value
                game.pot += bet_value
            game.current_hodor = player_index
            game_players_bet = game.players_bet
            game_players_bet[player_index] += bet_value
            betting = [-1,-1,-1,-1,-1,-1]
            betting[player_index] = bet_value
            game.betting['trade'].append(betting)            
            if bet_value == table.min_bet * 10:
                game.top_bet = True
                game.usersays[player_index] = 3
            else:
                game.usersays[player_index] = 2
            game.usersays_value[player_index] = bet_value            
            game.players_bet = game_players_bet
            player.save()            
            game.save()
            return True
    except:
        return False

def call_betting(user_id, table_id, call_value):
    try:
        player = Players.objects.get(id=user_id)
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)
        game_players = game.players
        table_status = table.status
        player_index = game_players.index(user_id)
        if game.speaker_id != user_id or player_index != game.speaker or table_status[player_index] != 2:
            print(f'gaming.py/CALL BETTING: something wrong...')
            return False
        else:            
            if table.cointype == 0:
                player.silvercoin -= call_value
                game.pot += call_value
            if table.cointype == 1:
                player.goldcoin -= call_value
                game.pot += call_value
            if table.cointype == 2:
                player.bonuscoin -= call_value
                game.pot += call_value
            game_players_bet = game.players_bet
            game_players_bet[player_index] += call_value            
            game.usersays[player_index] = 8
            game.usersays_value[player_index] = call_value            
            game.players_bet = game_players_bet
            betting = [-1,-1,-1,-1,-1,-1]
            betting[player_index] = call_value
            game.betting['trade'].append(betting)
            player.save()            
            game.save()
            return True
    except:
        return False


def check_betting(user_id, table_id):
    try:        
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)        
        player_index = game.players.index(user_id)
        if game.speaker_id != user_id or player_index != game.speaker or table.status[player_index] != 2:
            print(f'gaming.py/CHECK BETTING: something wrong...')
            return False
        else:                       
            game.usersays[player_index] = 7
            game.usersays_value[player_index] = 0
            game.check_status[player_index] = True
            betting = [-1,-1,-1,-1,-1,-1]
            betting[player_index] = 0
            game.betting['trade'].append(betting)
            game.save()
            return True
    except:
        return False

def fold_betting(user_id, table_id):
    try:        
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)        
        player_index = game.players.index(user_id)
        if game.speaker_id != user_id or player_index != game.speaker or table.status[player_index] != 2:
            print(f'gaming.py/CHECK BETTING: something wrong...')
            return False
        else:                       
            game.usersays[player_index] = 9
            game.usersays_value[player_index] = 0
            table.status[player_index] = 11
            for i in range(0, 4):
                game.card_players[player_index*4 + i] = 0
            betting = [-1,-1,-1,-1,-1,-1]
            betting[player_index] = -11
            game.betting['trade'].append(betting)
            table.save()
            game.save()
            return True
    except:
        return False

def raise_betting(user_id, table_id, raise_value):
    try:
        player = Players.objects.get(id=user_id)
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)
        player_index = game.players.index(user_id)
        call_value = max(game.players_bet) - game.players_bet[player_index]
        print(f'RAISE BETTING: 1')
        total_value = raise_value + call_value
        print(f'RAISE BETTING: 2')
        table_status = table.status
        print(f'RAISE BETTING: 3')
        player_index = game.players.index(user_id)
        print(f'RAISE BETTING: 4')
        if game.speaker_id != user_id or player_index != game.speaker or table_status[player_index] != 2:
            print(f'gaming.py/RAISE BETTING: something wrong...')
            return False
        else:
            print('RAISE BETTING: else inside')
            if table.cointype == 0:
                player.silvercoin -= total_value
                game.pot += total_value
            if table.cointype == 1:
                player.goldcoin -= total_value
                game.pot += total_value
            if table.cointype == 2:
                player.bonuscoin -= total_value
                game.pot += total_value
            game.current_hodor = player_index
            game_players_bet = game.players_bet
            game_players_bet[player_index] += total_value
            betting = [-1,-1,-1,-1,-1,-1]
            betting[player_index] = total_value
            game.betting['trade'].append(betting)
            if raise_value == table.min_bet * 10:
                game.top_bet = True
                game.usersays[player_index] = 15
            else:
                game.usersays[player_index] = 6
            game.usersays_value[player_index] = raise_value            
            game.players_bet = game_players_bet
            player.save()            
            game.save()
            return True
    except:
        print('RAISE BETTING: except')
        return False

def trade_is_complete(game_id):
    try:
        all_bets_are_off = True
        game = Game.objects.get(id=game_id)
        table = Tables.objects.get(number=game.table_id)
        max_value = max(game.players_bet)
        if max_value == 0:
            return False
        for i in range(0, 6):
            if game.players[i] != 0 and table.status[i] == 2:                
                if game.players_bet[i] != max_value:
                    all_bets_are_off = False
                    break
        if all_bets_are_off:
            game.betting['hodor'] = game.current_hodor
            game.gaming['cards'] = game.card_players
            game.stage = 5
            game.speaker = -1
            game.speaker_id = 0
            game.save()
        return all_bets_are_off
    except:
        return False

def all_are_check(game_id):
    try:
        all_bets_are_check = True
        game = Game.objects.get(id=game_id)
        table = Tables.objects.get(number=game.table_id)
        for i in range(0, 6):
            if (game.players[i] != 0) and (table.status[i] == 2):
                if game.check_status[i] != True:
                    all_bets_are_check = False
                    break
        if all_fold_victory(game_id):
            all_bets_are_check = False
        else:
            if all_bets_are_check:
                game.check_status = [False, False, False, False, False, False]
                for i in range(0, 6):
                    if (game.players[i] != 0) and (table.status[i] == 2):
                        table.status[i] = 1
                # Set new dealer
                for i in range(table.dealing + 1, table.dealing + table.max_players + 1):                    
                    ind = i % table.max_players
                    if game.players[ind] != 0 and table.status[ind] == 1:
                        table.dealing = ind                    
                        break
                # Set new speaker
                for i in range(table.dealing + 1, table.dealing + table.max_players + 1):
                    index = i % table.max_players
                    if game.players[index] != 0 and table.status[index] == 1:
                        game.speaker = index
                        game.speaker_id = game.players[index]
                        break

                betting_model = {
                    "players": game.players,
                    "dealer": -1,
                    "ante": [-1, -1, -1, -1, -1, -1],
                    "blind": [-1, -1, -1, -1, -1, -1],
                    "trade": [],
                    "hodor": -1,
                    "cards": []
                }
                betting_log = game.betting
                game.log.append({"betting": betting_log, "gaming": {}})
                game.betting = betting_model

                game.stage = 11
                table.save()
                game.save()
            
        return all_bets_are_check
    except:
        return False
    

def all_fold_victory(game_id):
    try:
        print('ALL FOLD VICTORY - try')
        game = Game.objects.get(id=game_id)
        table = Tables.objects.get(number=game.table_id)
        if table.status.count(2) != 1:
            return False
        else:
            winner_index = table.status.index(2)
            game.winner = winner_index
            player = Players.objects.get(id=game.players[winner_index])
            if table.cointype == 0:
                player.silvercoin += game.pot
            elif table.cointype == 1:
                player.goldcoin += game.pot
            elif table.cointype == 2:
                player.bonuscoin += game.pot
            game.stage = 12
            game.speaker = -1
            game.speaker_id = 0            
            game.current_hodor = -1
            game.end_game = datetime.utcnow()
            for i in range(0, 6):
                if table.status[i] != 12:
                    table.status[i] = 0
            game.gaming['winner'] = game.winner
            game.log.append({"betting": game.betting, "gaming": game.gaming})
            player.save()
            game.save()
            table.save()
            do_game_stats(game_id)
            return True
    except:
        print('ALL FOLD VICTORY - except')
        return False

def update_table_players_status(table_id):
    try:
        #print('UPDATE TABLE PLAYERS STATUS - Try')
        table = Tables.objects.get(number=table_id)
        players_for_drop = []
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        for i in range(0, 6):
            if table.status[i] != 0:
                player = Players.objects.get(id=table.players[i])
                if table.status[i] == 12:
                    if table.cointype == 0:
                        if player.silvercoin >= table.min_bet:
                            table.status[i] = 0                
                    elif table.cointype == 1:
                        if player.goldcoin >= table.min_bet:
                            table.status[i] = 0                    
                    elif table.cointype == 2:
                        if player.bonuscoin >= table.min_bet:
                            table.status[i] = 0
                    table.save()
                print(f'UPDATE TABLE PLAYERS STATUS: Player {player.id} status {table.status[i]} lastdeal {player.last_activity} Current time is {unix_time} Different is {unix_time - player.last_activity}')
                if table.default_ready[i] > table.default_ready_limit:
                    players_for_drop.append({"index": i, "user_id": player.id, "error": 712})
                elif (table.status[i] == 12 and player.last_activity + table.inactive_drop_interval < unix_time):                    
                    players_for_drop.append({"index": i, "user_id": player.id, "error": 712})
        if len(players_for_drop) >= 1:
            return {"status": True, "drop": True, "droplist": players_for_drop}
        else:
            return {"status": True, "drop": False}
    except:
        print('UPDATE TABLE PLAYERS STATUS - Except')
        return {"status": False}

def check_drop_card_complete(game_id):
    game = Game.objects.get(id=game_id)
    table = Tables.objects.get(number=game.table_id)
    drop_is_complete = True
    for i in range(0, table.max_players):
        if game.players[i] != 0 and table.status[i] not in (3, 11, 12):
            drop_is_complete = False
    if drop_is_complete:
        game.stage = 6        
        game.speaker = game.current_hodor
        game.save()
        table_lastdeal_update(game.table_id)


def turn_checking(game_id, card_id, player_index):
    game = Game.objects.get(id=game_id)
    card_index = game.card_players.index(card_id)    
    if (card_index >= player_index * 4) and (card_index < (player_index * 4) + 4) and (card_id != 0):        
        if all(element == 0 for element in game.card_place) and (game.current_hodor == player_index):
            return {"status": True}
        elif game.card_place[game.current_hodor] != 0:
            card_hodor = game.card_place[game.current_hodor]
            range_hodor = range(((card_hodor - 1) // 9) * 9 + 1, ((card_hodor - 1) // 9) * 9 + 10)            
            range_trump = range( ((game.card_players[24] - 1) // 9) * 9 + 1, ((game.card_players[24] - 1) // 9) * 9 + 10)
            if card_id in range_hodor:                
                return {"status": True}
            elif card_id in range_trump:
                no_hodor_suit = True
                for ci in range(0, 4):
                    cc = game.card_players[player_index * 4 + ci]
                    if cc in range_hodor:
                        no_hodor_suit = False
                if no_hodor_suit:                    
                    return {"status": True}
                else:
                    print('TURN CHECKING ERROR (717): You must make a move with a card of the same suit as the attacker player')
                    return {"status": False, "error": 717}
            else:
                no_hodor_suit = True
                for ci in range(0, 4):
                    cc = game.card_players[player_index * 4 + ci]
                    if cc in range_hodor:
                        no_hodor_suit = False
                if not no_hodor_suit:
                    return {"status": False, "error": 717}
                no_trump = True
                for ci in range(0, 4):
                    cc = game.card_players[player_index * 4 + ci]
                    if cc in range_trump:
                        no_trump = False
                if no_hodor_suit and no_trump:
                    print('TURN CHECKING: good poor suit!')
                    return {"status": True}
                else:                    
                    print('TURN CHECKING ERROR (718): If you do not have a card of the same suit as the attacker players card, you must make a move with a trump card')
                    return {"status": False, "error": 718}
    print('TURN_CHECKING: error')
    return {"status": False, "error": 0}

def turn_1(game_id, user_id, card_pos):
    try:
        game = Game.objects.get(id=game_id)
        table = Tables.objects.get(number=game.table_id)
        player_index = game.players.index(user_id)
        card_id = game.card_players[player_index*4 + card_pos]
        if (game.speaker != player_index) or (card_id == 0):
            return {"status": False, "error": 0}
        else:
            turn_checking_result = turn_checking(game_id, card_id, player_index)
            if not turn_checking_result['status']:
                return turn_checking_result
            else:
                game.card_players[player_index*4 + card_pos] = 0
                game.card_place[player_index] = card_id
                table.status[player_index] = 4
                game.save()
                table.save()
                return {"status": True}
    except:
        return {"status": False, "error": 0}

def turn_2(game_id, user_id, card_pos):
    try:        
        game = Game.objects.get(id=game_id)
        table = Tables.objects.get(number=game.table_id)
        player_index = game.players.index(user_id)
        card_id = game.card_players[player_index*4 + card_pos]
        print(f'TURN 3 player index is {player_index} card id is {card_id}')
        if (game.speaker != player_index) or (card_id == 0):
            return {"status": False, "error": 0}
        else:
            turn_checking_result = turn_checking(game_id, card_id, player_index)
            if not turn_checking_result['status']:
                return turn_checking_result
            else:
                game.card_players[player_index*4 + card_pos] = 0
                game.card_place[player_index] = card_id
                table.status[player_index] = 5
                game.save()
                table.save()
                return {"status": True}
    except:
        return {"status": False, "error": 0}

def turn_3(game_id, user_id, card_pos):
    try:
        game = Game.objects.get(id=game_id)
        table = Tables.objects.get(number=game.table_id)
        player_index = game.players.index(user_id)
        card_id = game.card_players[player_index*4 + card_pos]
        print(f'TURN 3 player index is {player_index} card id is {card_id}')
        if (game.speaker != player_index) or (card_id == 0):
            return {"status": False, "error": 0}
        else:
            turn_checking_result = turn_checking(game_id, card_id, player_index)
            if not turn_checking_result['status']:
                return turn_checking_result
            else:
                game.card_players[player_index*4 + card_pos] = 0
                game.card_place[player_index] = card_id
                table.status[player_index] = 6
                game.save()
                table.save()
                return {"status": True}
    except:
        return {"status": False, "error": 0}

def turn_winner(card_place, hodor_card, trump_card):
    range_hodor = range(((hodor_card - 1) // 9) * 9 + 1, ((hodor_card - 1) // 9) * 9 + 10)
    range_trump = range(((trump_card - 1) // 9) * 9 + 1, ((trump_card - 1) // 9) * 9 + 10)
    print(f'TURN WINNER: Range_hodor is {range_hodor}; Range_trump is {range_trump}; Card place is {card_place}')
    card_compare = [0] * 6
    for i in range(0, 6):
        if card_place[i] in range_hodor:
            card_compare[i] = card_place[i] + 100
        elif card_place[i] in range_trump:
            card_compare[i] = card_place[i] + 200
        else:
            card_compare[i] = card_place[i]
    best_hand = card_compare.index(max(card_compare))
    return best_hand

def check_turn_1_complete(game_id):
    game = Game.objects.get(id=game_id)
    table = Tables.objects.get(number=game.table_id)
    all_players_turned_1 = True
    for i in range(0, table.max_players):
        if (game.players[i] != 0) and (table.status[i] != 0) and (table.status[i] != 11) and (table.status[i] != 12):
            if table.status[i] != 4:
                all_players_turned_1 = False
    if all_players_turned_1:
        game.stage = 7
        hodor_card = game.card_place[game.current_hodor]
        trump = game.card_players[24]
        game.turn1win = turn_winner(game.card_place, hodor_card, trump)
        for i in range(0, 6):
            cp = i + game.current_hodor
            if cp >= 6:
                cp = cp % 6
            game.card_place1[i] = game.card_place[cp]        
        game.gaming['turn_1'] = game.card_place
        game.card_place = [0, 0, 0, 0, 0, 0]
        game.current_hodor = game.turn1win
        game.speaker = game.turn1win
        for i in range(0, 6):
            if i == game.speaker:
                game.speaker_id = game.players[i]        
        game.gaming['turn_1_winner'] = game.turn1win
        game.save()
    return all_players_turned_1


def check_turn_2_complete(game_id):
    game = Game.objects.get(id=game_id)
    table = Tables.objects.get(number=game.table_id)
    all_players_turned_2 = True
    for i in range(0, table.max_players):
        if (game.players[i] != 0) and (table.status[i] != 0) and (table.status[i] != 11) and (table.status[i] != 12):
            if table.status[i] != 5:
                all_players_turned_2 = False    
    if all_players_turned_2:
        game.stage = 8
        hodor_card = game.card_place[game.current_hodor]
        trump = game.card_players[24]        
        game.turn2win = turn_winner(game.card_place, hodor_card, trump)        
        for i in range(0, 6):
            cp = i + game.current_hodor
            if cp >= 6:
                cp = cp % 6
            game.card_place2[i] = game.card_place[cp]
        game.gaming['turn_2'] = game.card_place
        game.card_place = [0, 0, 0, 0, 0, 0]
        game.current_hodor = game.turn2win
        game.speaker = game.turn2win
        for i in range(0, 6):
            if i == game.speaker:
                game.speaker_id = game.players[i]    
        game.gaming['turn_2_winner'] = game.turn2win
        game.save()
    return all_players_turned_2

def check_turn_3_complete(game_id):
    game = Game.objects.get(id=game_id)
    table = Tables.objects.get(number=game.table_id)
    all_players_turned_3 = True
    for i in range(0, table.max_players):
        if (game.players[i] != 0) and (table.status[i] != 0) and (table.status[i] != 11) and (table.status[i] != 12):
            if table.status[i] != 6:
                all_players_turned_3 = False    
    if all_players_turned_3:
        game.stage = 9
        hodor_card = game.card_place[game.current_hodor]
        trump = game.card_players[24]        
        game.turn3win = turn_winner(game.card_place, hodor_card, trump)        
        for i in range(0, 6):
            cp = i + game.current_hodor
            if cp >= 6:
                cp = cp % 6
            game.card_place3[i] = game.card_place[cp]
        game.gaming['turn_3'] = game.card_place
        game.card_place = [0, 0, 0, 0, 0, 0]
        game.current_hodor = game.turn3win
        game.speaker = game.turn3win
        for i in range(0, 6):
            if i == game.speaker:
                game.speaker_id = game.players[i]
        game.speaker = -1
        game.speaker_id = 0
        game.current_hodor = -1        
        game.gaming['turn_3_winner'] = game.turn3win
        game.save()
        if (game.turn1win == game.turn2win) or (game.turn1win == game.turn3win) or (game.turn2win == game.turn3win):
            end_game(game_id)
        else:
            azi_start(game_id)
    return all_players_turned_3

def end_game(game_id):
    print('END_GAME: started')
    game = Game.objects.get(id=game_id)
    table = Tables.objects.get(number=game.table_id)
    winner_pos = None
    if (game.turn1win == game.turn2win):
        winner_pos = game.turn1win
    elif (game.turn1win == game.turn3win):
        winner_pos = game.turn1win
    elif (game.turn2win == game.turn3win):
        winner_pos = game.turn2win
    print(f'END_GAME: Winner_pos is {winner_pos}')     
    game.winner = winner_pos
    winner_id = game.players[winner_pos]

    player = Players.objects.get(id=winner_id)
    table.dealing = winner_pos

    if table.cointype == 0:
        player.silvercoin += game.pot
    elif table.cointype == 1:
        player.goldcoin += game.pot
    elif table.cointype == 2:
        player.bonuscoin += game.pot
    game.stage = 12
    game.end_game = datetime.utcnow()

    game.gaming['winner'] = game.winner
    game.log.append({"betting": game.betting, "gaming": game.gaming})

    game.save()
    player.save()
    do_game_stats(game_id)

    for i in range(0, table.max_players):
        if table.status[i] != 12:
            table.status[i] = 0
        else:
            if table.players[i] != 0:
                poor_player = Players.objects.get(id=table.players[i])
                if table.cointype == 0 and player.silvercoin >= table.min_bet:
                    table.status[i] = 0
                elif table.cointype == 1 and player.goldcoin >= table.min_bet:
                    table.status[i] = 0
                elif table.cointype == 2 and player.bonuscoin >= table.min_bet:
                    table.status[i] = 0
            else:
                table.status[i] = 0
    table.save()

def azi_start(game_id):
    game = Game.objects.get(id=game_id)
    table = Tables.objects.get(number=game.table_id)
    print(f'AZI START: Game {game_id} is draw, players in AZI')
    for i in range(0, table.max_players):
        if (table.status[i] == 6) and ((game.turn1win == i) or (game.turn2win == i) or (game.turn3win == i)):
            table.status[i] = 7
            game.gaming['azi_in'][i] = table.players[i]
            print(f'Players pos {i} in AZI')
        elif (table.status[i] == 6) or (game.status[i] == 11):
            table.status[i] = 8
            print(f'Players pos {i} not in AZI')
    game.stage = 10
    table.dealing = game.turn3win
    game.azi_price = math.floor(game.pot / 2)
    game.usersays = [0, 0, 0, 0, 0, 0]
    game.usersays_value = [0, 0, 0, 0, 0, 0]
    game.check_status = [False, False, False, False, False, False]
    game.current_hodor = -1    
    game.save()
    table.save()

def player_azi_burst(game_id, user_id):
    try:
        game = Game.objects.get(id=game_id)
        table = Tables.objects.get(number=game.table_id)
        player = Players.objects.get(id=user_id)
        player_index = game.players.index(user_id)
        value = game.azi_price
        if not (table.status[player_index] == 8 or table.status[player_index] == 11):
            return {"status": False, "error": 0}
        print(f'PLAYER AZI BURST')
        if table.cointype == 0:
            if player.silvercoin < value:
                return {"status": False, "error": 719} #Error 719: You don't have enough coins to burst-in into AZI
            else:
                print(f'PLAYER AZI BURST - 1')
                player.silvercoin -= value
                game.pot += value
                game.usersays[player_index] = 11
                game.usersays_value[player_index] = value
                table.status[player_index] = 9
                print(f'PLAYER AZI BURST - 2')
                game.gaming['azi_burst'][player_index] = user_id
                game.gaming['azi_price'][player_index] = value
                print(f'PLAYER AZI BURST - 3')
                player.save()
                table.save()
                game.save()
                print(f'PLAYER AZI BURST - 4')
                return {"status": True}
        elif table.cointype == 1:
            if player.goldcoin < value:
                return {"status": False, "error": 719} #Error 719: You don't have enough coins to burst-in into AZI
            else:
                player.goldcoin -= value
                game.pot += value
                game.usersays[player_index] = 11
                game.usersays_value[player_index] = value
                table.status[player_index] = 9
                game.gaming['azi_burst'][player_index] = user_id
                game.gaming['azi_price'][player_index] = value
                player.save()
                table.save()
                game.save()
                return {"status": True}
        elif table.cointype == 2:
            if player.bonuscoin < value:
                return {"status": False, "error": 719} #Error 719: You don't have enough coins to burst-in into AZI
            else:
                player.bonuscoin -= value
                game.pot += value
                game.usersays[player_index] = 11
                game.usersays_value[player_index] = value
                table.status[player_index] = 9
                game.gaming['azi_burst'][player_index] = user_id
                game.gaming['azi_price'][player_index] = value
                player.save()
                table.save()
                game.save()
                return {"status": True}
        
    except:
        print(f'PLAYER AZI BURST - Except')
        return {"status": False, "error": 0}
    


def player_azi_refuse(game_id, user_id):
    try:
        game = Game.objects.get(id=game_id)
        table = Tables.objects.get(number=game.table_id)        
        player_index = game.players.index(user_id)
        if not (table.status[player_index] == 8 or table.status[player_index] == 11):
            return {"status": False, "error": 0}
        game.usersays[player_index] = 12
        game.usersays_value[player_index] = 0
        table.status[player_index] = 10
        game.gaming['azi_refuse'][player_index] = user_id
        game.save()
        table.save()
        return {"status": True}
    except:
        return {"status": False, "error": 0}

def player_azi_in_checking(game_id):
    game = Game.objects.get(id=game_id)
    table = Tables.objects.get(number=game.table_id)
    all_players_says = True
    for i in range(0, table.max_players):
        if game.players[i] != 0 and (table.status[i] == 8 or table.status[i] == 11):
            all_players_says = False
            break
    if all_players_says:
        game.stage = 2
        table.dealing = game.turn3win
        for p in range(0, table.max_players):
            if table.status[p] == 7 or table.status[p] == 9:
                table.status[p] = 2
            if table.status[p] == 10:
                table.status[p] = 11
        game.card_place = [0, 0, 0, 0, 0, 0]
        game.card_place1 = [0, 0, 0, 0, 0, 0]
        game.card_place2 = [0, 0, 0, 0, 0, 0]
        game.card_place3 = [0, 0, 0, 0, 0, 0]
        game.players_bet = [0, 0, 0, 0, 0, 0]
        game.top_bet = False
        for i in range(table.dealing + 1, table.dealing + table.max_players + 1):
            index = i % table.max_players
            if game.players[index] != 0 and table.status[index] == 2:
                game.speaker = index
                game.speaker_id = game.players[index]        
                print(f'SET SPEAKER: Speaker is {index} - User {game.players[index]}')
                break
        game.turn1win = -1
        game.turn2win = -1
        game.turn3win = -1
        game.usersays = [0, 0, 0, 0, 0, 0]
        game.usersays_value = [0, 0, 0, 0, 0, 0]
        game.actual_deck = None
        game.card_players = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        game.log.append({"betting": game.betting, "gaming": game.gaming})
        game.betting = {
            "players": game.players,
            "dealer": -1,
            "ante": [-1, -1, -1, -1, -1, -1],
            "blind": [-1, -1, -1, -1, -1, -1],
            "trade": [],
            "hodor": -1,
            "cards": []
        }
        game.gaming = {
            "players": [0, 0, 0, 0, 0, 0],
            "cards": [],
            "drop": [0, 0, 0, 0, 0, 0],
            "turn_1_winner": -1,
            "turn_2_winner": -1,
            "turn_3_winner": -1,
            "turn_1": [0, 0, 0, 0, 0, 0],
            "turn_2": [0, 0, 0, 0, 0, 0],
            "turn_3": [0, 0, 0, 0, 0, 0],
            "winner": -1,
            "azi_in": [0, 0, 0, 0, 0, 0],
            "azi_burst": [0, 0, 0, 0, 0, 0],
            "azi_refuse": [0, 0, 0, 0, 0, 0],
            "azi_price": [-1, -1, -1, -1, -1, -1]
        }
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        table.lastdeal = unix_time
        game.save()
        table.save()

def default_blind_check(table_id):    
    try:        
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)                
        game.stage = 3
        game.usersays = [0, 0, 0, 0, 0, 0]
        game.usersays_value = [0, 0, 0, 0, 0, 0]
        game.usersays[game.speaker] = 14
        game.save()
    except:
        print('DEFAULT BLIND CHECK - Except')

def default_betting_player(table_id):
    try:
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)
        user_id = game.players[game.speaker]
        if max(game.players_bet) == 0:
            if check_betting(user_id, table_id):
                table_lastdeal_update(table_id)
                if not all_are_check(table.currentgame):                    
                    next_speaker(table.currentgame)            
        else:
            if fold_betting(user_id, table_id):                
                table_lastdeal_update(table_id)            
                if not all_fold_victory(table.currentgame):
                    if not all_are_check(table.currentgame):
                        if not trade_is_complete(table.currentgame):
                            next_speaker(table.currentgame)
    except:
        print('DEFAULT BETTING PLAYER - Except')

def default_card_dropping_players(table_id):
    try:
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)
        for i in range(0, table.max_players):
            player_index = game.players.index(game.players[i])
            if table.status[player_index] == 2 and all(game.card_players[player_index*4+step] != 0 for step in range(4)):
                game.gaming['drop'][player_index] = game.card_players[player_index*4]
                game.card_players[player_index*4] = 0
                table.status[player_index] = 3        
        game.save()
        table.save()
        table_lastdeal_update(table_id)
    except:
        print('DEFAULT CARD DROPPING PLAYERS - Except')

def default_turn_player(table_id):
    try:
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)
        player_index = game.speaker
        for card_pos in range(0, 4):
            card_id = game.card_players[player_index*4 + card_pos]
            if card_id != 0 and ((game.stage == 6 and table.status[player_index] == 3) or (game.stage == 7 and table.status[player_index] == 4) or (game.stage == 8 and table.status[player_index] == 5)):
                turn_check = turn_checking(game.id, card_id, player_index)
                if turn_check['status']:
                    game.card_players[player_index*4 + card_pos] = 0
                    game.card_place[player_index] = card_id
                    if game.stage == 6:
                        table.status[player_index] = 4
                    elif game.stage == 7:
                        table.status[player_index] = 5
                    elif game.stage == 8:
                        table.status[player_index] = 6                    
                    game.save()
                    table.save()                    
                    table_lastdeal_update(table_id)
                    break
    except:
        print('DEFAULT TURN PLAYER - Except')

def default_players_azi_decline(table_id):
    try:
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)
        for i in range(0, table.max_players):
            user_id = game.players[i]
            player_azi_refuse(game.id, user_id)
        player_azi_in_checking(game.id)
    except:
        print('DEFAULT TURN PLAYER - Except')
    
#------------------------------------------------------------------------

def start_new_table(new_table):
    try:
        print(f'START NEW TABLE {new_table}')
        user_id = new_table['user_id']
        player = Players.objects.get(id=user_id)
        if player.active_table > 0:            
            return { "status": False, 'error': 900 }
        max_players = new_table['max_players']
        min_bet = new_table['min_bet']
        drop_suit = new_table['drop_suit']
        cointype = new_table['cointype']
        blind_game = new_table['blind_game']
        interval = new_table['interval']
        password = new_table['password']
        print(f'START NEW GAME before IF 1')
        if (cointype == 0 and player.silvercoin < min_bet) or (cointype == 1 and player.goldcoin < min_bet) or (cointype == 2 and player.bonuscoin < min_bet):            
            return { "status": False, 'error': 901 }
        print(f'START NEW GAME before IF 2')
        if max_players > 6 or max_players < 2 or min_bet < 1 or min_bet > 1000 or drop_suit < 0 or drop_suit > 4 or interval < 10 or interval > 60:            
            return { "status": False, 'error': 0 }
        tables = Tables.objects.all()
        tables_numbers = [table.number for table in tables]
        print(f'START NEW GAME - tables {tables_numbers}')
        new_number = find_min_missing_natural(tables_numbers)        
        created_table = Tables(
            number=new_number,
            max_players=max_players,
            drop_suit=drop_suit,
            cointype=cointype,
            min_bet=min_bet,
            max_bet=min_bet*10,
            table_password=password,
            interval=interval,
            blind_game=blind_game
        )
        created_table.save()
        table = Tables.objects.get(number=new_number)
        table.players[0] = user_id        
        table.players_now = sum(1 for player in table.players[:table.max_players] if player != 0)
        table.save()
        player.active_table = new_number
        player.save()    
        return { "status": True, 'table_id': table.number }
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return { "status": False, 'error': 0 }


# SCHEDULER FUNCTIONS ----------------------------------------------------------------------------
def check_and_delete_tables():
    tables = Tables.objects.all()
    tables_deleted = False
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    unix_time = int(current_time.timestamp())
    for table in tables:
        if table.time_stop !=0 and unix_time > table.time_stop + 180 and table.players_now == 0:
            table.delete()
            tables_deleted = True
    return tables_deleted

def check_and_delete_verifications_code():
    players = Players.objects.all()
    codes_deleted = False
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    unix_time = int(current_time.timestamp())
    for player in players:
        if player.verification_code != None and player.verification_time + 3600 <= unix_time and player.verification_time != 0:
            player.verification_code = None
            player.verification_time = 0
            player.verification_try = 0
            player.save()
            codes_deleted = True
    return codes_deleted

def check_and_deposit_bots():
    bots = BotPlayers.objects.all()
    deposited = False
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    unix_time = int(current_time.timestamp())
    for bot in bots:
        if bot.democoin < 100000:
            bot.democoin += 100000
            log_note = {"date": unix_time, "deposit": 100000}
            bot.deposit_log.append(log_note)
            bot.save()
            deposited = True
    return deposited

def check_airdrops():
    airdrop_done = False
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    try:
        WeeklyAirdrop = Airdrops.objects.get(name='weekly')
    except Airdrops.DoesNotExist:
        WeeklyAirdrop = None
    try:
        MonthlyAirdrop = Airdrops.objects.get(name='monthly')
    except Airdrops.DoesNotExist:
        MonthlyAirdrop = None
    try:
        DailyAirdrop = Airdrops.objects.get(name='daily')
    except Airdrops.DoesNotExist:
        DailyAirdrop = None
    try:
        all_airdrops = Airdrops.objects.exclude(name__in=['daily', 'weekly', 'monthly'])
    except Airdrops.DoesNotExist:
        all_airdrops = None

    if WeeklyAirdrop is not None:
        if WeeklyAirdrop.completed:
            if WeeklyAirdrop.day_of_week != current_time.weekday():
                WeeklyAirdrop.completed = False
                WeeklyAirdrop.save()
        else:
            if WeeklyAirdrop.day_of_week == current_time.weekday() and WeeklyAirdrop.hour == current_time.hour:
                do_weekly_airdrop()
                airdrop_done = True
    
    if MonthlyAirdrop is not None:
        if MonthlyAirdrop.completed:
            if MonthlyAirdrop.day != current_time.day:
                MonthlyAirdrop.completed = False
                MonthlyAirdrop.save()
        else:
            if MonthlyAirdrop.day == current_time.day and MonthlyAirdrop.hour == current_time.hour:
                do_monthly_airdrop()
                airdrop_done = True
    
    if DailyAirdrop is not None:
        if DailyAirdrop.completed:
            if DailyAirdrop.hour != current_time.hour:
                DailyAirdrop.completed = False
                DailyAirdrop.save()
        else:
            if DailyAirdrop.hour == current_time.hour:
                do_daily_airdrop()
                airdrop_done = True

    if all_airdrops is not None:
        for airdrop in all_airdrops:
            try:
                if not airdrop.completed and airdrop.date is not None and airdrop.date <= current_time:
                    if do_custom_airdrop(airdrop.name):
                        airdrop_done = True
            except Exception as custom_airdrop_error:
                print(f'Custom airdrop error - {custom_airdrop_error}')

    return airdrop_done


# ------------- AIRDROPS -------------------------------------------------------------------------
def do_custom_airdrop(airdrop_name):
    try:
        airdrop = Airdrops.objects.get(name=airdrop_name)
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        try:
            players = airdrop.to
            if not isinstance(players, list) or not all(isinstance(x, int) for x in players):
                players = Players.objects.values_list('id', flat=True)
        except:
            players = Players.objects.values_list('id', flat=True)
        for player_id in players:
            try:
                player_data = get_player_data(player_id)
                if airdrop.cointype == 0:
                    action = {
                        "date": unix_time,
                        "coin": "silvercoin",                        
                        "value": airdrop.value,
                        "method": airdrop_name
                    }
                    player_data.airdrop_silver += airdrop.value
                    player_data.coin_activity.append(action)
                    player_data.history_silver.append(action)
                    player_data.save()
                elif airdrop.cointype == 1:
                    action = {
                        "date": unix_time,
                        "coin": "goldcoin",                        
                        "value": airdrop.value,
                        "method": airdrop_name
                    }
                    player_data.airdrop_gold += airdrop.value
                    player_data.coin_activity.append(action)
                    player_data.history_gold.append(action)
                    player_data.save()
                elif airdrop.cointype == 2:
                    action = {
                        "date": unix_time,
                        "coin": "bonuscoin",                        
                        "value": airdrop.value,
                        "method": airdrop_name
                    }
                    player_data.airdrop_bonus += airdrop.value
                    player_data.coin_activity.append(action)
                    player_data.history_bonus.append(action)
                    player_data.save()
            except Exception as no_player:
                print(f'DO CUSTOM AIRDROP - Error No player: {no_player}')
                airdrop.completed = True
                airdrop.save()
                return False
        airdrop.completed = True
        airdrop.save()
        print(f'CUSTOM AIRDROP COMPLETED SUCCESSFULLY! ')        
        return True
    except:
        return False


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

def do_weekly_airdrop():
    try:
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        WeeklyAirdrop = Airdrops.objects.get(name='weekly')        
        try:
            players = WeeklyAirdrop.to
            if not isinstance(players, list) or not all(isinstance(x, int) for x in players):
                players = Players.objects.values_list('id', flat=True)
        except (json.JSONDecodeError, TypeError):
            players = Players.objects.values_list('id', flat=True)
        for player_id in players:
            try:
                player_data = get_player_data(player_id)
                if WeeklyAirdrop.cointype == 0:
                    action = {
                        "date": unix_time,
                        "coin": "silvercoin",                        
                        "value": WeeklyAirdrop.value,
                        "method": "weekly"                        
                    }
                    player_data.airdrop_silver += WeeklyAirdrop.value
                    player_data.coin_activity.append(action)
                    player_data.history_silver.append(action)
                    player_data.save()
                elif WeeklyAirdrop.cointype == 1:
                    action = {
                        "date": unix_time,
                        "coin": "goldcoin",                        
                        "value": WeeklyAirdrop.value,
                        "method": "weekly"                        
                    }
                    player_data.airdrop_gold += WeeklyAirdrop.value
                    player_data.coin_activity.append(action)
                    player_data.history_gold.append(action)
                    player_data.save()
                elif WeeklyAirdrop.cointype == 2:
                    action = {
                        "date": unix_time,
                        "coin": "bonuscoin",                        
                        "value": WeeklyAirdrop.value,
                        "method": "weekly"                        
                    }
                    player_data.airdrop_bonus += WeeklyAirdrop.value
                    player_data.coin_activity.append(action)
                    player_data.history_bonus.append(action)
                    player_data.save()                
            except Exception as no_player:
                print(f'DO WEEKLY AIRDROP - Error No player: {no_player}')
                WeeklyAirdrop.completed = True
                WeeklyAirdrop.save()
        WeeklyAirdrop.completed = True
        WeeklyAirdrop.save()
        print(f'WEEKLY AIRDROP COMPLETED SUCCESSFULLY! ')
    except Exception as e:
        print(f'DO WEEKLY AIRDROP - Error : {e}')

def do_monthly_airdrop():
    try:
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        MonthlyAirdrop = Airdrops.objects.get(name='monthly')
        try:
            players = MonthlyAirdrop.to
            if not isinstance(players, list) or not all(isinstance(x, int) for x in players):
                players = Players.objects.values_list('id', flat=True)
        except (json.JSONDecodeError, TypeError):
            players = Players.objects.values_list('id', flat=True)
        for player_id in players:
            try:
                player_data = get_player_data(player_id)
                if MonthlyAirdrop.cointype == 0:
                    action = {
                        "date": unix_time,
                        "coin": "silvercoin",                        
                        "value": MonthlyAirdrop.value,
                        "method": "monthly"                        
                    }
                    player_data.airdrop_silver += MonthlyAirdrop.value
                    player_data.coin_activity.append(action)
                    player_data.history_silver.append(action)
                    player_data.save()
                elif MonthlyAirdrop.cointype == 1:
                    action = {
                        "date": unix_time,
                        "coin": "goldcoin",                        
                        "value": MonthlyAirdrop.value,
                        "method": "monthly"                        
                    }
                    player_data.airdrop_gold += MonthlyAirdrop.value
                    player_data.coin_activity.append(action)
                    player_data.history_gold.append(action)
                    player_data.save()
                elif MonthlyAirdrop.cointype == 2:
                    action = {
                        "date": unix_time,
                        "coin": "bonuscoin",                        
                        "value": MonthlyAirdrop.value,
                        "method": "monthly"                        
                    }
                    player_data.airdrop_bonus += MonthlyAirdrop.value
                    player_data.coin_activity.append(action)
                    player_data.history_bonus.append(action)
                    player_data.save()                
            except Exception as no_player:
                print(f'DO MONTHLY AIRDROP - Error No player: {no_player}')
                MonthlyAirdrop.completed = True
                MonthlyAirdrop.save()
        MonthlyAirdrop.completed = True
        MonthlyAirdrop.save()
        print(f'MONTHLY AIRDROP COMPLETED SUCCESSFULLY! ')
    except Exception as e:
        print(f'DO MONTHLY AIRDROP - Error : {e}')

def do_daily_airdrop():
    pass
# ------------- SANDBOX --------------------------------------------------------------------------

def new_sandbox_game(user_id):
    print('NEW SANDBOX GAME')
    game = SandboxGame(
        start_game = datetime.utcnow().replace(tzinfo=timezone.utc),
        user_id = user_id,
        players = [0, 1, 2, 3, 4, 5]
    )
    game.save()    
    return game

def get_sandbox_game(user_id):
    try:        
        try:            
            sandbox_game = SandboxGame.objects.get(user_id=user_id)            
        except SandboxGame.DoesNotExist:
            print('GET SANDBOX GAME - EXCEPT')
            sandbox_game = new_sandbox_game(user_id)
        player = Players.objects.get(id=user_id)
        nicknames = sandbox_game.bot_nicknames
        nicknames[0] = player.nickname
        game_json = {
            "user_id": user_id,
            "max_players": sandbox_game.max_players,
            "players": sandbox_game.players,
            "min_bet": sandbox_game.min_bet,
            "drop_suit": sandbox_game.drop_suit,
            "trump_suit": sandbox_game.trump_suit,
            "pot": sandbox_game.pot,
            "winner": sandbox_game.winner,
            "card_players": cards_quntity(sandbox_game.card_players),
            "card_place1": sandbox_game.card_place1,
            "card_place2": sandbox_game.card_place2,
            "card_place3": sandbox_game.card_place3,
            "card_place": sandbox_game.card_place,
            "speaker": sandbox_game.speaker,
            "speaker_id": sandbox_game.speaker_id,
            "stage": sandbox_game.stage,
            "players_bet": sandbox_game.players_bet,
            "usersays": sandbox_game.usersays,
            "usersays_value": sandbox_game.usersays_value,
            "top_bet": sandbox_game.top_bet,
            "check_status": sandbox_game.check_status,
            "status": sandbox_game.status,
            "turn1win": sandbox_game.turn1win,
            "turn2win": sandbox_game.turn2win,
            "turn3win": sandbox_game.turn3win,
            "current_hodor": sandbox_game.current_hodor,
            "azi_price": sandbox_game.azi_price,
            "blind_game": sandbox_game.blind_game,
            "dealing": sandbox_game.dealing,
            "player_balance": player.democoin,
            "bot_nicknames": nicknames,
            "trump_value": sandbox_game.card_players[24],
            "my_cards": sandbox_game.card_players[:4]
        }
        return { "status": True, "game": game_json }    
    except:
        return { "status": False, "error": 0 }
    

def player_sandbox_change_rivals(user_id, max_players):
    try:
        sandbox_game = SandboxGame.objects.get(user_id=user_id)
        bot_players = list(BotPlayers.objects.all())
        all_bot_ids = [bot.id for bot in bot_players]
        random_bot_ids = random.sample(all_bot_ids, 5)
        random_bot_ids.insert(0, 0)
        players = random_bot_ids
        player = Players.objects.get(id=user_id)
        sandbox_game.bot_nicknames[0] = player.nickname
        sandbox_game.players = players
        sandbox_game.max_players = max_players
        for i in range(1, 6):
            bot = BotPlayers.objects.get(id=players[i])
            sandbox_game.bot_nicknames[i] = bot.nickname
        sandbox_game.save()
        return {"status": True}
    except:
        return {"status": False}

def sandbox_set_speaker(user_id):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        for i in range(game.dealing + 1, game.dealing + game.max_players + 1):
            index = i % game.max_players
            if game.players[index] != -1 and game.status[index] == 1:
                game.speaker = index
                game.speaker_id = game.players[index]
                game.save()                
                break
    except:
        pass

def sandbox_nextspeaker(user_id):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        lastspeaker = game.speaker
        for i in range(game.speaker + 1, game.speaker + game.max_players + 1):
            index = i % game.max_players
            if game.players[index] != -1 and game.status[index] != 0 and game.status[index] != 8 and game.status[index] != 10 and game.status[index] != 11 and game.status[index] != 12:
                game.speaker = index
                game.speaker_id = game.players[index]
                game.save()
                print(f'NEXTSPEAKER: Lastspeaker {lastspeaker} updated to New Speaker {game.speaker}')
                break
    except:
        print('NEXT SPEAKER EXCEPT')

def player_sandbox_start_game(game):
    try:
        print(f'START NEW GAME: front game is {game}')
        player = Players.objects.get(id=game['user_id'])
        if player.democoin < game['min_bet']:
            return {"status": False, "error": 724} # You don't have enough coins to play with this minimum bet! You need to reduce the minimum bet or top up your balance
        sandbox_game = SandboxGame.objects.get(user_id=game['user_id'])
        sandbox_game.max_players = game['max_players']
        sandbox_game.min_bet = game['min_bet']
        sandbox_game.drop_suit = game['drop_suit']
        sandbox_game.blind_game = game['blind_game']
        if game['winner'] != -1:
            if game['winner'] < game['max_players']:
                sandbox_game.dealing = game['winner']
            else:            
                sandbox_game.dealing = 0
        else:            
            sandbox_game.dealing = 0
        sandbox_game.winner = -1
        sandbox_game.stage = 1
        for k in range(game['max_players'], 6):
            sandbox_game.players[k] = -1
            sandbox_game.bot_nicknames[k] = ''
        sandbox_game.start_game = datetime.utcnow().replace(tzinfo=timezone.utc)
        sandbox_game.trump_suit = 0
        sandbox_game.pot =0
        sandbox_game.end_game = None
        sandbox_game.actual_deck = None
        sandbox_game.card_players = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        sandbox_game.card_place1 = [0, 0, 0, 0, 0, 0]
        sandbox_game.card_place2 = [0, 0, 0, 0, 0, 0]
        sandbox_game.card_place3 = [0, 0, 0, 0, 0, 0]
        sandbox_game.card_place = [0, 0, 0, 0, 0, 0]
        sandbox_game.cards_now = [0, 0, 0, 0, 0, 0]
        sandbox_game.speaker = -1
        sandbox_game.speaker_id = -1
        sandbox_game.players_bet = [0, 0, 0, 0, 0, 0]
        sandbox_game.usersays = [0, 0, 0, 0, 0, 0]
        sandbox_game.usersays_value = [0, 0, 0, 0, 0, 0]
        sandbox_game.top_bet = False
        sandbox_game.check_status = [False, False, False, False, False, False]
        sandbox_game.status = [0, 0, 0, 0, 0, 0]
        sandbox_game.turn1win = -1
        sandbox_game.turn2win = -1
        sandbox_game.turn3win = -1
        sandbox_game.current_hodor = -1
        sandbox_game.azi_price = 0
        sandbox_game.blind_complete = False
        for i in range(0, 6):
            if sandbox_game.players[i] != -1:
                sandbox_game.status[i] = 1
        print(f'SART NEW GAME - game berore saving is {sandbox_game}')
        sandbox_game.save()
        return {"status": True}
    except:
        print(f'SART NEW GAME - EXECPT')
        return {"status": False, "error": 0}
    

def sandbox_ante_checking(user_id):
    game = SandboxGame.objects.get(user_id=user_id)        
    all_bets_are_off = True
    for i in range (0, game.max_players):
        if game.players[i] != -1 and not (game.status[i] == 2 or game.status[i] == 11 or game.status[i] == 12):
            all_bets_are_off = False
    if all_bets_are_off:        
        game.stage = 2
        game.save()
        print(f'Sandbox ANTE CHECKING - gamestage is {game.stage}')
        return all_bets_are_off
    else:
        return False    
                
def sandbox_antebetting(user_id):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        if game.speaker == 0:
            player = Players.objects.get(id=user_id)
        else:
            player = BotPlayers.objects.get(id=game.players[game.speaker])
        no_coin = False        
        if player.democoin < game.min_bet:
            no_coin = True
        else:
            player.democoin -= game.min_bet
            game.pot += game.min_bet
            game.status[game.speaker] = 2
            game.usersays[game.speaker] = 1
            game.usersays_value[game.speaker] = game.min_bet
            player.save()
            game.save()            
            print(f'SANDBOX ANTE BETTING: Player {game.bot_nicknames[game.speaker]} bets Ante {game.min_bet}')
        if no_coin:
            game.status[game.speaker] = 12
            game.usersays[game.speaker] = 13                
            player.save()
            game.save()                
            print(f'ANTE BETTING: Player {game.bot_nicknames[game.speaker]} out of coins')        
    except:
        print('ANTE BETTING EXCEPT')        
    pass

def sandbox_all_fold_victory(user_id):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        if game.status.count(2) != 1:
            return False
        else:
            winner_index = game.status.index(2)
            game.winner = winner_index
            if winner_index == 0:
                player = Players.objects.get(id=user_id)
            else:
                player = BotPlayers.objects.get(id=game.players[winner_index])
            player.democoin += game.pot
            game.stage = 12
            game.speaker = -1
            game.speaker_id = -1
            game.current_hodor = -1
            for i in range(0, 6):
                if game.status[i] != 12:
                    game.status[i] = 0
            player.save()
            game.save()
            return True
    except:
        print('ALL FOLD VICTORY - except')
        return False
    
def sandbox_create_actual_deck(user_id):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        if game.drop_suit == 0:
            game.actual_deck = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]
        elif game.drop_suit == 1:
            game.actual_deck = [10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]
        elif game.drop_suit == 2:
            game.actual_deck = [1,2,3,4,5,6,7,8,9,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]
        if game.drop_suit == 3:
            game.actual_deck = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,28,29,30,31,32,33,34,35,36]
        if game.drop_suit == 4:
            game.actual_deck = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]
        game.save()
    except:
        pass

def sandbox_dealing_is_complete(user_id):
    game = SandboxGame.objects.get(user_id=user_id)
    active_players = 0
    for i in range(0, 6):
        if game.status[i] == 2 and game.players[i] != -1:
            active_players += 1
    count_zero = game.card_players.count(0)
    count_cards = 25 - count_zero
    if count_cards == active_players*4 + 1:
        print(f'DEALING IS COMPLETE: Dealing is complete')       
        return True
    else:
        # print(f'DEALING IS COMPLETE: Dealing is not complete - Active players is {active_players} and {count_cards} cards is dealed ')
        return False

def sandbox_deal_card(user_id):    
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        player_card_count = [0,0,0,0,0,0]
        actual_players = [0,0,0,0,0,0]
        first_deal = None
        player_index = -1
        # Находим индекс игрока, которому нужно раздать карту
        for i in range(game.dealing + 1, game.dealing + game.max_players + 1):
            index = i % game.max_players
            if game.players[index] != -1 and game.status[index] == 2:
                first_deal = index
                break
        # Подсчитываем количество карт у каждого игрока
        for i in range(0, 6):
            if game.status[i] == 2 and game.players[i] != -1:
                actual_players[i] = game.players[i]
                this_player_cards = game.card_players[i*4:(i+1)*4]
                player_card_count[i] = 4 - this_player_cards.count(0)
            else:
                player_card_count[i] = 4
        # Если у всех игроков по 4 карты, выбираем козырную карту и сортируем карты
        if all(count == 4 for count in player_card_count):
            trump_card = random.choice(game.actual_deck)
            game.actual_deck.remove(trump_card)
            game.card_players[24] = trump_card
            game.save()
            try:
                game.card_players = sort_cards(game.card_players)                
                game.save()
            except:                
                game.save()
                print('DEAL CARDS: Sort cards error')
            return player_index
        else:
            # Находим игрока с минимальным числом карт
            min_cards = min(player_card_count)
            for i in range (first_deal, first_deal + 7):
                index = i % game.max_players
                if actual_players[index] != -1 and player_card_count[index] == min_cards:
                    deal_card = random.choice(game.actual_deck)
                    game.actual_deck.remove(deal_card)
                    game.card_players[index * 4 + min_cards] = deal_card
                    game.save()
                    player_index = index                
                    break
            return player_index
    except:
        return -2

def sandbox_fill_table(user_id):
    game = SandboxGame.objects.get(user_id=user_id)
    bot_players = list(BotPlayers.objects.all())    
    all_bot_ids = [bot.id for bot in bot_players]
    available_bot_ids = [bot_id for bot_id in all_bot_ids if bot_id not in game.players[1:]]    
    for i in range(len(game.players)):
        if game.players[i] == -1:
            new_id = random.choice(available_bot_ids)
            game.players[i] = new_id
            bot_player = BotPlayers.objects.get(id=new_id)
            game.bot_nicknames[i] = bot_player.nickname
            # Удаляем выбранный ID из доступных, чтобы он не повторялся
            available_bot_ids.remove(game.players[i])    
    game.save()

def sandbox_player_blind_bet(user_id, blind_bet):
    try:        
        game = SandboxGame.objects.get(user_id=user_id)
        player = Players.objects.get(id=user_id)
        blind_bet_value = blind_bet * game.min_bet
        if player.democoin < blind_bet_value:
            return {"status": False, "error": 707}
        else:
            player_index = 0
            if not game.blind_game or player_index != game.speaker or game.status[player_index] != 2:
                print(f'gaming.py/BLIND BETTING: something wrong...')
                return {"status": False, "error": 0}
            else:
                player.democoin -= blind_bet_value
                game.pot += blind_bet_value
                game.stage = 3
                game.current_hodor = player_index
                game.players_bet[player_index] += blind_bet_value*2
                game.usersays = [0, 0, 0, 0, 0, 0]
                game.usersays_value = [0, 0, 0, 0, 0, 0]
                if blind_bet_value == game.min_bet * 5:
                    game.top_bet = True
                    game.usersays[player_index] = 5
                else:
                    game.usersays[player_index] = 4
                game.usersays_value[player_index] = blind_bet_value*2
                game.blind_complete = True
                player.save()            
                game.save()
                sandbox_nextspeaker(user_id)
                return {"status": True}            
    except:
        return {"status": False, "error": 0}

def sandbox_player_blind_check(user_id):    
    try:
        game = SandboxGame.objects.get(user_id=user_id)        
        player_index = 0
        if not game.blind_game or player_index != game.speaker or game.status[player_index] != 2:            
            return {"status": False, "error": 0}
        else:
            game.stage = 3
            game.usersays = [0, 0, 0, 0, 0, 0]
            game.usersays_value = [0, 0, 0, 0, 0, 0]
            game.usersays[player_index] = 14
            game.save()
            return {"status": True}
    except:
        return {"status": False, "error": 0}

def sandbox_someone_check(user_id, index):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        player_index = index
        if max(game.players_bet) != 0:
            return {"status": False, "error": 711}
        else:
            if player_index != game.speaker or game.status[player_index] != 2:
                print(f'gaming.py/SANDBOX_SOMEONE_CHECK: something wrong...')
                return {"status": False, "error": 0}
            else:
                for i in range(0, 6):
                    if game.usersays[i] == 1:
                        game.usersays[i] = 0
                game.usersays[player_index] = 7
                game.usersays_value[player_index] = 0
                game.check_status[player_index] = True                
                game.save()                
                return {"status": True}
    except:
        return {"status": False, "error": 0}

def sandbox_someone_fold(user_id, index):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        player_index = index
        if player_index != game.speaker or game.status[player_index] != 2:
            print(f'gaming.py/SANDBOX_SOMEONE_FOLD: something wrong... Player index is {player_index} Gamespeaker is {game.speaker} Player status is {game.status[player_index]}')
            return {"status": False, "error": 0}
        else:
            for i in range(0, 6):
                if game.usersays[i] == 1:
                    game.usersays[i] = 0
            game.usersays[player_index] = 9
            game.usersays_value[player_index] = 0
            game.status[player_index] = 11
            for i in range(0, 4):
                game.card_players[player_index*4 + i] = 0
            game.save()
            return {"status": True}
        
    except:
        return {"status": False, "error": 0}


def sandbox_someone_bet(user_id, bet, index):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        player_index = index
        bet_value = bet * game.min_bet
        if player_index == 0:
            player = Players.objects.get(id=user_id)
        else:
            player = BotPlayers.objects.get(id=index)
        if player.democoin < bet_value:
            return {"status": False, "error": 707}    
        else:    
            if player_index != game.speaker or game.status[player_index] != 2:
                print(f'gaming.py/BET BETTING: something wrong...')
                return {"status": False, "error": 0}
            else:
                for i in range(0, 6):
                    if game.usersays[i] == 1:
                        game.usersays[i] = 0
                player.democoin -= bet_value
                game.pot += bet_value
                game.current_hodor = player_index        
                game.players_bet[player_index] += bet_value                
                if bet_value == game.min_bet * 10:
                    game.top_bet = True
                    game.usersays[player_index] = 3
                else:
                    game.usersays[player_index] = 2
                game.usersays_value[player_index] = bet_value
                player.save()            
                game.save()
                return {"status": True}
    except:
        return {"status": False, "error": 0}


def sandbox_someone_call(user_id, index):
    try:        
        game = SandboxGame.objects.get(user_id=user_id)
        player_index = index
        call_value = max(game.players_bet) - game.players_bet[player_index]        
        if call_value <= 0:
            return {"status": False, "error": 711}
        if player_index == 0:
            player = Players.objects.get(id=user_id)
        else:
            player = BotPlayers.objects.get(id=index)
        if player.democoin < call_value:
            return {"status": False, "error": 707}
        else:
            if player_index != game.speaker or game.status[player_index] != 2:
                print(f'gaming.py/SANDBOX SOMEONE CALL: something wrong...')
                return {"status": False, "error": 0}
            else:
                player.democoin -= call_value
                game.pot += call_value
                game.players_bet[player_index] += call_value            
                game.usersays[player_index] = 8
                game.usersays_value[player_index] = call_value                
                player.save()            
                game.save()
                return {"status": True}
    except:
        return {"status": False, "error": 0}


def sandbox_someone_raise(user_id, bet, index):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        player_index = index
        call_value = max(game.players_bet) - game.players_bet[player_index]
        bet_value = bet * game.min_bet
        if player_index == 0:
            player = Players.objects.get(id=user_id)
        else:
            player = BotPlayers.objects.get(id=index)
        if player.democoin < bet_value + call_value:
            return {"status": False, "error": 707}    
        else:
            total_value = bet_value + call_value
            if player_index != game.speaker or game.status[player_index] != 2:
                print(f'gaming.py/SANDBOX SOMEONE RAISE: something wrong...')
                return False
            else:
                player.democoin -= total_value
                game.pot += total_value
                game.current_hodor = player_index                
                game.players_bet[player_index] += total_value
                if bet_value == game.min_bet * 10:
                    game.top_bet = True
                    game.usersays[player_index] = 15
                else:
                    game.usersays[player_index] = 6
                game.usersays_value[player_index] = bet_value                
                player.save()            
                game.save()
                return {"status": True}
    except:
        return {"status": False, "error": 0}



def sandbox_trade_is_complete(user_id):
    try:
        all_bets_are_off = True
        game = SandboxGame.objects.get(user_id=user_id)
        max_value = max(game.players_bet)
        if max_value == 0:
            return False
        for i in range(0, 6):
            if game.players[i] != -1 and game.status[i] == 2:                
                if game.players_bet[i] != max_value:
                    all_bets_are_off = False
                    break
        if all_bets_are_off:
            game.stage = 5
            game.speaker = -1
            game.speaker_id = -1
            game.save()
        return all_bets_are_off
    except:
        return False


def sandbox_all_are_check(user_id):
    try:
        all_bets_are_check = True
        game = SandboxGame.objects.get(user_id=user_id)        
        for i in range(0, 6):
            if (game.players[i] != -1) and (game.status[i] == 2):
                if game.check_status[i] != True:
                    all_bets_are_check = False
                    break
        if sandbox_all_fold_victory(user_id):
            all_bets_are_check = False
        else:
            if all_bets_are_check:
                game.check_status = [False, False, False, False, False, False]
                for i in range(0, 6):
                    if (game.players[i] != -1) and (game.status[i] == 2):
                        game.status[i] = 1
                # Set new dealer
                for i in range(game.dealing + 1, game.dealing + game.max_players + 1):                    
                    ind = i % game.max_players
                    if game.players[ind] != -1 and game.status[ind] == 1:
                        game.dealing = ind                    
                        break
                # Set new speaker
                for i in range(game.dealing + 1, game.dealing + game.max_players + 1):
                    index = i % game.max_players
                    if game.players[index] != -1 and game.status[index] == 1:
                        game.speaker = index
                        game.speaker_id = game.players[index]
                        break
                game.stage = 11
                game.save()
        return all_bets_are_check
    except:
        return False

def sandbox_check_drop_card_complete(user_id):
    game = SandboxGame.objects.get(user_id=user_id)    
    drop_is_complete = True
    for i in range(0, game.max_players):
        if game.players[i] != -1 and game.status[i] not in (3, 11, 12):
            drop_is_complete = False
    if drop_is_complete:
        game.stage = 6        
        game.speaker = game.current_hodor
        game.save()
    pass

def sandbox_check_bots_drop_card_complete(user_id):
    game = SandboxGame.objects.get(user_id=user_id)    
    drop_is_complete = True
    for i in range(1, game.max_players):
        if game.players[i] != -1 and game.status[i] not in (3, 11, 12):
            drop_is_complete = False
    return drop_is_complete

def sandbox_bots_card_dropping(user_id):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        for i in range(1, game.max_players):
            player_index = game.players.index(game.players[i])
            if game.status[player_index] == 2 and all(game.card_players[player_index*4+step] != 0 for step in range(4)):                
                game.card_players[player_index*4] = 0
                game.status[player_index] = 3
        game.save()        
    except:
        print('DEFAULT CARD DROPPING PLAYERS - Except')

def sandbox_turn_checking(card_players, card_place, current_hodor, card_id):    
    player_index = 0
    card_index = card_players.index(card_id)    
    if (card_index >= player_index * 4) and (card_index < (player_index * 4) + 4) and (card_id != 0):        
        if all(element == 0 for element in card_place) and (current_hodor == player_index):
            return {"status": True}
        elif card_place[current_hodor] != 0:
            card_hodor = card_place[current_hodor]
            range_hodor = range(((card_hodor - 1) // 9) * 9 + 1, ((card_hodor - 1) // 9) * 9 + 10)            
            range_trump = range( ((card_players[24] - 1) // 9) * 9 + 1, ((card_players[24] - 1) // 9) * 9 + 10)
            if card_id in range_hodor:                
                return {"status": True}
            elif card_id in range_trump:
                no_hodor_suit = True
                for ci in range(0, 4):
                    cc = card_players[player_index * 4 + ci]
                    if cc in range_hodor:
                        no_hodor_suit = False
                if no_hodor_suit:
                    return {"status": True}
                else:
                    print('TURN CHECKING ERROR (717): You must make a move with a card of the same suit as the attacker player')
                    return {"status": False, "error": 717}
            else:
                no_hodor_suit = True
                for ci in range(0, 4):
                    cc = card_players[player_index * 4 + ci]
                    if cc in range_hodor:
                        no_hodor_suit = False
                if not no_hodor_suit:
                    return {"status": False, "error": 717}
                no_trump = True
                for ci in range(0, 4):
                    cc = card_players[player_index * 4 + ci]
                    if cc in range_trump:
                        no_trump = False
                if no_hodor_suit and no_trump:                    
                    return {"status": True}
                else:                    
                    print('TURN CHECKING ERROR (718): If you do not have a card of the same suit as the attacker players card, you must make a move with a trump card')
                    return {"status": False, "error": 718}
    print('TURN_CHECKING: error')
    return {"status": False, "error": 0}



def sandbox_turn_1(user_id, card_pos):
    try:
        game = SandboxGame.objects.get(user_id=user_id)        
        player_index = 0
        card_id = game.card_players[player_index*4 + card_pos]
        if (game.speaker != player_index) or (card_id == 0):
            return {"status": False, "error": 0}
        else:
            turn_checking_result = sandbox_turn_checking(game.card_players, game.card_place, game.current_hodor, card_id)
            if not turn_checking_result['status']:
                return turn_checking_result
            else:
                game.card_players[player_index*4 + card_pos] = 0
                game.card_place[player_index] = card_id
                game.status[player_index] = 4
                game.save()                
                return {"status": True}
    except:
        return {"status": False, "error": 0}

def sandbox_turn_2(user_id, card_pos):
    try:
        game = SandboxGame.objects.get(user_id=user_id)        
        player_index = 0
        card_id = game.card_players[player_index*4 + card_pos]
        if (game.speaker != player_index) or (card_id == 0):
            return {"status": False, "error": 0}
        else:
            turn_checking_result = sandbox_turn_checking(game.card_players, game.card_place, game.current_hodor, card_id)
            if not turn_checking_result['status']:
                return turn_checking_result
            else:
                game.card_players[player_index*4 + card_pos] = 0
                game.card_place[player_index] = card_id
                game.status[player_index] = 5
                game.save()                
                return {"status": True}
    except:
        return {"status": False, "error": 0}

def sandbox_turn_3(user_id, card_pos):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        player_index = 0
        card_id = game.card_players[player_index*4 + card_pos]
        if (game.speaker != player_index) or (card_id == 0):
            return {"status": False, "error": 0}
        else:
            turn_checking_result = sandbox_turn_checking(game.card_players, game.card_place, game.current_hodor, card_id)
            if not turn_checking_result['status']:
                return turn_checking_result
            else:
                game.card_players[player_index*4 + card_pos] = 0
                game.card_place[player_index] = card_id
                game.status[player_index] = 6
                game.save()                
                return {"status": True}
    except:
        return {"status": False, "error": 0}



def turn_winner(card_place, hodor_card, trump_card):
    range_hodor = range(((hodor_card - 1) // 9) * 9 + 1, ((hodor_card - 1) // 9) * 9 + 10)
    range_trump = range(((trump_card - 1) // 9) * 9 + 1, ((trump_card - 1) // 9) * 9 + 10)
    print(f'TURN WINNER: Range_hodor is {range_hodor}; Range_trump is {range_trump}; Card place is {card_place}')
    card_compare = [0] * 6
    for i in range(0, 6):
        if card_place[i] in range_hodor:
            card_compare[i] = card_place[i] + 100
        elif card_place[i] in range_trump:
            card_compare[i] = card_place[i] + 200
        else:
            card_compare[i] = card_place[i]
    best_hand = card_compare.index(max(card_compare))
    return best_hand

def sandbox_check_turn_1_complete(user_id):
    game = SandboxGame.objects.get(user_id=user_id)
    print(f'SANDBOX CHECK TURN 1 COMPLETE: Game stage is {game.stage}, speaker is {game.speaker}')
    if game.stage == 7:
        print(f'SANDBOX CHECK TURN 1 COMPLETE: Game stage is {game.stage}, default True')
        return True
    all_players_turned_1 = True
    for i in range(0, game.max_players):
        if (game.players[i] != -1) and (game.status[i] != 0) and (game.status[i] != 11) and (game.status[i] != 12):
            if game.status[i] != 4:
                all_players_turned_1 = False
    if all_players_turned_1:
        game.stage = 7
        hodor_card = game.card_place[game.current_hodor]
        trump = game.card_players[24]
        game.turn1win = turn_winner(game.card_place, hodor_card, trump)
        for i in range(0, 6):
            cp = i + game.current_hodor
            if cp >= 6:
                cp = cp % 6
            game.card_place1[i] = game.card_place[cp]        
        game.card_place = [0, 0, 0, 0, 0, 0]
        game.current_hodor = game.turn1win
        game.speaker = game.turn1win
        for i in range(0, 6):
            if i == game.speaker:
                game.speaker_id = game.players[i]        
        game.save()
    print(f'SANDBOX CHECK TURN 1 COMPLETE: Game stage is {game.stage}, result is {all_players_turned_1}')
    return all_players_turned_1

def sandbox_check_turn_2_complete(user_id):
    game = SandboxGame.objects.get(user_id=user_id)
    print(f'SANDBOX CHECK TURN 2 COMPLETE: Game stage is {game.stage}, speaker is {game.speaker}')
    if game.stage == 8:
        print(f'SANDBOX CHECK TURN 2 COMPLETE: Game stage is {game.stage}, default True')
        return True
    all_players_turned_2 = True
    for i in range(0, game.max_players):
        if (game.players[i] != -1) and (game.status[i] != 0) and (game.status[i] != 11) and (game.status[i] != 12):
            if game.status[i] != 5:
                all_players_turned_2 = False
    if all_players_turned_2:
        game.stage = 8
        hodor_card = game.card_place[game.current_hodor]
        trump = game.card_players[24]
        game.turn2win = turn_winner(game.card_place, hodor_card, trump)
        for i in range(0, 6):
            cp = i + game.current_hodor
            if cp >= 6:
                cp = cp % 6
            game.card_place2[i] = game.card_place[cp]        
        game.card_place = [0, 0, 0, 0, 0, 0]
        game.current_hodor = game.turn2win
        game.speaker = game.turn2win
        for i in range(0, 6):
            if i == game.speaker:
                game.speaker_id = game.players[i]        
        game.save()
    print(f'SANDBOX CHECK TURN 2 COMPLETE: Game stage is {game.stage}, result is {all_players_turned_2}')
    return all_players_turned_2

def sandbox_check_turn_3_complete(user_id):
    game = SandboxGame.objects.get(user_id=user_id)
    print(f'SANDBOX CHECK TURN 3 COMPLETE: Game stage is {game.stage}, speaker is {game.speaker}')
    if game.stage == 9:
        print(f'SANDBOX CHECK TURN 3 COMPLETE: Game stage is {game.stage}, default True')
        return True
    all_players_turned_3 = True
    for i in range(0, game.max_players):
        if (game.players[i] != -1) and (game.status[i] != 0) and (game.status[i] != 11) and (game.status[i] != 12):
            if game.status[i] != 6:
                all_players_turned_3 = False
    if all_players_turned_3:
        game.stage = 9
        hodor_card = game.card_place[game.current_hodor]
        trump = game.card_players[24]
        game.turn3win = turn_winner(game.card_place, hodor_card, trump)
        for i in range(0, 6):
            cp = i + game.current_hodor
            if cp >= 6:
                cp = cp % 6
            game.card_place3[i] = game.card_place[cp]        
        game.card_place = [0, 0, 0, 0, 0, 0]
        game.current_hodor = game.turn3win
        game.speaker = game.turn3win
        for i in range(0, 6):
            if i == game.speaker:
                game.speaker_id = game.players[i]        
        game.save()        
    print(f'SANDBOX CHECK TURN 3 COMPLETE: Game stage is {game.stage}, result is {all_players_turned_3}')
    return all_players_turned_3


def sandbox_end_game(user_id):
    print('END_GAME: started')
    game = SandboxGame.objects.get(user_id=user_id)    
    winner_pos = None
    if (game.turn1win == game.turn2win):
        winner_pos = game.turn1win
    elif (game.turn1win == game.turn3win):
        winner_pos = game.turn1win
    elif (game.turn2win == game.turn3win):
        winner_pos = game.turn2win
    print(f'END_GAME: Winner_pos is {winner_pos}')     
    game.winner = winner_pos
    winner_id = game.players[winner_pos]
    if winner_pos == 0:
        player = Players.objects.get(id=user_id)
    else:
        player = BotPlayers.objects.get(id=winner_id)
    game.speaker = -1
    game.dealing = winner_pos
    player.democoin += game.pot
    game.stage = 12
    game.end_game = datetime.utcnow()

    game.save()
    player.save()    
    for i in range(0, game.max_players):
        if game.status[i] != 12:
            game.status[i] = 0
    game.save()

def sandbox_azi_start(user_id):
    game = SandboxGame.objects.get(user_id=user_id)
    for i in range(0, game.max_players):
        if (game.status[i] == 6) and ((game.turn1win == i) or (game.turn2win == i) or (game.turn3win == i)):
            game.status[i] = 7                        
        elif (game.status[i] == 6) or (game.status[i] == 11):
            game.status[i] = 8
            print(f'Players pos {i} not in AZI')
    game.stage = 10
    game.dealing = game.turn3win
    print(f'info --- SANDBOX AZI START - game dealing sets to {game.dealing}')
    game.azi_price = math.floor(game.pot / 2)
    game.usersays = [0, 0, 0, 0, 0, 0]
    game.usersays_value = [0, 0, 0, 0, 0, 0]
    game.check_status = [False, False, False, False, False, False]
    game.current_hodor = -1    
    game.save()    

def sandbox_player_azi_burst(user_id, index):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        if index == 0:
            player = Players.objects.get(id=user_id)
        else:
            player = BotPlayers.objects.get(id=game.players[index])       
        player = Players.objects.get(id=user_id)
        player_index = index
        value = game.azi_price
        if not (game.status[player_index] == 8 or game.status[player_index] == 11):
            return {"status": False, "error": 0}
        if player.democoin < value:
            return {"status": False, "error": 719} #Error 719: You don't have enough coins to burst-in into AZI
        else:
            player.democoin -= value
            game.pot += value
            game.usersays[player_index] = 11
            game.usersays_value[player_index] = value
            game.status[player_index] = 9
            player.save()            
            game.save()
            return {"status": True}
    except:
        return {"status": False, "error": 0}
    

def sandbox_player_azi_refuse(user_id, index):
    try:
        game = SandboxGame.objects.get(user_id=user_id)  
        player_index = index
        if not (game.status[player_index] == 8 or game.status[player_index] == 11):
            return {"status": False, "error": 0}
        game.usersays[player_index] = 12
        game.usersays_value[player_index] = 0
        game.status[player_index] = 10
        game.save()        
        return {"status": True}
    except:
        return {"status": False, "error": 0}

def sandbox_player_azi_in_checking(user_id):
    game = SandboxGame.objects.get(user_id=user_id)    
    all_players_says = True
    for i in range(0, game.max_players):
        if game.players[i] != -1 and (game.status[i] == 8 or game.status[i] == 11):
            all_players_says = False
            break
    if all_players_says:
        game.stage = 2
        print(f'info --- SANDBOX PLAYER AZI IN CHECKING - game dealing sets to {game.dealing}')
        #game.dealing = game.turn3win
        for p in range(0, game.max_players):
            if game.status[p] == 7 or game.status[p] == 9:
                game.status[p] = 2
            if game.status[p] == 10:
                game.status[p] = 11
        game.card_place = [0, 0, 0, 0, 0, 0]
        game.card_place1 = [0, 0, 0, 0, 0, 0]
        game.card_place2 = [0, 0, 0, 0, 0, 0]
        game.card_place3 = [0, 0, 0, 0, 0, 0]
        game.players_bet = [0, 0, 0, 0, 0, 0]
        game.top_bet = False
        for i in range(game.dealing + 1, game.dealing + game.max_players + 1):
            index = i % game.max_players
            if game.players[index] != -1 and game.status[index] == 2:
                game.speaker = index
                game.speaker_id = game.players[index]        
                print(f'SET SPEAKER: Speaker is {index} - User {game.players[index]}')
                break
        game.turn1win = -1
        game.turn2win = -1
        game.turn3win = -1
        game.usersays = [0, 0, 0, 0, 0, 0]
        game.usersays_value = [0, 0, 0, 0, 0, 0]
        game.actual_deck = None
        game.card_players = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        game.save()


#---------------------------------------------------------------------------------------------------------------------------------------------

def get_player_stats(user_id):
    try:
        player_stats = PlayersStats.objects.get(user_id=user_id)
    except PlayersStats.DoesNotExist:
        player_stats = PlayersStats.objects.create(user_id=user_id)
        player_stats.games_log = []
        player_stats.save()    
    return player_stats

# Обработка статистики игры
def do_game_stats(game_id):
    try:
        game = Game.objects.get(id=game_id)
        ante = game.min_bet
        cointype = game.cointype
        log = game.log        
        pot = 0
        game_unixtime = int(game.end_game.timestamp())
        bets = [0, 0, 0, 0, 0, 0]
        players = [0, 0, 0, 0, 0, 0]
        profit = [0, 0, 0, 0, 0, 0]
        relative = [0, 0, 0, 0, 0, 0]
        relative_k = [0, 0, 0, 0, 0, 0]
        for deal in log:
            for index in range(0, 6):
                if deal['betting']['players'][index] != 0:
                    players[index] = deal['betting']['players'][index]
                    if deal['betting']['ante'][index] >= 0:
                        pot += deal['betting']['ante'][index]
                        bets[index] += deal['betting']['ante'][index]
                    if deal['betting']['blind'][index] >= 0:
                        pot += deal['betting']['blind'][index]
                        bets[index] += deal['betting']['blind'][index]
                    for trade_iteration in deal['betting']['trade']:
                        if trade_iteration[index] >= 0:
                            pot += trade_iteration[index]
                            bets[index] += trade_iteration[index]
                    try:
                        if deal['gaming']['azi_price'][index] >= 0:
                            pot += deal['gaming']['azi_price'][index]
                            bets[index] += deal['gaming']['azi_price'][index]
                    except:
                        pass
        winner_index = log[-1]['gaming']['winner']
        rates = [0, 0, 0, 0, 0, 0]
        for i in range(0, 6):
            if players[i] != 0:
                if i == winner_index:
                    profit[i] = pot - bets[i]
                    relative[i] = profit[i] / ante
                else:
                    profit[i] = 0 - bets[i]
                    relative[i] = profit[i] / ante
                stats = get_player_stats(players[i])
                rates[i] = stats.rate

        total_rate = sum(rates)
        expect_win = [0, 0, 0, 0, 0, 0]
        players_number = len(list(filter(lambda x: x != 0, players)))
        for i in range(0, 6):
            if players[i] != 0:
                expect_win[i] = 1 / (1 + 10 ** (((total_rate - rates[i])/(players_number - 1) - rates[i]) / 400)*(players_number - 1))

                if i == winner_index:
                    profit[i] = pot - bets[i]
                    relative[i] = profit[i] / ante
                else:
                    profit[i] = 0 - bets[i]
                    relative[i] = profit[i] / ante
        correction = (sum(expect_win) - 1)/players_number
        for k in range(0, 6):
            if expect_win[k] !=0:
                expect_win[k] -= correction

        new_rates = [0,0,0,0,0,0]
        max_relative = max(relative)
        for i in range(0, 6):
            relative_k[i] = abs(relative[i]/max_relative)
        K = 32  # Коэффициент К Эло
        for i in range(0, 6):
            if rates[i] != 0:
                if i == winner_index:
                    new_rates[i] = rates[i] + K * (1 - expect_win[i])
                else:
                    new_rates[i] = rates[i] + K * (0 - expect_win[i]*relative_k[i])
        rates_correction = (sum(new_rates) - sum(rates))/2
        for i in range(0, 6):
            if players[i] != 0:
                new_rates[i] -= rates_correction * relative_k[i]
        
        for i in range(0, 6):
            if players[i] != 0:
                try:                    
                    stats = get_player_stats(players[i])
                    if cointype == 0:
                        stats.games_silver += 1
                        stats.profit_silver += profit[i]
                        stats.relative_silver += relative[i]
                        if winner_index == i:
                            stats.wins_silver += 1
                    elif cointype == 1:
                        stats.games_gold += 1
                        stats.profit_gold += profit[i]
                        stats.relative_gold += relative[i]
                        if winner_index == i:
                            stats.wins_gold += 1
                    elif cointype == 2:
                        stats.games_bonus += 1
                        stats.profit_bonus += profit[i]
                        stats.relative_bonus += relative[i]
                        if winner_index == i:
                            stats.wins_bonus += 1
                    stats.rate = new_rates[i]
                    
                    game_log = {
                        "game_id": game_id,
                        "winner": winner_index == i,
                        "cointype": cointype,
                        "date": game_unixtime,
                        "profit": profit[i],
                        "relative": relative[i],
                        "rate_delta": new_rates[i] - rates[i]
                    }
                    stats.games_log.append(game_log)
                    
                    stats.save()
                except Exception as e:
                    print(f'DO GAME STATS - error Exception {e}')
                    pass

    except Exception as e:
        print(f'Stats of game {game_id} was not created - Exceptions is: {e}')