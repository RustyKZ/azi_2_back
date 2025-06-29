from players.models import Players
from games.models import Tables, Game
from .supply import *
from datetime import datetime, timezone
from .gaming import *

def get_tables_for_tables_hall():
    all_players = Players.objects.all()
    all_players_json = [
    {"id": p.id, "nickname": p.nickname, "active_table": p.active_table, "rating": p.rating, "reputation": p.reputation}
    for p in all_players
    ]
    all_tables = Tables.objects.all()    
    all_tables_json = [{
        "id": table.number, 
        "max_players": table.max_players,
        "drop_suit": table.drop_suit,
        "cointype": table.cointype,
        "min_bet": table.min_bet,
        "max_bet": table.max_bet,        
        "players": table.players,
        "blind_game": table.blind_game,        
        "players_now": table.players_now,
        "interval": table.interval,
        "protected": (table.table_password != '') and (table.table_password is not None)
        }
    for table in all_tables
    ]
    return {'status': True, "all_players": all_players_json, "all_tables": all_tables_json}

def get_table(table_id):
    try:
        table = Tables.objects.get(number=table_id)
        table_json = {
            "status": True,
            "id": table.number,
            "max_players": table.max_players,
            "drop_suit": table.drop_suit,
            "cointype": table.cointype,
            "min_bet": table.min_bet,
            "max_bet": table.max_bet,
            "players": table.players,
            "blind_game": table.blind_game,
            "players_now": table.players_now,
            "interval": table.interval,
            "table_password": table.table_password,
            "currentgame": table.currentgame,
            "time_stop": table.time_stop,
            "dealer": table.dealing,
            "players_nicknames": ['','','','','',''],
            'status': table.status,
            'lastdeal': table.lastdeal
        }
        #print(f'GET TABLE JSON: {table_json['players']}')
        for pn in range (6):
            if table_json['players'][pn] != 0:
                player = Players.objects.get(id=table_json['players'][pn])
                table_json['players_nicknames'][pn] = player.nickname
        return table_json
    except:
        print(f'GET TABLE JSON: NONE')
        return None

def get_game_for_playing_table(game_id):
    try:
        if game_id !=0:
            game = Game.objects.get(id=game_id)
            game_json = {
                "id": game.id,
                "table_id": game.table_id,
                "cointype": game.cointype,
                "players": game.players,
                "min_bet": game.min_bet,
                "drop_suit": game.drop_suit,
                "trump_suit": game.trump_suit,
                "pot": game.pot,
                "winner": game.winner,
                "card_players": cards_quntity(game.card_players),
                "card_place1": game.card_place1,
                "card_place2": game.card_place2,
                "card_place3": game.card_place3,
                "card_place": game.card_place,
                "cards_now": game.cards_now,
                "speaker": game.speaker,
                "speaker_id": game.speaker_id,
                "stage": game.stage,
                "players_bet": game.players_bet,
                "usersays": game.usersays,
                "top_bet": game.top_bet,
                "check_status": game.check_status,
                "status": game.status,
                "turn1win": game.turn1win,
                "turn2win": game.turn2win,
                "turn3win": game.turn3win,
                "current_hodor": game.current_hodor,
                "azi_price": game.azi_price,
                "usersays_value": game.usersays_value,
                "trump_value": game.card_players[24]
            }
            return game_json
        else:            
            game_json = {
                "id": 0,
                "stage": 0,
            }
            return game_json
    except:
        return None

def player_join_table(user_id, table_id, table_password):
    try:
        player = Players.objects.get(id=user_id)
        table = Tables.objects.get(number=table_id)
        table_players = table.players
        free_seat = any(p == 0 for p in table_players[:table.max_players])
        if (player.active_table != 0) and (player.active_table != -1) and (player.active_table != -2) and (player.active_table != table_id):
            return { "status": False, 'error': 702 }
        if not free_seat:
            return { "status": False, 'error': 700 }
        if table.table_password and table_password != table.table_password:
            return { "status": False, 'error': 704 }
        if (table.cointype == 0) and (player.silvercoin < table.min_bet):
            return { "status": False, 'error': 706 }
        if (table.cointype == 1) and (player.goldcoin < table.min_bet):
            return { "status": False, 'error': 706 }
        if (table.cointype == 2) and (player.bonuscoin < table.min_bet):
            return { "status": False, 'error': 706 }
        gamestage = 0
        if table.currentgame != 0:
            try:
                game = Game.objects.get(id=table.currentgame)
                gamestage = game.stage
            except:
                pass
        print(f'PLAYER JOIN TABLE: gamestage is {gamestage}')
        for r in range(0, table.max_players):
            if table_players[r] == user_id:
                return { "status": False, 'error': 701 }
        for i in range(0, table.max_players):
            if table_players[i] == 0:
                table_players[i] = user_id
                player.active_table = table_id
                table.players = table_players
                table.players_now = sum(1 for player in table_players[:table.max_players] if player != 0)
                table.time_stop = 0
                table.default_ready[i] = 0
                if table.players_now > 1 and (gamestage == 0 or gamestage == 12):
                    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
                    unix_time = int(current_time.timestamp())
                    table.lastdeal = unix_time
                player.save()
                table.save()
                coins = get_table_coins(table_id)
                return { 
                    'status': True,
                    'table': get_table(table_id),
                    'game': table.currentgame,
                    'coins': coins,
                }
    except:
        return { "status": False, 'error': 0 }
    
