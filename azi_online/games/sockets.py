import socketio
from django.conf import settings
from players.models import Players
from .player_actions import *
from .gaming import *

sio = socketio.Server(cors_allowed_origins=[settings.CLIENT_URL])


def update_test():
    print(f'SCHEDULER - Update test')
    sio.emit('update_test_connection', {"message": "SCHEDULER CHECKING..."}, room='tables_hall')

# SCHEDULER FUNCTION ----------------------------------------------------------------------------
def minute_scheduler():
    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    if current_time.minute == 18:
        if check_airdrops():
            print('MINUTE SCHEDULER: Airdrops complete!')
        else:
            print('MINUTE SCHEDULER: Airdrops not started!')
    if check_and_delete_verifications_code():
        print('MINUTE SCHEDULER: Player verification code was deleled!')
    if check_and_deposit_bots():
        print('MINUTE SCHEDULER: Bot accounts were replenished with democoins! ')
    
    if check_and_delete_tables():
        print('MINUTE SCHEDULER: Tables updated!')
        output_data = get_tables_for_tables_hall()
        print(f'MINUTE SCHEDULER - Output data: {output_data}')
        sio.emit('update_tables_hall_data', output_data, room='tables_hall')
#-----------------------------------------------------------------------------------------------

@sio.event
def test_connection(sid, input_data):
    #rooms = sio.manager.rooms.get(sid)
    rooms = sio.manager.get_rooms(sid,  namespace='/')
    print(f'socket IO test connection - SID is {sid}, Rooms is {rooms}')

@sio.event
def connect(sid, environ):
    print('GAMES Socket.io : Connected', sid)

@sio.event
def update_socket_sid(sid, input_data):
    print(f'UPDATE SOCKET SID - Input data: {input_data}')
    user_id = input_data['user_id']
    player = Players.objects.get(id=user_id)
    if player.id != 0:
        player.sid = sid
        player.save()
        print(f'UPDATE SOCKET SID: sid {sid} for player {player.nickname} updated successfully')

def leave_all_rooms(sid):
    # Получаем список комнат, в которых находится пользователь
    rooms = sio.manager.rooms.get(sid)
    if rooms:
        for room_id in rooms:
            # Покидаем каждую комнату
            sio.leave_room(sid, room_id)

@sio.event
def join_tables_hall(sid, input_data):
    room_id = 'tables_hall'
    user_id = input_data['user_id']
    leave_all_rooms(sid)
    sio.enter_room(sid, room_id)
    player = Players.objects.get(id=user_id)
    if player.active_table == 0:
        player.active_table = -1
        player.save()
        player_lastaction_update(user_id)
        output_data = get_tables_for_tables_hall()
        sio.emit('update_tables_hall_data', output_data, room=room_id)
        print('SOCKET IO JOIN TABLE HALL')
    else:
        output_data = get_tables_for_tables_hall()
        sio.emit('update_tables_hall_data', output_data, to=sid)
        print('SOCKET IO JOIN TABLE HALL update personally')

@sio.event
def leave_tables_hall(sid, input_data):
    room_id = 'tables_hall'
    user_id = input_data['user_id']
    sio.leave_room(sid, room_id)
    player = Players.objects.get(id=user_id)
    if player.active_table == -1:
        player.active_table = 0
        player.save()
        player_lastaction_update(user_id)
        output_data = get_tables_for_tables_hall()
        print(f'LEAVE TABLES HALL: {output_data}')
        sio.emit('update_tables_hall_data', output_data, room=room_id)
    else:
        output_data = get_tables_for_tables_hall()
        sio.emit('update_tables_hall_data', output_data, to=sid)
        print('SOCKET IO LEAVE TABLE HALL update personally')

@sio.event
def join_table_outside(sid, input_data):
    print(f'SOCKET IO JOIN TABLE OUTSIDE - Input Data: {input_data}')
    room_id = 'table-' + str(input_data['table_id'])
    user_id = input_data['user_id']
    table_id = input_data['table_id']
    table_password = input_data['table_password']
    output_data = player_join_table(user_id, table_id, table_password)
    print(f'SOCKET IO JOIN TABLE OUTSIDE - Output Data: {output_data}')
    if output_data['status']:
        sio.leave_room(sid, 'tables_hall')
        #sio.enter_room(sid, room_id)
        sio.emit('join_table_response', output_data, to=sid)
        output_tableshall_data = get_tables_for_tables_hall()
        sio.emit('update_tables_hall_data', output_tableshall_data, room='tables_hall')
    else:
        sio.emit('join_table_response', output_data, to=sid)

@sio.event
def join_table_inside(sid, input_data):
    print(f'SOCKET IO JOIN TABLE INSIDE - Input Data: {input_data}')
    room_id = 'table-' + str(input_data['table_id'])
    user_id = input_data['user_id']
    table_id = input_data['table_id']
    leave_all_rooms(sid)
    sio.enter_room(sid, room_id)
    player = Players.objects.get(id=user_id)
    player.sid = sid
    player.save()
    player_lastaction_update(user_id)
    update_frontend_table_data(table_id)


@sio.event
def leave_table(sid, input_data):
    room_id = 'table-' + str(input_data['table_id'])
    user_id = input_data['user_id']
    table_id = input_data['table_id']
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = player_leave_table(user_id, table_id)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:            
            sio.leave_room(sid, room_id)
            sio.emit('update_table_data', output_data, room=room_id)
            output_tableshall_data = get_tables_for_tables_hall()
            sio.emit('update_tables_hall_data', output_tableshall_data, room='tables_hall')
            player_lastaction_update(user_id)
            sio.emit('get_private_notice', {'status': True, 'error': 800} , to=sid) #Quit from the table
    current_gamestage(table_id)

@sio.event
def return_table(sid, input_data):
    print(f'SOCKET IO RETURN TABLE - Input Data: {input_data}')
    user_id = input_data['user_id']
    table_id = input_data['table_id']
    room_id = 'table-' + str(input_data['table_id'])
    output_data = player_return_table(user_id, table_id)
    if output_data['status']:
        leave_all_rooms(sid)
        sio.enter_room(sid, room_id)
        player = Players.objects.get(id=user_id)
        player.sid = sid
        player.save()
        player_lastaction_update(user_id)
    print(f'SOCKET IO RETURN TABLE - Output Data: {output_data}')
    sio.emit('update_table_data', output_data, to=sid)

@sio.event
def player_ready_for_the_new_game(sid, input_data):
    print(f'SOCKET IO PLAYER READY FOR THE NEW GAME - Input Data: {input_data}')
    user_id = input_data['user_id']
    table_id = input_data['table_id']
    room_id = 'table-' + str(input_data['table_id'])
    output_data = player_ready_set_status(user_id, table_id)
    sio.emit('update_table_data', output_data, room=room_id)
    if output_data['user_status'] == 12:
        sio.emit('get_private_notice', {'status': True, 'error': 706}, to=sid)
    player_lastaction_update(user_id)
    print(f'PLAYER READY {user_id} is ready for game at table {table_id}')
    current_gamestage(table_id)
    