def player_leave_table(user_id, table_id):
    try:
        player = Players.objects.get(id=user_id)
        table = Tables.objects.get(number=table_id)
        player_index = table.players.index(user_id)
        coins = get_table_coins(table_id)
        if table.currentgame == 0:
            print(f'PLAYER LEAVE TABLE: IF in')
            table.players[player_index] = 0
            table.status[player_index] = 0
            player.active_table = 0
            table.players_now = sum(1 for pl in table.players[:table.max_players] if pl != 0)
            if table.players_now == 1:                    
                table.lastdeal = 0
            if table.players_now == 0:
                current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
                unix_time = int(current_time.timestamp())
                table.time_stop = unix_time
                table.lastdeal = 0
            player.save()
            table.save()
            print(f'PLAYER LEAVE TABLE: IF in before return')
            return { 
                'status': True,
                'table': get_table(table_id),
                'game': get_game_for_playing_table(table.currentgame),
                'coins': coins,
            }
        
        game = Game.objects.get(id=table.currentgame)        
        if not (game.stage == 0 or game.stage == 12):
            if user_id in game.players and table.status[player_index] in [2,3,4,5,6,7,9]:
                return { "status": False, 'error': 720 } #Error 720: You cannot leave the game you started until it ends            
        table.players[player_index] = 0
        table.status[player_index] = 0
        player.active_table = 0
        table.players_now = sum(1 for pl in table.players[:table.max_players] if pl != 0)
        if table.players_now == 1:                    
            table.lastdeal = 0
        if table.players_now == 0:
            current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
            unix_time = int(current_time.timestamp())
            table.time_stop = unix_time
            table.lastdeal = 0
        player.save()
        table.save()
        game.players[player_index] = 0
        for i in range(0, 4):
            game.card_players[player_index*4 + i] = 0
        if game.stage == 12 and game.winner == player_index:
            game.winner = -1
        if game.stage == 12 and game.turn1win == player_index:
            game.turn1win = -1
        if game.stage == 12 and game.turn2win == player_index:
            game.turn2win = -1
        if game.stage == 12 and game.turn3win == player_index:
            game.turn3win = -1
        game.save()
        return { 
            'status': True,
            'table': get_table(table_id),
            'game': get_game_for_playing_table(table.currentgame),
            'coins': coins,
        }
    except:
        print('PLAYER LEAVE TABLE - Except')
        return { "status": False, 'error': 0 }

def player_return_table(user_id, table_id):
    try:
        player = Players.objects.get(id=user_id)
        table = Tables.objects.get(number=table_id)
        table_players = table.players
        if (player.active_table != table_id):
            return { "status": False, 'error': 703 }
        for r in range(0, table.max_players):
            if table_players[r] == user_id:
                table.default_ready[r] = 0
                table.save()
                coins = get_table_coins(table_id)
                return { 
                    'status': True,
                    'table': get_table(table_id),
                    'game': get_game_for_playing_table(table.currentgame),
                    'coins': coins,
                }                
    except: 
        return { "status": False, 'error': 0 }

def update_table_data(table_id):
    try:
        table = Tables.objects.get(number=table_id)
        #print(f'UPDATE TABLE DATA - table is {table.number}')
        coins = get_table_coins(table_id)
        return { 
            'status': True,
            'table': get_table(table_id),
            'game': get_game_for_playing_table(table.currentgame),
            'coins': coins,
        }
    except:
        return { "status": False, 'error': 0 }

def player_ready_set_status(user_id, table_id):
    try:
        player = Players.objects.get(id=user_id)
        table = Tables.objects.get(number=table_id)
        players = table.players
        players_status = table.status
        player_index = players.index(player.id)
        print(f'PLAYER READY SET STATUS: user_id is {user_id} table is {table_id} | Player index is {player_index}')
        if not check_enough_coin(user_id, table_id, table.min_bet):
            players_status[player_index] = 12
            table.status = players_status
            table.default_ready[player_index] = 0
            table.save()
        else:
            players_status[player_index] = 1
            table.status = players_status
            table.default_ready[player_index] = 0
            table.save()
        coins = get_table_coins(table_id)
        return {
            'status': True,
            'table': get_table(table_id),
            'game': get_game_for_playing_table(table.currentgame),
            'coins': coins,
            'user_status': players_status[player_index]
        }
    except:
        return { "status": False, 'error': 0 }