def update_frontend_table_data(table_id):
    room_id = 'table-' + str(table_id)
    output_data = update_table_data(table_id)
    output_data['source'] = 'def UPDATE FORNTEND TABLE DATA'
    if output_data['status']:
        # print(f'UPDATE FRONTEND TABLE DATA - room: {room_id} Data: {output_data}')
        print (f'UPDATE FRONTEND TABLE DATA: Gamestage is {output_data['game']['stage']}')
        if output_data['game']['stage'] >= 3 and output_data['game']['stage'] <= 8:
            players = output_data['table']['players']
            max_players = output_data['table']['max_players']
            game_id = output_data['game']['id']
            for i in range(0, max_players):
                if players[i] != 0:
                    player = Players.objects.get(id=players[i])
                    sid = player.sid
                    player_cards = get_user_cards(player.id, game_id)
                    sio.emit('get_my_cards', player_cards , to=sid)
                    # print (f'UPDATE FRONTEND TABLE DATA: Player {player.nickname} recieved his cards: {player_cards}')
        sio.emit('update_table_data', output_data, room=room_id)

def update_frontend_turn(table_id, turn_player_index):
    room_id = 'table-' + str(table_id)
    output_data = update_table_data(table_id)
    output_data['source'] = 'def UPDATE FORNTEND TURN'
    output_data['turn_player_index'] = turn_player_index
    if output_data['status']:
        players = output_data['table']['players']
        max_players = output_data['table']['max_players']
        game_id = output_data['game']['id']
        for i in range(0, max_players):
            if players[i] != 0:
                player = Players.objects.get(id=players[i])
                sid = player.sid
                player_cards = get_user_cards(player.id, game_id)
                sio.emit('get_my_cards', player_cards , to=sid)
                # print (f'UPDATE FRONTEND TABLE DATA: Player {player.nickname} recieved his cards: {player_cards}')
        sio.emit('update_table_data', output_data, room=room_id)


@sio.event
def user_blind_bet(sid, data):
    table_id = data['table_id']
    user_id = data['user_id']
    blind_bet = data['blind_bet']
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = player_blind_bet(user_id, table_id, blind_bet)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            player_lastaction_update(user_id)
            update_frontend_table_data(table_id)
        print(f'USER BLIND BET: {output_data}')
    current_gamestage(table_id)

@sio.event
def user_blind_check(sid, data):
    table_id = data['table_id']
    user_id = data['user_id']    
    table = Tables.objects.get(number=table_id)
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        print(f'USER BLIND BET: User {user_id} checks blind bet at the table {table_id}')
        output_data = player_blind_check(user_id, table_id)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            player_lastaction_update(user_id)
            update_frontend_table_data(table_id)
    current_gamestage(table_id)

@sio.event
def user_bet(sid, data):
    table_id = data['table_id']
    user_id = data['user_id']
    bet = data['bet']
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = player_bet(user_id, table_id, bet)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            player_lastaction_update(user_id)
            update_frontend_table_data(table_id)
        print(f'USER BET: {output_data}')
    current_gamestage(table_id)

@sio.event
def user_raise(sid, data):
    table_id = data['table_id']
    user_id = data['user_id']
    raise_bet = data['raise_bet']
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = player_raise(user_id, table_id, raise_bet)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            player_lastaction_update(user_id)
            update_frontend_table_data(table_id)
        print(f'USER RAISE: {output_data}')
    current_gamestage(table_id)

@sio.event
def user_call(sid, data):
    table_id = data['table_id']
    user_id = data['user_id']    
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = player_call(user_id, table_id)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            player_lastaction_update(user_id)
            update_frontend_table_data(table_id)
        print(f'USER BET: {output_data}')
    current_gamestage(table_id)

@sio.event
def user_check(sid, data):
    table_id = data['table_id']
    user_id = data['user_id']    
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = player_check(user_id, table_id)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            player_lastaction_update(user_id)
            update_frontend_table_data(table_id)
        print(f'USER BET: {output_data}')
    current_gamestage(table_id)

@sio.event
def user_fold(sid, data):
    table_id = data['table_id']
    user_id = data['user_id']    
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = player_fold(user_id, table_id)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            player_lastaction_update(user_id)
            update_frontend_table_data(table_id)
        print(f'USER BET: {output_data}')
    current_gamestage(table_id)


@sio.event
def get_my_cards(sid, data):
    game_id = data['game_id']
    user_id = data['user_id']
    print(f'GET MY CARDS: User {user_id} requests cards in game {game_id}')
    output_data = get_user_cards(user_id, game_id)
    if not output_data['status']:
        sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
    else:
        print(f'GET MY CARDS: User {user_id} requests cards in game {game_id} - Recieved')
        sio.emit('get_my_cards', output_data , to=sid)

@sio.event
def user_drop_card(sid, data):
    game_id = data['game_id']
    user_id = data['user_id']
    card_pos = data['card_pos']
    game = Game.objects.get(id=game_id)
    table_id = game.table_id
    table = Tables.objects.get(number=table_id)

    print(f'USER DROP CARD: User {user_id} drops card {card_pos} in game {game_id}')
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        player_index = game.players.index(user_id)
        game.gaming['drop'][player_index] = game.card_players[player_index*4 + card_pos]
        game.card_players[player_index*4 + card_pos] = 0
        table.status[player_index] = 3        
        game.save()
        table.save()        
        player_lastaction_update(user_id)        
    check_drop_card_complete(game_id)
    update_frontend_table_data(table_id)
    current_gamestage(game.table_id)

@sio.event
def game_turn_1(sid, data):
    game_id = data['game_id']
    user_id = data['user_id']
    card_pos = data['card_pos']
    game = Game.objects.get(id=game_id)    
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        turn_1_result = turn_1(game_id, user_id, card_pos)
        if not turn_1_result['status']:
            sio.emit('get_private_notice', {'status': True, 'error': turn_1_result['error']} , to=sid)
        else:
            table_lastdeal_update(game.table_id)
            player_lastaction_update(user_id)
            last_speaker = game.speaker
            next_speaker(game_id)
            update_frontend_turn(game.table_id, last_speaker)
            sio.sleep(0.3)
    if check_turn_1_complete(game_id):
        sio.sleep(1)
        update_frontend_table_data(game.table_id)
        sio.sleep(1)
    current_gamestage(game.table_id)

@sio.event
def game_turn_2(sid, data):
    game_id = data['game_id']
    user_id = data['user_id']
    card_pos = data['card_pos']
    game = Game.objects.get(id=game_id)    
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        turn_2_result = turn_2(game_id, user_id, card_pos)
        if not turn_2_result['status']:
            sio.emit('get_private_notice', {'status': True, 'error': turn_2_result['error']} , to=sid)
        else:
            table_lastdeal_update(game.table_id)
            player_lastaction_update(user_id)
            last_speaker = game.speaker
            next_speaker(game_id)
            update_frontend_turn(game.table_id, last_speaker)
            sio.sleep(0.3)
    if check_turn_2_complete(game_id):
        sio.sleep(1)
        update_frontend_table_data(game.table_id)
        sio.sleep(1)
    current_gamestage(game.table_id)

@sio.event
def game_turn_3(sid, data):
    game_id = data['game_id']
    user_id = data['user_id']
    card_pos = data['card_pos']
    game = Game.objects.get(id=game_id)
    print(f'GAME TURN 3 socket: User {user_id} card pos {card_pos}')
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        turn_3_result = turn_3(game_id, user_id, card_pos)
        if not turn_3_result['status']:
            sio.emit('get_private_notice', {'status': True, 'error': turn_3_result['error']} , to=sid)
        else:
            table_lastdeal_update(game.table_id)
            player_lastaction_update(user_id)
            last_speaker = game.speaker
            next_speaker(game_id)
            update_frontend_turn(game.table_id, last_speaker)
            sio.sleep(0.3)
    if check_turn_3_complete(game_id):
        sio.sleep(1)
        update_frontend_table_data(game.table_id)
        sio.sleep(1)
    current_gamestage(game.table_id)

@sio.event
def user_azi_burst(sid, data):
    game_id = data['game_id']
    user_id = data['user_id']    
    game = Game.objects.get(id=game_id)
    player = Players.objects.get(id=user_id)
    print(f'USER AZI BURST: game #{game_id} user {user_id}')    
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        burst_in = player_azi_burst(game_id, user_id)
        if not burst_in['status']:
            sio.emit('get_private_notice', {'status': True, 'error': burst_in['error']} , to=sid)
        else:            
            player_lastaction_update(user_id)
            player_azi_in_checking(game_id)
            update_frontend_table_data(game.table_id)
    current_gamestage(game.table_id)

@sio.event
def user_azi_refuse(sid, data):
    game_id = data['game_id']
    user_id = data['user_id']    
    game = Game.objects.get(id=game_id)
    player = Players.objects.get(id=user_id)
    print(f'USER AZI REFUSE: game #{game_id} user {user_id}')    
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        refuse = player_azi_refuse(game_id, user_id)
        if not refuse['status']:
            sio.emit('get_private_notice', {'status': True, 'error': refuse['error']} , to=sid)
        else:            
            player_lastaction_update(user_id)
            player_azi_in_checking(game_id)
            update_frontend_table_data(game.table_id)
    current_gamestage(game.table_id)


@sio.event
def default_action(sid, input_data):
    user_id = input_data['user_id']
    table_id = input_data['table_id']    
    output_data =  table_default_action(user_id, sid, table_id)    
    if output_data['status']: 
        update_frontend_table_data(table_id) #temporary
        current_gamestage_default_action(table_id)
    else:
        update_frontend_table_data(table_id) #temporary
        print(f'def Default Action ERROR')

def update_players_status(table_id):
    table = Tables.objects.get(number=table_id)
    update_players = update_table_players_status(table_id)
    print(f'UPDATE PLAYERS STATUS - {update_players}')
    if update_players['status']:                    
        if update_players['drop']:
            droplist = update_players['droplist']
            for drop in droplist:
                drop_player = Players.objects.get(id=drop['user_id'])                            
                table.status[drop['index']] = 0
                table.players[drop['index']] = 0
                drop_player.active_table = -1
                table.players_now = sum(1 for pl in table.players[:table.max_players] if pl != 0)
                table.save()
                drop_player.save()
                leave_all_rooms(drop_player.sid)
                sio.enter_room(drop_player.sid, 'tables_hall')
                sio.emit('get_private_message', {'status': True, 'error': drop['error']} , to=drop_player.sid)
                print(f'GAMESTAGE 12: Drop player {drop_player.id}. Private_notice for {drop_player.sid}')
                output_tableshall_data = get_tables_for_tables_hall()
                sio.emit('update_tables_hall_data', output_tableshall_data, room='tables_hall')

def card_dealing_table_update(table_id, deal_card_player):
    room_id = 'table-' + str(table_id)
    output_data = update_table_data(table_id)
    output_data['source'] = 'def CARD DEALING TABLE UPDATE'
    output_data['index'] = deal_card_player
    print(f'CARD DEALING TABLE UPDATE - {deal_card_player}')
    if output_data['status']:
        # print(f'UPDATE FRONTEND TABLE DATA - room: {room_id} Data: {output_data}')
        sio.emit('update_table_data_cards', output_data, room=room_id)

def default_set_players_ready(table_id):
    try:
        table = Tables.objects.get(number=table_id)
        for i in range(0, table.max_players):
            if table.players[i] != 0 and table.status[i] == 0:
                player = Players.objects.get(id=table.players[i])
                no_coin = False
                if (table.cointype == 0 and player.silvercoin < table.min_bet) or (table.cointype == 1 and player.goldcoin < table.min_bet) or (table.cointype == 2 and player.bonuscoin < table.min_bet):
                    no_coin = True
                if no_coin:
                    table.status[i] = 12
                else:
                    table.default_ready[i] += 1
                    table.status[i] = 1
                    remaining = table.default_ready_limit - table.default_ready[i]
                    if remaining == 2:
                        error_number = 721
                    elif remaining == 1:
                        error_number = 722
                    else:
                        error_number = 723
                    sio.emit('get_private_notice', {'status': True, 'error': error_number} , to=player.sid)
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
        unix_time = int(current_time.timestamp())
        table.lastdeal = unix_time
        table.save()
    except:
        print('DEFAULT SET PLAYERS READY - Except')


"""
Этапы игры (game.stage)
0 - Ожидание решения играть/не играть
1 - Ожидание ставок Анте
2 - Ставки Анте сделаны
3 - Ставки втемную сделаны
4 - Карты розданы
5 - Ставки за первый ход сделаны, определены играющие и заходящий
6 - Лишняя карта сброшена
7 - Первый ход сделан
8 - Второй ход сделан
9 - Третий ход сделан, определен победитель или АЗИ
10 - Ожидание врезки в АЗИ
11- Все игроки пасы, зарыли, добавление анте
12- Ожидание начала следующей игры

# Статус игрока (table.status)
    # 0 - ожидание
    # 1 - готов к игре
    # 2 - сделана стартовая ставка Ante
    # 3 - окончены торги и сброшена карта
    # 4 - сделан 1-й ход
    # 5 - сделан 2-й ход
    # 6 - сделан 3-й ход
    # 7 - в Ази
    # 8 - вырезан из Ази
    # 9 - Вкупился в Ази
    # 10- Отказался от Ази
    # 11- Упал 
    # 12- Нет монет для игры    

"""