# Обработка действия по умолчанию
def table_default_action(user_id, sid, table_id):    
    try:        
        player = Players.objects.get(id=user_id)
        table = Tables.objects.get(number=table_id)        
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        table_players = table.players
        if table.lastdeal + table.interval <= unix_time and user_id in table_players and player.sid == sid:
            table.lastdeal = unix_time
            table.save()            
            print(f'TABLE DEFAULT ACTION: table.lastdeal updated - {table.lastdeal} by {player.nickname}')
            return {
                'status': True,
            }
        else:
            print(f'TABLE DEFAULT ACTION: wrong actiavation by {player.nickname}')
            return { "status": False, 'error': 0 }        
    except:
        return { "status": False, 'error': 0 }


def player_blind_bet(user_id, table_id, blind_bet):
    try:        
        table = Tables.objects.get(number=table_id)
        blind_bet_value = blind_bet * table.min_bet
        if not check_enough_coin(user_id, table_id, blind_bet_value):
            return {"status": False, "error": 707}    
        else:
            if blind_betting(user_id, table_id, blind_bet_value):
                table_lastdeal_update(table_id)
                next_speaker(table.currentgame)
                return {"status": True}
            else:
                return {"status": False, "error": 0}
    except:
        return {"status": False, "error": 0}
    
def player_bet(user_id, table_id, bet):
    try:        
        table = Tables.objects.get(number=table_id)
        bet_value = bet * table.min_bet
        if not check_enough_coin(user_id, table_id, bet_value):
            return {"status": False, "error": 707}    
        else:
            if bet_betting(user_id, table_id, bet_value):
                table_lastdeal_update(table_id)
                next_speaker(table.currentgame)
                return {"status": True}
            else:
                return {"status": False, "error": 0}
    except:
        return {"status": False, "error": 0}
    
def player_raise(user_id, table_id, raise_bet):
    try:        
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)
        player_index = game.players.index(user_id)
        call_value = max(game.players_bet) - game.players_bet[player_index]
        bet_value = raise_bet * table.min_bet
        if not check_enough_coin(user_id, table_id, bet_value + call_value):
            return {"status": False, "error": 707}    
        else:
            if raise_betting(user_id, table_id, bet_value):
                table_lastdeal_update(table_id)
                next_speaker(table.currentgame)
                return {"status": True}
            else:
                print('PLAYER RAISE: else')
                return {"status": False, "error": 0}
    except:
        print('PLAYER RAISE: except')
        return {"status": False, "error": 0}
    
def player_call(user_id, table_id):
    try:        
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)
        player_index = game.players.index(user_id)
        call_value = max(game.players_bet) - game.players_bet[player_index]
        if call_value <= 0:
            return {"status": False, "error": 711}
        if not check_enough_coin(user_id, table_id, call_value):
            return {"status": False, "error": 707}
        else:
            if call_betting(user_id, table_id, call_value):
                table_lastdeal_update(table_id)
                if not trade_is_complete(game.id):
                    next_speaker(table.currentgame)
                return {"status": True}
            else:
                return {"status": False, "error": 0}
    except:
        return {"status": False, "error": 0}

def player_check(user_id, table_id):
    try:
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)
        if max(game.players_bet) != 0:
            return {"status": False, "error": 711}
        if check_betting(user_id, table_id):
            table_lastdeal_update(table_id)
            if not all_are_check(table.currentgame):
                next_speaker(table.currentgame)
            return {"status": True}
        else:
            return {"status": False, "error": 0}
    except:
        return {"status": False, "error": 0}

def player_fold(user_id, table_id):
    try:
        table = Tables.objects.get(number=table_id)
        game = Game.objects.get(id=table.currentgame)        
        if fold_betting(user_id, table_id):
            table_lastdeal_update(table_id)
            if all_fold_victory(table.currentgame):
                return {"status": True}
            if all_are_check(table.currentgame):    
                return {"status": True}
            if trade_is_complete(game.id):
                return {"status": True}            
            next_speaker(table.currentgame)
            return {"status": True}
        else:
            return {"status": False, "error": 0}
    except:
        return {"status": False, "error": 0}
    
def player_blind_check(user_id, table_id):
    try:        
        if blind_check(user_id, table_id):
            table_lastdeal_update(table_id)
            return {"status": True}
        else:
            return {"status": False, "error": 0}
    except:
        return {"status": False, "error": 0}

def get_user_cards(user_id, game_id):
    try:        
        game = Game.objects.get(id=game_id)
        try:
            index = game.players.index(user_id)
        except:
            return {"status": False, "error": 708}    
        cards = game.card_players[index*4:(index+1)*4]
        return {"status": True, "cards": cards}
    except:
        return {"status": False, "error": 0}


        