# Обработка этапов игры
def current_gamestage(table_id):
    gamestage_complete = False
    while not gamestage_complete:
        table = Tables.objects.get(number=table_id)
        game_id = table.currentgame
        if game_id == 0:
            print(f'CURRENT GAMESTAGE - game: {game_id}')
            if try_to_start_game(table_id):
                update_frontend_table_data(table_id)
                #current_gamestage(table_id)
            else:
                gamestage_complete = True
        else:
            game = Game.objects.get(id=game_id)
            print(f'CURRENT GAMESTAGE - gamestage: {game.stage}')
            # 0 - Ожидание решения играть/не играть
            if game.stage == 0:
                update_players_status(table_id)
                if try_to_start_game(table_id):
                    update_frontend_table_data(table_id)
                    #current_gamestage(table_id)
                else:
                    gamestage_complete = True
            #1 - Ожидание ставок Анте
            elif game.stage == 1:
                if not ante_all_bets_checking(game_id):
                    game_players = game.players
                    table_status = table.status
                    if game_players[game.speaker] != 0 and table_status[game.speaker] == 1:
                        ante_betting(game_id)
                    next_speaker(game_id)
                    update_frontend_table_data(table_id)
                    sio.sleep(1)
                else:
                    all_fold_victory(game_id)
                    update_frontend_table_data(table_id)
                #current_gamestage(table_id)
        #2 - Ставки Анте сделаны
            elif game.stage == 2:
                print(f'CURRENT GAMESTAGE - gamestage 2: ...')
                if not table.blind_game:
                    game.stage = 3
                    game.save()
                    update_frontend_table_data(table_id)
                    #current_gamestage(table_id)
                else:
                    gamestage_complete = True
            #3 - Ставки втемную сделаны - раздача карт
            elif game.stage == 3:
                game.speaker = -1
                game.save()
                print(f'CURRENT GAMESTAGE - gamestage 3: ... Dealing')
                if game.actual_deck is None:
                    create_actual_deck(game.id)
                else:
                    if dealing_is_complete(game_id):
                        game.stage = 4
                        game.speaker = game.players.index(game.speaker_id)
                        game.save()
                        table_lastdeal_update(game.table_id)
                        update_frontend_table_data(table_id)
                    else:
                        deal_card_player = deal_card(game_id)
                        if deal_card_player >=0 and deal_card_player <=5:
                            card_dealing_table_update(table_id, deal_card_player)
                        else:
                            update_frontend_table_data(table_id)
                        sio.sleep(0.2)
            
                #current_gamestage(table_id)
            elif game.stage == 4:
                print(f'CURRENT GAMESTAGE - gamestage 4: ... Trade open')
                gamestage_complete = True
            elif game.stage == 5:
                print(f'CURRENT GAMESTAGE - gamestage 5: ... Dropping card')
                gamestage_complete = True
            elif game.stage == 6:
                print(f'CURRENT GAMESTAGE - gamestage 6: ... First turn')
                #update_frontend_table_data(table_id)
                gamestage_complete = True
            elif game.stage == 7:
                print(f'CURRENT GAMESTAGE - gamestage 7: ... Second turn')
                gamestage_complete = True
            elif game.stage == 8:
                print(f'CURRENT GAMESTAGE - gamestage 8: ... Third turn')
                gamestage_complete = True
            elif game.stage == 9:
                print(f'CURRENT GAMESTAGE - gamestage 9: ... Checking winner or AZI detecting')
                gamestage_complete = True
            elif game.stage == 10:
                print(f'CURRENT GAMESTAGE - gamestage 10: ... AZI waiting')
                update_frontend_table_data(table_id)
                sio.sleep(2)
                player_azi_in_checking(game_id)            
                update_frontend_table_data(table_id)
                gamestage_complete = True
            elif game.stage == 11:
                print(f'CURRENT GAMESTAGE - gamestage 11: ... Re-betting Ante')
                if not ante_all_bets_checking(game_id):
                    game_players = game.players
                    table_status = table.status
                    if game_players[game.speaker] != 0 and table_status[game.speaker] == 1:
                        ante_betting(game_id)
                    next_speaker(game_id)
                    update_frontend_table_data(table_id)
                    sio.sleep(1)
                    #current_gamestage(table_id)
                else:
                    if not all_fold_victory(game_id):
                        game.stage = 3
                        game.actual_deck = None
                        game.card_players = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        game.save()
                    update_frontend_table_data(table_id)
                    #current_gamestage(table_id)
            elif game.stage == 12:
                update_players_status(table_id)
                update_frontend_table_data(table_id)
                if try_to_start_game(table_id):
                    update_frontend_table_data(table_id)
                    #current_gamestage(table_id)
                else:
                    gamestage_complete = True
    if game_id == 0:
        print(f'def CURRENT GAMESTAGE is OVER, game is 0')
    else:
        game = Game.objects.get(id=game_id)
        print(f'def CURRENT GAMESTAGE is OVER, game is {game.id}, stage is {game.stage}')

# Обработка этапов игры при действии по умолчанию
def current_gamestage_default_action(table_id):
    table = Tables.objects.get(number=table_id)
    game_id = table.currentgame
    if game_id == 0:
        print(f'CURRENT GAMESTAGE DEFAULT ACTION - game: {game_id}')
        update_players_status(table_id)
        if try_to_start_game(table_id):
            update_frontend_table_data(table_id)
        else:
            default_set_players_ready(table_id)
            current_gamestage(table_id)
    else:
        game = Game.objects.get(id=game_id)
        print(f'CURRENT GAMESTAGE DEFAULT ACTION - gamestage: {game.stage}')
        if game.stage == 0:
            update_players_status(table_id)
            default_set_players_ready(table_id)
            current_gamestage(table_id)
        elif game.stage == 1:
            print(f'CURRENT GAMESTAGE DEFAULT ACTION - gamestage 1: ...')
            current_gamestage(table_id)
        elif game.stage == 2:
            print(f'CURRENT GAMESTAGE DEFAULT ACTION - gamestage 2: ...')
            if not table.blind_game:
                game.stage = 3
                game.save()
                update_frontend_table_data(table_id)                
            else:
                default_blind_check(table_id)            
            current_gamestage(table_id)
        elif game.stage == 4:
            print(f'CURRENT GAMESTAGE DEFAULT ACTION - gamestage 4: ...')
            default_betting_player(table_id)
            update_frontend_table_data(table_id)
            current_gamestage(table_id)
        elif game.stage == 5:
            print(f'CURRENT GAMESTAGE - gamestage 5: ... Dropping card')
            default_card_dropping_players(table_id)
            check_drop_card_complete(game_id)
            current_gamestage(table_id)
        elif game.stage == 6:
            print(f'CURRENT GAMESTAGE - gamestage 6: ... First turn')
            default_turn_player(table_id)
            last_speaker = game.speaker
            next_speaker(game_id)
            check_turn_1_complete(game_id)
            update_frontend_turn(table_id, last_speaker)
            current_gamestage(table_id)
        elif game.stage == 7:
            print(f'CURRENT GAMESTAGE - gamestage 7: ... Second turn')
            default_turn_player(table_id)
            last_speaker = game.speaker
            next_speaker(game_id)
            check_turn_2_complete(game_id)
            update_frontend_turn(table_id, last_speaker)
            current_gamestage(table_id)
        elif game.stage == 8:
            print(f'CURRENT GAMESTAGE - gamestage 8: ... Third turn')
            default_turn_player(table_id)
            last_speaker = game.speaker
            next_speaker(game_id)
            check_turn_3_complete(game_id)
            update_frontend_turn(table_id, last_speaker)
            current_gamestage(table_id)
        elif game.stage == 9:
            print(f'CURRENT GAMESTAGE - gamestage 9: ... Checking winner or AZI detecting')
            update_frontend_table_data(table_id)
        elif game.stage == 10:
            print(f'CURRENT GAMESTAGE - gamestage 10: ... AZI waiting')
            default_players_azi_decline(table_id)
            update_frontend_table_data(table_id)
            current_gamestage(table_id)
        elif game.stage == 12:
            update_players_status(table_id)
            default_set_players_ready(table_id)
            current_gamestage(table_id)

#-----------------------------------------------------------------------------------------------------
            
@sio.event
def create_new_table(sid, data):    
    user_id = data['user_id']
    new_table = data['new_table']
    print(f'CREATE NEW TABLE: user {user_id} sid is {sid} created new table: {new_table}')
    player = Players.objects.get(id=user_id)    
    if player.sid != sid:
        sio.emit('get_private_message', {'status': True, 'error': 710} , to=sid)
    else:
        result = start_new_table(new_table)
        if not result['status']:            
            sio.emit('new_game_created', {'status': False, 'table_created': result} , to=sid)
            print(f'CREATE NEW TABLE error: {result}')
        else:
            room_id = 'table-' + str(result['table_id'])            
            leave_all_rooms(sid)
            sio.enter_room(sid, room_id)
            player = Players.objects.get(id=user_id)
            player.sid = sid
            player.save()
            player_lastaction_update(user_id)            
            sio.emit('new_game_created', {'status': True, 'table_created': result} , to=sid)
            output_tableshall_data = get_tables_for_tables_hall()
            sio.emit('update_tables_hall_data', output_tableshall_data, room='tables_hall')

# SANDBOX GAME ----------------------------------------------------------------------------------------

@sio.event
def join_sandbox_outside(sid, input_data):
    print(f'SOCKET IO JOIN SANDBOX OUTSIDE - Input Data: {input_data}')
    user_id = input_data['user_id']    
    player = Players.objects.get(id=user_id)
    leave_all_rooms(sid)
    player.active_table = -2
    player.save()
    output_tableshall_data = get_tables_for_tables_hall()
    sio.emit('update_tables_hall_data', output_tableshall_data, room='tables_hall')
    sio.emit('join_sandbox_response', {"status": True}, to=sid)

@sio.event
def leave_sandbox(sid, input_data):
    user_id = input_data['user_id']
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        player.active_table = -1
        player.save()
        sio.enter_room(sid, 'tables_hall')
        player_lastaction_update(user_id)
        output_tableshall_data = get_tables_for_tables_hall()
        sio.emit('update_tables_hall_data', output_tableshall_data, room='tables_hall')
        player_lastaction_update(user_id)
        sio.emit('get_private_notice', {'status': True, 'error': 800} , to=sid) #Quit from the table

@sio.event
def close_sandbox(sid, input_data):
    user_id = input_data['user_id']
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        player.active_table = -1
        player.save()
        sio.enter_room(sid, 'tables_hall')
        player_lastaction_update(user_id)
        output_tableshall_data = get_tables_for_tables_hall()
        sio.emit('update_tables_hall_data', output_tableshall_data, room='tables_hall')
        player_lastaction_update(user_id)
        sio.emit('get_private_notice', {'status': True, 'error': 800} , to=sid) #Quit from the table
        game = SandboxGame.objects.get(user_id=user_id)
        game.delete()


@sio.event
def join_sandbox_inside(sid, input_data):
    print(f'SOCKET IO JOIN SANDBOX INSIDE - Input Data: {input_data}')
    user_id = input_data['user_id']    
    player = Players.objects.get(id=user_id)
    leave_all_rooms(sid)
    player_lastaction_update(user_id)
    player.sid = sid
    player.save()
    output_data = get_sandbox_game(user_id)
    if output_data['status']:
        sio.emit('update_sandbox_game', output_data, to=sid)

@sio.event
def update_sandbox_request(sid):
    try:
        player = Players.objects.get(sid=sid)
        output_data = get_sandbox_game(player.id)
        if output_data['status']:
            sio.emit('update_sandbox_game', output_data, to=player.sid)
    except:
        pass

def update_sandbox_game(user_id):
    player = Players.objects.get(id=user_id)
    try:
        output_data = get_sandbox_game(user_id)
        if output_data['status']:
            sio.emit('update_sandbox_game', output_data, to=player.sid)
    except:
        pass

def sandbox_update_frontend_turn(user_id, turn_player_index):
    try:
        output_data = get_sandbox_game(user_id)
        output_data['turn_player_index'] = turn_player_index
        if output_data['status']:
            player = Players.objects.get(id=user_id)            
            sio.emit('update_sandbox_game', output_data, to=player.sid)
    except:
        pass    
    

@sio.event
def sandbox_change_rivals(sid, data):    
    user_id = data['user_id']
    max_players = data['max_players']
    player_lastaction_update(user_id)
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_message', {'status': True, 'error': 710} , to=sid)
    else:
        result = player_sandbox_change_rivals(user_id, max_players)
        if not result['status']:            
            sio.emit('get_private_message', {'status': True, 'error': 0} , to=sid)
        else:
            update_sandbox_game(user_id)

@sio.event
def sandbox_start_game(sid, data):
    user_id = data['user_id']
    game = data['game']
    print(f'SANDBOX START GAME: User {user_id} starts new game- {game}')
    player_lastaction_update(user_id)
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_message', {'status': True, 'error': 710} , to=sid)
    else:
        result = player_sandbox_start_game(game)
        if not result['status']:
            sio.emit('get_private_notice', {'status': True, 'error': result['error']} , to=sid)
        else:
            sandbox_set_speaker(user_id)
            print('SANDBOX START GAME - speaker is set')
            update_sandbox_game(user_id)            
            sandbox_current_gamestage(user_id)

@sio.event
def sandbox_user_blind_bet(sid, data):    
    user_id = data['user_id']
    blind_bet = data['blind_bet']
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = sandbox_player_blind_bet(user_id, blind_bet)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            player_lastaction_update(user_id)
            update_sandbox_game(user_id)        
    update_sandbox_game(user_id)
    sandbox_current_gamestage(user_id)

@sio.event
def sandbox_user_blind_check(sid, data):    
    user_id = data['user_id']        
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        print(f'USER BLIND BET: User {user_id} checks blind bet at the table SANDBOX')
        output_data = sandbox_player_blind_check(user_id)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            player_lastaction_update(user_id)
            update_sandbox_game(user_id)
    sandbox_current_gamestage(user_id)

@sio.event
def sandbox_user_bet(sid, data):
    user_id = data['user_id']
    bet = data['bet']
    print(f'SANDBOX BET - {data}')    
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = sandbox_someone_bet(user_id, bet, 0)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            print('call NEXT speaker - 1')
            sandbox_nextspeaker(user_id)
            player_lastaction_update(user_id)
            update_sandbox_game(user_id)
        print(f'USER BET: {output_data}')
    sandbox_current_gamestage(user_id)

@sio.event
def sandbox_user_raise(sid, data):
    user_id = data['user_id']
    raise_bet = data['raise_bet']
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = sandbox_someone_raise(user_id, raise_bet, 0)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            print('call NEXT speaker - 2')
            sandbox_nextspeaker(user_id)
            player_lastaction_update(user_id)
            update_sandbox_game(user_id)
        print(f'USER RAISE: {output_data}')
    sandbox_current_gamestage(user_id)

@sio.event
def sandbox_user_call(sid, data):
    user_id = data['user_id']    
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = sandbox_someone_call(user_id, 0)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)            
        else:
            if not sandbox_trade_is_complete(user_id):
                print('call NEXT speaker - 3')
                sandbox_nextspeaker(user_id)
            player_lastaction_update(user_id)
            update_sandbox_game(user_id)        
    sandbox_current_gamestage(user_id)

@sio.event
def sandbox_user_check(sid, data):
    print('SANDBOX USER CHECK')    
    user_id = data['user_id']    
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = sandbox_someone_check(user_id, 0)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            if not sandbox_all_are_check(user_id):
                print('call NEXT speaker - 4')
                sandbox_nextspeaker(user_id)
            player_lastaction_update(user_id)
            update_sandbox_game(user_id)
    sandbox_current_gamestage(user_id)

@sio.event
def sandbox_user_fold(sid, data):
    print('SANDBOX USER FOLD')
    user_id = data['user_id']    
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        output_data = sandbox_someone_fold(user_id, 0)
        if not output_data['status']:
            sio.emit('get_private_notice', {'status': True, 'error': output_data['error']} , to=sid)
        else:
            if sandbox_all_fold_victory(user_id):
                update_sandbox_game(user_id)
                sandbox_current_gamestage(user_id)
            elif sandbox_all_are_check(user_id):    
                update_sandbox_game(user_id)
                sandbox_current_gamestage(user_id)
            elif sandbox_trade_is_complete(user_id):
                update_sandbox_game(user_id)
                sandbox_current_gamestage(user_id)
            print('call NEXT speaker - 5')
            sandbox_nextspeaker(user_id)
            player_lastaction_update(user_id)
            update_sandbox_game(user_id)
    sandbox_current_gamestage(user_id)
    




#--------------------------------------------------------
@sio.event
def sandbox_goto_currentgamestage(sid, data):
    user_id = data['user_id']
    print(f'Manual SANDBOX CURRENT GAMESTAGE ACTIVATED...')
    game = SandboxGame.objects.get(user_id=user_id)
    game.stage = 12
    game.save()
    sandbox_current_gamestage(user_id)
            
def update_sandbox_game_dealing(user_id, deal_card_player):
    player = Players.objects.get(id=user_id)    
    output_data = get_sandbox_game(user_id)    
    output_data['index'] = deal_card_player    
    if output_data['status']:        
        sio.emit('update_table_data_cards', output_data, to=player.sid)

@sio.event
def sandbox_user_drop_card(sid, data):    
    user_id = data['user_id']
    card_pos = data['card_pos']
    game = SandboxGame.objects.get(user_id=user_id)
    print(f'SANDBOX USER DROP CARD: User {user_id} drops card {card_pos} in game SANDBOX')
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        print(f'SANDBOX USER DROP CARD: ELSE')
        player_index = 0        
        game.card_players[card_pos] = 0
        game.status[player_index] = 3        
        game.save()        
        player_lastaction_update(user_id)
        update_sandbox_game(user_id)
    sandbox_check_drop_card_complete(user_id)
    sandbox_current_gamestage(user_id)

@sio.event
def sandbox_game_turn_1(sid, data):    
    user_id = data['user_id']
    card_pos = data['card_pos']
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        turn_1_result = sandbox_turn_1(user_id, card_pos)
        if not turn_1_result['status']:
            sio.emit('get_private_notice', {'status': True, 'error': turn_1_result['error']} , to=sid)
        else:            
            player_lastaction_update(user_id)
            print('call NEXT speaker - 6')
            sandbox_nextspeaker(user_id)
            update_sandbox_game(user_id)
            sio.sleep(0.3)
    print(f'turn1 - SANDBOX - User getting card...')
    if sandbox_check_turn_1_complete(user_id):
        print(f'turn1 - SANDBOX - turn 1 is compelte (finished by user)')
        sio.sleep(1)
        update_sandbox_game(user_id)
        sio.sleep(1)
    sandbox_current_gamestage(user_id)

@sio.event
def sandbox_game_turn_2(sid, data):    
    user_id = data['user_id']
    card_pos = data['card_pos']
    print(f'SANDBOX TURN 2 USER : {user_id}, card {card_pos}')
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        turn_2_result = sandbox_turn_2(user_id, card_pos)
        if not turn_2_result['status']:
            sio.emit('get_private_notice', {'status': True, 'error': turn_2_result['error']} , to=sid)
        else:            
            player_lastaction_update(user_id)
            print('call NEXT speaker - 7')
            sandbox_nextspeaker(user_id)
            update_sandbox_game(user_id)
            sio.sleep(0.3)
    if sandbox_check_turn_2_complete(user_id):
        sio.sleep(1)
        update_sandbox_game(user_id)
        sio.sleep(1)
    sandbox_current_gamestage(user_id)

@sio.event
def sandbox_game_turn_3(sid, data):    
    user_id = data['user_id']
    card_pos = data['card_pos']
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        turn_3_result = sandbox_turn_3(user_id, card_pos)
        if not turn_3_result['status']:
            sio.emit('get_private_notice', {'status': True, 'error': turn_3_result['error']} , to=sid)
        else:            
            player_lastaction_update(user_id)
            print('call NEXT speaker - 8')
            sandbox_nextspeaker(user_id)
            update_sandbox_game(user_id)
            sio.sleep(0.3)
    if sandbox_check_turn_3_complete(user_id):
        sio.sleep(1)
        update_sandbox_game(user_id)
        sio.sleep(1)
    sandbox_current_gamestage(user_id)

@sio.event
def sandbox_user_azi_burst(sid, data):    
    user_id = data['user_id']        
    player = Players.objects.get(id=user_id)
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        burst_in = sandbox_player_azi_burst(user_id, 0)
        if not burst_in['status']:
            sio.emit('get_private_notice', {'status': True, 'error': burst_in['error']} , to=sid)
        else:            
            player_lastaction_update(user_id)
            sandbox_player_azi_in_checking(user_id)
    update_sandbox_game(user_id)
    sandbox_current_gamestage(user_id)

@sio.event
def sandbox_user_azi_refuse(sid, data):    
    user_id = data['user_id']        
    player = Players.objects.get(id=user_id)    
    if player.sid != sid:
        sio.emit('get_private_notice', {'status': True, 'error': 710} , to=sid)
    else:
        refuse = sandbox_player_azi_refuse(user_id, 0)
        if not refuse['status']:
            sio.emit('get_private_notice', {'status': True, 'error': refuse['error']} , to=sid)
        else:            
            player_lastaction_update(user_id)
            sandbox_player_azi_in_checking(user_id)
    update_sandbox_game(user_id)
    sandbox_current_gamestage(user_id)


def sandbox_current_gamestage(user_id):
    gamestage_complete = False
    gamestage_iteration = 0
    print(f'\n+++++++++++++++++++++++++ SANDBOX CURRENT GAMESTAGE +++++++++++++++++++++++++ Start function - gamestage_complete: {gamestage_complete}')
    while not gamestage_complete:
        if gamestage_iteration >= 1000:
            print('!!!!!!!!!!!!!! ERRROR ---------- SANDBOX GAMESTAGE - ITERATIONS LIMIT !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            break
        game = SandboxGame.objects.get(user_id=user_id)
        # 0 - Ожидание решения играть/не играть
        if game.stage == 0:
            pass
        #1 - Ожидание ставок Анте
        elif game.stage == 1:
            while game.stage == 1:
                game = SandboxGame.objects.get(user_id=user_id)
                print('SANDBOX GAME STAGE 1')
                if not sandbox_ante_checking(user_id):
                    if game.players[game.speaker] != -1 and game.status[game.speaker] == 1:
                        sandbox_antebetting(user_id)
                    print(f'CGS#1 - stage is {game.stage}')
                    print('call NEXT speaker - 9')
                    sandbox_nextspeaker(user_id)
                    update_sandbox_game(user_id)
                    sio.sleep(1)
                else:
                    sandbox_all_fold_victory(user_id)
                    update_sandbox_game(user_id)
                game = SandboxGame.objects.get(user_id=user_id)
        #2 - Ставки Анте сделаны
        elif game.stage == 2:
            if not game.blind_game:
                game.stage = 3
                game.save()
                update_sandbox_game(user_id)
            elif game.blind_complete:
                game.stage = 3
                game.save()
                update_sandbox_game(user_id)
            elif game.speaker == 0:
                gamestage_complete = True
            else:
                while game.stage == 2:
                    game = SandboxGame.objects.get(user_id=user_id)
                    print('SANDBOX GAME STAGE 2')
                    if game.blind_complete:                       
                        print('CGS#2 - game.blind_complete - True')
                        game.stage = 3
                        game.save()
                        update_sandbox_game(user_id)
                        break
                    else:
                        if game.speaker > 0 and not game.blind_complete: 
                            blind_bet = bot_blind_bet(user_id)
                            print(f'SGS2 - Blind_bet is {blind_bet}; Gamestage is {game.stage}')
                            if blind_bet['status']:
                                if blind_bet['bet']:
                                    print('CGS - BOT ACTION - Blind bet - nextspeaker')
                                    print('call NEXT speaker - 10')
                                    sandbox_nextspeaker(user_id)
                                    game = SandboxGame.objects.get(user_id=user_id)
                                else:
                                    print('CGS - BOT ACTION - Blind bet - no nextspeaker')
                            update_sandbox_game(user_id)
                            sio.sleep(1)
                            break                
        #3 - Ставки втемную сделаны - раздача карт
        elif game.stage == 3:
            while game.stage == 3:
                game = SandboxGame.objects.get(user_id=user_id)
                #print('SANDBOX GAME STAGE 3')
                game.speaker = -1
                game.save()        
                if game.actual_deck is None:
                    sandbox_create_actual_deck(user_id)
                    break
                else:
                    if sandbox_dealing_is_complete(user_id):
                        game.stage = 4
                        game.speaker = game.players.index(game.speaker_id)
                        game.save()
                        update_sandbox_game(user_id)                        
                    else:
                        deal_card_player = sandbox_deal_card(user_id)
                        if deal_card_player >=0 and deal_card_player <=5:
                            update_sandbox_game_dealing(user_id, deal_card_player)
                        else:
                            update_sandbox_game(user_id)
                        sio.sleep(0.2)            
                        break
                game = SandboxGame.objects.get(user_id=user_id)
        elif game.stage == 4:
            while game.stage == 4 and game.speaker > 0:
                game = SandboxGame.objects.get(user_id=user_id)
                print(f'SANDBOX GAME STAGE 4 - Trading -------------------- speaker is {game.speaker}')
                if game.speaker > 0:
                    print(f'SANDBOX GAME STAGE 4 - Speaker is {game.speaker}')
                    ai_solution = bot_solution_trade(user_id)            
                    if ai_solution['solution'] == 'bet':
                        ai_turn = sandbox_someone_bet(user_id, ai_solution['value'], game.speaker)
                    elif ai_solution['solution'] == 'check':
                        ai_turn = sandbox_someone_check(user_id, game.speaker)
                    elif ai_solution['solution'] == 'fold':
                        ai_turn = sandbox_someone_fold(user_id, game.speaker)
                    elif ai_solution['solution'] == 'call':
                        ai_turn = sandbox_someone_call(user_id, game.speaker)
                    elif ai_solution['solution'] == 'raise':
                        ai_turn = sandbox_someone_raise(user_id, ai_solution['value'], game.speaker)
                    print(f'SANDBOX CGS #4 Ai {game.speaker} turn is {ai_turn['status']:}')

                    if ai_turn['status']:
                        update_sandbox_game(user_id)
                        sio.sleep(1)
                        if sandbox_all_fold_victory(user_id):
                            update_sandbox_game(user_id)
                            break
                        elif sandbox_all_are_check(user_id):
                            update_sandbox_game(user_id)
                            break
                        elif sandbox_trade_is_complete(user_id):
                            update_sandbox_game(user_id)
                            break
                        print(f'SANDBOX GAME STAGE 4 - Speaker update: current speaker is {game.speaker}')
                        print('call NEXT speaker - 11')
                        sandbox_nextspeaker(user_id)
                        update_sandbox_game(user_id)
                        game = SandboxGame.objects.get(user_id=user_id)
                    break
                else:
                    print(f'SANDBOX GAME STAGE 4 - BREAK - speaker is {game.speaker}')
                    game = SandboxGame.objects.get(user_id=user_id)
                    break                
            if game.speaker == 0:
                gamestage_complete = True
        elif game.stage == 5:
            game = SandboxGame.objects.get(user_id=user_id)
            bots_all_drops_card = False
            while not bots_all_drops_card:
                print('SANDBOX GAME STAGE 5')
                sandbox_bots_card_dropping(user_id)
                update_sandbox_game(user_id)
                bots_all_drops_card = sandbox_check_bots_drop_card_complete(user_id)
                game = SandboxGame.objects.get(user_id=user_id)
            if not 0 in game.card_players[:4] or game.status[0] == 2:
                gamestage_complete = True
            sandbox_check_drop_card_complete(user_id)
        elif game.stage == 6:
            while game.stage == 6:
                game = SandboxGame.objects.get(user_id=user_id)
                update_sandbox_game(user_id)
                print('SANDBOX GAME STAGE 6 - Turn #1 -----------------------------------------------')
                if game.speaker > 0:
                    if game.status[game.speaker] == 3:
                        sandbox_bot_turn1(user_id)
                        last_speaker = game.speaker
                        sandbox_update_frontend_turn(user_id, last_speaker)
                        print('call NEXT speaker - 12')
                        sandbox_nextspeaker(user_id)
                        sio.sleep(0.5)                        
                        if sandbox_check_turn_1_complete(user_id):
                            sio.sleep(1)
                            update_sandbox_game(user_id)
                            sio.sleep(1)
                            break
                elif game.speaker == 0:
                    gamestage_complete = True
                    break
                game = SandboxGame.objects.get(user_id=user_id)                
        elif game.stage == 7:
            while game.stage == 7:
                game = SandboxGame.objects.get(user_id=user_id)
                print('SANDBOX GAME STAGE 7 - Turn #2 -----------------------------------------------')
                update_sandbox_game(user_id)
                if game.speaker > 0:
                    if game.status[game.speaker] == 4:
                        sandbox_bot_turn2(user_id)
                        last_speaker = game.speaker
                        sandbox_update_frontend_turn(user_id, last_speaker)
                        print('call NEXT speaker - 13')
                        sandbox_nextspeaker(user_id)
                        sio.sleep(0.5)                        
                        if sandbox_check_turn_2_complete(user_id):
                            sio.sleep(1)
                            update_sandbox_game(user_id)                
                            sio.sleep(1)
                            break
                elif game.speaker == 0:
                    gamestage_complete = True
                    break
                game = SandboxGame.objects.get(user_id=user_id)            
        elif game.stage == 8:
            while game.stage == 8:
                game = SandboxGame.objects.get(user_id=user_id)
                print('SANDBOX GAME STAGE 8 - Turn #3 -----------------------------------------------')
                update_sandbox_game(user_id)
                if game.speaker > 0:
                    if game.status[game.speaker] == 5:
                        sandbox_bot_turn3(user_id)
                        last_speaker = game.speaker
                        sandbox_update_frontend_turn(user_id, last_speaker)
                        print('call NEXT speaker - 14')                
                        sandbox_nextspeaker(user_id)
                        sio.sleep(0.5)            
                        if sandbox_check_turn_3_complete(user_id):
                            sio.sleep(1)
                            update_sandbox_game(user_id)
                            sio.sleep(1)
                            break
                elif game.speaker == 0:
                    gamestage_complete = True
                    break
                game = SandboxGame.objects.get(user_id=user_id)            
        elif game.stage == 9:
            game = SandboxGame.objects.get(user_id=user_id)
            print('SANDBOX GAME STAGE 9 ------------------- winner or AZI Detecting')
            if (game.turn1win == game.turn2win) or (game.turn1win == game.turn3win) or (game.turn2win == game.turn3win):
                sandbox_end_game(user_id)
            else:
                sandbox_azi_start(user_id)
        
        elif game.stage == 10:
            print('SANDBOX GAME STAGE 10 - AZI waiting ------------------------------------------')
            game = SandboxGame.objects.get(user_id=user_id)
            game.speaker = -1
            update_sandbox_game(user_id)
            sio.sleep(1)

            for bot_no in range(1, game.max_players):
                if game.players[bot_no] != -1 and game.status[bot_no] in [8, 11]:
                    if sandbox_get_bot_azi_solution(user_id, bot_no):
                        sandbox_bot_azi_burst(user_id, bot_no)
                    else:
                        sandbox_bot_azi_refuse(user_id, bot_no)
            update_sandbox_game(user_id)        
            sio.sleep(1)

            if game.status[0] in [8, 11]:
                gamestage_complete = True
                update_sandbox_game(user_id)
            else:
                sandbox_player_azi_in_checking(user_id)
                update_sandbox_game(user_id)

        elif game.stage == 11:
            print('SANDBOX GAME STAGE 11 - Re-betting Ante --------------------------------------')
            while game.stage == 11:
                game = SandboxGame.objects.get(user_id=user_id)                
                if not sandbox_ante_checking(user_id):
                    if game.players[game.speaker] != -1 and game.status[game.speaker] == 1:
                        sandbox_antebetting(user_id)
                    print(f'CGS#1 - stage is {game.stage}')
                    print('call NEXT speaker - 9')
                    sandbox_nextspeaker(user_id)
                    update_sandbox_game(user_id)
                    sio.sleep(1)
                else:
                    if not sandbox_all_fold_victory(user_id):
                        game.stage = 3
                        game.actual_deck = None
                        game.card_players = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        game.save()
                    update_sandbox_game(user_id)
                game = SandboxGame.objects.get(user_id=user_id)
        elif game.stage == 12:
            game = SandboxGame.objects.get(user_id=user_id)
            print('SANDBOX GAME STAGE 12 - END GAME -------------------------------------------------')
            sio.sleep(2)
            sandbox_fill_table(user_id)
            update_sandbox_game(user_id)
            gamestage_complete = True
        if gamestage_complete:
            game = SandboxGame.objects.get(user_id=user_id)
            print(f'--------------- gamestage {game.stage} is complete !!! -------------------------------------------------------------------------------')
        else:
            gamestage_iteration += 1
            if game.stage != 3:
                game = SandboxGame.objects.get(user_id=user_id)
                print(f'--------------- gamestage {game.stage} is not complete !!! Repeat iteration ----------------------------------------------------------')
    print(f'************ END OF FUNCTION - SANDBOX CURRENT GAMESTAGE: stage is {game.stage}, Speaker is {game.speaker} | speaker_ID is {game.speaker_id}\n')

"""
Этапы игры (game.stage)
0 - Ожидание решения играть/не играть
1 - Ожидание ставок Анте
2 - Ставки Анте сделаны
3 - Ставки втемную сделаны
4 - Карты розданы
5 - Ставки за первый ход сделаны, определены играющие и заходящий
6 - Лишняя карта сброшена
7 - Первый ход сделан
8 - Второй ход сделан
9 - Третий ход сделан, определен победитель или АЗИ
10 - Ожидание врезки в АЗИ
11- Все игроки пасы, зарыли, добавление анте
12- Ожидание начала следующей игры

# Статус игрока (table.status)
    # 0 - ожидание
    # 1 - готов к игре
    # 2 - сделана стартовая ставка Ante
    # 3 - окончены торги и сброшена карта
    # 4 - сделан 1-й ход
    # 5 - сделан 2-й ход
    # 6 - сделан 3-й ход
    # 7 - в Ази
    # 8 - вырезан из Ази
    # 9 - Вкупился в Ази
    # 10- Отказался от Ази
    # 11- Упал 
    # 12- Нет монет для игры    

"""