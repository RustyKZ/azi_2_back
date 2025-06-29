from games.models import SandboxGame, BotPlayers
import random

def generate_blindbet(greed):
    # Вычисляем вероятности для каждой ставки на основе значения greed
    probabilities = [(101 - greed) // 20] * 4 + [20]
    return random.choices(range(1, 6), weights=probabilities)[0]

def generate_bet(greed):
    # Вычисляем вероятности для каждой ставки на основе значения greed
    probabilities = [(101 - greed) // 10] * 9 + [10]
    return random.choices(range(1, 11), weights=probabilities)[0]

def bot_blind_bet(user_id):
    game = SandboxGame.objects.get(user_id=user_id)
    if game.blind_complete or game.stage != 2:
        return {"status": False}
    else:
        player_index = game.speaker
        player = BotPlayers.objects.get(id=game.players[game.speaker])
        bet_chance = random.randint(1, 100)
        betting = bet_chance <= player.blinding
        bet = generate_blindbet(player.greed)
        bet_value = bet * game.min_bet
        if betting:
            player.democoin -= bet_value
            game.pot += bet_value
            game.stage = 3
            game.current_hodor = player_index        
            game.players_bet[player_index] += bet_value*2        
            game.usersays = [0, 0, 0, 0, 0, 0]
            game.usersays_value = [0, 0, 0, 0, 0, 0]
            if bet_value == game.min_bet * 5:
                game.top_bet = True
                game.usersays[player_index] = 5
            else:
                game.usersays[player_index] = 4
            game.usersays_value[player_index] = bet_value*2
            game.blind_complete = True
            player.save()            
            game.save()
            return {"status": True, "bet": True}
        else:
            game.stage = 3
            game.usersays = [0, 0, 0, 0, 0, 0]
            game.usersays_value = [0, 0, 0, 0, 0, 0]
            game.blind_complete = True
            game.usersays[player_index] = 14
            game.save()
            return {"status": True, "bet": False}

# Получение номиналов козырных карт из карт бота
def find_trump_cards(cards, trump_card):
    if 1 <= trump_card <= 9:
        trump_suit = 1
    elif 10 <= trump_card <= 18:
        trump_suit = 2
    elif 19 <= trump_card <= 27:
        trump_suit = 3
    elif 28 <= trump_card <= 36:
        trump_suit = 4
    else:
        return []  # Неверная козырная карта, возвращаем пустой массив    
    # Определяем нижнюю и верхнюю границы для козырных карт в зависимости от масти
    lower_bound = (trump_suit - 1) * 9 + 1
    upper_bound = trump_suit * 9    
    # Формируем массив козырных карт
    trump_cards = [card % 9 if card % 9 != 0 else 9 for card in cards if lower_bound <= card <= upper_bound]    
    return trump_cards

# Проверка наличия атказа
def check_atkaz(bot_trumps, deck_trumps):
    # Сортируем массивы по убыванию
    bot_trumps.sort(reverse=True)
    deck_trumps.sort(reverse=True) 
    # Проверяем, есть ли среди элементов deck_trumps 2 и более самых старших элементов
    count = 0
    for trump in deck_trumps[:2]:
        if trump in bot_trumps:
            count += 1
            if count >= 2:
                return True
    # Проверяем, содержит ли массив bot_trumps 3 элемента из 4-х самых старших элементов deck_trumps
    count = 0
    for trump in deck_trumps[:4]:
        if trump in bot_trumps:
            count += 1
            if count >= 3:
                return True
    return False

# Проверка наличия почти атказа
def check_semi_atkaz(bot_trumps, deck_trumps):
    # Сортируем массивы по убыванию
    bot_trumps.sort(reverse=True)
    deck_trumps.sort(reverse=True)     
    if deck_trumps[0] in bot_trumps:
        count = 1
        for trump in deck_trumps[1:3]:
            if trump in bot_trumps:
                count += 1
                if count >= 2:
                    return True    
    if deck_trumps[1] in bot_trumps and deck_trumps[2] in bot_trumps:
        count = 1
        for trump in deck_trumps[3:5]:
            if trump in bot_trumps:
                count += 1
                if count >= 2:
                    return True
    return False

def check_combination_90(bot_trumps, deck_trumps):
    # Сортируем массивы по убыванию
    bot_trumps.sort(reverse=True)
    deck_trumps.sort(reverse=True)
    # Проверяем, есть ли среди козырей бота старший козырь колоды
    if deck_trumps[0] in bot_trumps:
        return True
    # Проверяем, есть ли среди козырей бота 2 карты рангом на ступень ниже старшего козыря колоды
    if deck_trumps[1] in bot_trumps and deck_trumps[2] in bot_trumps:
        return True
    # Проверяем, есть ли среди козырей бота 3 карты рангом на 2 ступени ниже старшего козыря колоды
    if deck_trumps[3] in bot_trumps and deck_trumps[4] in bot_trumps and deck_trumps[5] in bot_trumps:
        return True
    return False

def get_cards_power(cards, trump_card, drop_suit):
    trump_value = trump_card % 9
    if trump_value == 0:
        trump_value = 9
    deck_trumps = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    if trump_value in deck_trumps:
        deck_trumps.remove(trump_value)
    bot_trumps = find_trump_cards(cards, trump_card)
    number_of_trumps = len(bot_trumps)
    cards_power = 0 
    if drop_suit !=0:
        if check_atkaz(bot_trumps, deck_trumps):
            cards_power = 100
        elif check_semi_atkaz(bot_trumps, deck_trumps):
            cards_power = 95
        else:
            if number_of_trumps == 3:
                cards_power += 60
                if check_combination_90(bot_trumps, deck_trumps):
                    cards_power = 90
            elif number_of_trumps == 2:
                cards_power += 40
                if check_combination_90(bot_trumps, deck_trumps):
                    cards_power = 70
                if cards[1] % 9 == 0: #Проверка наличния полевого туза
                    cards_power += 15
            elif number_of_trumps == 1:
                cards_power += 20
                if check_combination_90(bot_trumps, deck_trumps):
                    cards_power = 50
                if cards[1] % 9 == 0 or cards[2] % 9 == 0: #Проверка наличния полевого туза
                    cards_power += 15
            elif number_of_trumps == 0:
                if cards[3] % 9 == 0 and cards[2] % 9 == 0: #Проверка наличния полевого туза
                    cards_power += 15
                elif cards[3] % 9 == 0:
                    cards_power += 10
    else:
        if check_atkaz(bot_trumps, deck_trumps):
            cards_power = 100
        elif check_semi_atkaz(bot_trumps, deck_trumps):
            cards_power = 97
        else:
            if number_of_trumps == 3:
                cards_power += 70
                if check_combination_90(bot_trumps, deck_trumps):
                    cards_power = 95
            elif number_of_trumps == 2:
                cards_power += 50
                if check_combination_90(bot_trumps, deck_trumps):
                    cards_power = 75
                if cards[1] % 9 == 0: #Проверка наличния полевого туза
                    cards_power += 15
            elif number_of_trumps == 1:
                cards_power += 25
                if check_combination_90(bot_trumps, deck_trumps):
                    cards_power = 55
                if cards[1] % 9 == 0 or cards[2] % 9 == 0: #Проверка наличния полевого туза
                    cards_power += 15
            elif number_of_trumps == 0:
                if cards[3] % 9 == 0 and cards[2] % 9 == 0: #Проверка наличния полевого туза
                    cards_power += 20
                elif cards[3] % 9 == 0:
                    cards_power += 15
    return cards_power

def get_bet_criteria(bot):
    index_criteria = random.randint(1, 3)
    if index_criteria == 1:
        return bot.greed
    elif index_criteria == 2:
        return bot.risking
    elif index_criteria == 3:
        return bot.agression

def get_call_criteria(bot):
    my_list = [1, 2, 4, 6]
    index_criteria = random.choice(my_list)
    if index_criteria == 1:
        return bot.greed
    elif index_criteria == 2:
        return bot.risking
    elif index_criteria == 4:
        return bot.fearless
    elif index_criteria == 6:
        return 101 - bot.thrift
    
def get_raise_criteria(bot):
    my_list = [1, 3, 5]
    index_criteria = random.choice(my_list)
    if index_criteria == 1:
        return bot.greed
    elif index_criteria == 3:
        return bot.agression
    elif index_criteria == 5:
        return bot.bluffing


def bot_solution_trade(user_id):
    game = SandboxGame.objects.get(user_id=user_id)
    index = game.speaker
    bot = BotPlayers.objects.get(id=game.players[index])
    cards = game.card_players[index*4:(index+1)*4]
    trump_card = game.card_players[24]
    cards_power = get_cards_power(cards, trump_card, game.drop_suit)
    bet_criteria = get_bet_criteria(bot)
    call_criteria = get_call_criteria(bot)
    raise_criteria = get_raise_criteria(bot)
    if max(game.players_bet) == 0:
        if cards_power + bet_criteria >= 150:
            if random.choice([True, False]):
                bot_bet = 10
            else:
                bot_bet = 9
        elif cards_power + bet_criteria >= 100:
            bot_bet = generate_bet(bet_criteria)
        else:
            bot_bet = 0
        if bot_bet == 0:
            return {"solution": "check"}
        else:
            return {"solution": "bet", "value": bot_bet}
    else:
        if cards_power + call_criteria < random.randint(80, 100):
            return {"solution": "fold"}
        else:
            if random.choice([True, False]):
                return {"solution": "call"}
            elif game.top_bet:
                return {"solution": "call"}
            else:
                if cards_power + raise_criteria >= 150:
                    if random.choice([True, False]):
                        bot_raise = 10
                    else:
                        bot_raise = 9
                elif cards_power + raise_criteria >= 90:
                    bot_raise = generate_bet(raise_criteria)
                else:
                    if random.choice([True, False]):
                        bot_raise = 2
                    else:
                        bot_raise = 1
                return {"solution": "raise", "value": bot_raise}


def get_cards_combination(cards, trump_card):
    trump_value = trump_card % 9
    if trump_value == 0:
        trump_value = 9
    deck_trumps = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    if trump_value in deck_trumps:
        deck_trumps.remove(trump_value)
    bot_trumps = find_trump_cards(cards, trump_card)
    number_of_trumps = len(bot_trumps)
    if check_atkaz(bot_trumps, deck_trumps):
        return 0 #Atkaz
    elif check_semi_atkaz(bot_trumps, deck_trumps) and number_of_trumps == 3:
        return 1 #Semi-Atkaz 3 trumps
    elif check_semi_atkaz(bot_trumps, deck_trumps) and number_of_trumps == 2:
        return 2 #Semi-Atkaz 2 trumps
    elif number_of_trumps == 3 and cards[3] % 9 == 0:
        return 3 #Triple with Ace
    elif number_of_trumps == 3:
        return 4 #Triple
    elif number_of_trumps == 2 and cards[1] % 9 == 0 and cards[3] % 9 == 0:
        return 5 #2 trumps with Ace + Ace
    elif number_of_trumps == 2 and cards[3] % 9 == 0:
        return 6 #2 trumps with Ace
    elif number_of_trumps == 2 and cards[1] % 9 == 0:
        return 7 #2 trumps + Ace
    elif number_of_trumps == 2:
        return 8 #2 trumps
    elif number_of_trumps == 1 and (cards[1] % 9 == 0 or cards[2] % 9 == 0):        
        return 9 #1 trumps + Ace
    elif number_of_trumps == 1:
        return 10 #1 trumps
    else:
        return 11 #Nothing

def sandbox_bot_turn_checking(card_players, card_place, current_hodor, card_id, player_index):
    card_index = card_players.index(card_id)    
    if (card_index >= player_index * 4) and (card_index < (player_index * 4) + 4) and (card_id != 0):        
        if all(element == 0 for element in card_place) and (current_hodor == player_index):
            return True
        elif card_place[current_hodor] != 0:
            card_hodor = card_place[current_hodor]
            range_hodor = range(((card_hodor - 1) // 9) * 9 + 1, ((card_hodor - 1) // 9) * 9 + 10)            
            range_trump = range( ((card_players[24] - 1) // 9) * 9 + 1, ((card_players[24] - 1) // 9) * 9 + 10)
            if card_id in range_hodor:
                return True
            elif card_id in range_trump:
                no_hodor_suit = True
                for ci in range(0, 4):
                    cc = card_players[player_index * 4 + ci]
                    if cc in range_hodor:
                        no_hodor_suit = False
                if no_hodor_suit:                    
                    return True
                else:                    
                    return False
            else:
                no_hodor_suit = True
                for ci in range(0, 4):
                    cc = card_players[player_index * 4 + ci]
                    if cc in range_hodor:
                        no_hodor_suit = False
                if not no_hodor_suit:
                    return False
                no_trump = True
                for ci in range(0, 4):
                    cc = card_players[player_index * 4 + ci]
                    if cc in range_trump:
                        no_trump = False
                if no_hodor_suit and no_trump:                    
                    return True
                else:                    
                    return False
    return False

def sandbox_beat_checking(card_players, card_place, current_hodor, card_id):
    if card_place[current_hodor] != 0:
        card_hodor = card_place[current_hodor]
        range_hodor = range(((card_hodor - 1) // 9) * 9 + 1, ((card_hodor - 1) // 9) * 9 + 10)            
        range_trump = range( ((card_players[24] - 1) // 9) * 9 + 1, ((card_players[24] - 1) // 9) * 9 + 10)
        card_place_value = [0,0,0,0,0,0]
        if card_hodor not in range_trump:
            for i in range(0, 6):
                if card_place[i] != 0:                
                    if card_place[i] in range_hodor:
                        card_place_value[i] = card_place[i] + 100
                    elif card_place[i] in range_trump:
                        card_place_value[i] = card_place[i] + 200
                    else:
                        card_place_value[i] = card_place[i]
        else:
            for i in range(0, 6):
                if card_place[i] != 0:                
                    if card_place[i] in range_trump:
                        card_place_value[i] = card_place[i] + 200                    
                    else:
                        card_place_value[i] = card_place[i]
        if card_id in range_trump:
            card_value = card_id + 200
        elif card_id in range_hodor:
            card_value = card_id + 100
        else:
            card_value = card_id
        if card_value > max(card_place_value):
            return True
        else:
            return False
    else:
        return True
        
def sandbox_bot_turn1(user_id):
    game = SandboxGame.objects.get(user_id=user_id)
    bot = BotPlayers.objects.get(id=game.players[game.speaker])
    player_index = game.speaker
    cards = game.card_players[player_index*4: player_index*4 + 4]
    players = game.status.count(3) + game.status.count(4)
    beat_hands = game.status.count(3) - 1
    if game.current_hodor == player_index:
        bot_combination = get_cards_combination(cards, game.card_players[24])
        if bot_combination == 0:    #Atkaz
            hodor_card = 1
        elif bot_combination == 1:  #Semi-Atkaz 3 trumps
            if players == 2:
                hodor_card = 2
            else:
                if random.choice([True, False]):
                    hodor_card = 2
                else:
                    hodor_card = 1
        elif bot_combination == 2:  #Semi-Atkaz 2 trumps
            hodor_card = 1
        elif bot_combination == 3:  #Triple with Ace
            if players == 2:
                hodor_card = 1
            else:
                if random.randint(1, 100) <= bot.agression:
                    hodor_card = 3
                else:
                    hodor_card = 1
        elif bot_combination == 4:  #Triple
            if players == 2:
                hodor_card = 2
            else:
                if random.choice([True, False]):
                    hodor_card = 2
                else:
                    hodor_card = 1
        elif bot_combination == 5:  #2 trumps with Ace + Ace
            if players == 2:
                hodor_card = 1
            else:
                if random.randint(1, 100) <= bot.agression:
                    hodor_card = 3
                else:
                    hodor_card = 1
        elif bot_combination == 6:  #2 trumps with Ace
            if players == 2:
                hodor_card = 1
            else:
                if random.randint(1, 100) <= bot.agression and random.randint(1, 100) <= bot.risking:
                    hodor_card = 3
                else:
                    hodor_card = 1
        elif bot_combination == 7:  #2 trumps + Ace
            if players == 2:
                hodor_card = 1
            else:
                if random.randint(1, 100) <= bot.agression:
                    hodor_card = 2
                else:
                    hodor_card = 1
        elif bot_combination == 8:  #2 trumps
            if players == 2:
                hodor_card = 1
            else:
                if random.randint(1, 100) <= bot.agression and random.randint(1, 100) <= bot.risking:
                    hodor_card = 2
                else:
                    hodor_card = 1
        elif bot_combination == 9:  #1 trumps + Ace
            hodor_card = 2
        elif bot_combination == 10:  #1 trumps
            if players == 2:
                hodor_card = 2
            else:
                if random.choice([True, False]):
                    hodor_card = 2
                else:
                    hodor_card = 1
        elif bot_combination == 11:  #None
            hodor_card = 3
        if cards[hodor_card] == 0:
            for i in range(0, 4):
                if cards[i] != 0:
                    hodor_card = i
                    break
        print(f'BOT HODOR: Cards: {cards}; Combination: {bot_combination}; Hodor card: {hodor_card}')
    else:
        card_index_possible = []
        for ind in range(0, 4):
            if cards[ind] != 0:
                if sandbox_bot_turn_checking(game.card_players, game.card_place, game.current_hodor, cards[ind], player_index):
                    card_index_possible.append(ind)
        card_index_beat_possible = []
        for idx in card_index_possible:
            if sandbox_beat_checking(game.card_players, game.card_place, game.current_hodor, cards[idx]):
                card_index_beat_possible.append(idx)
        beat_variant = len(card_index_beat_possible)
        if beat_variant != 0:
            if players > 2 and beat_hands >=1:
                if beat_variant == 3:
                    if random.randint(1, 100) <= bot.agression:
                        hodor_card = 3
                    elif random.choice([True, False]):
                        hodor_card = 2
                    else:
                        hodor_card = 1
                elif beat_variant == 2:
                    if random.randint(1, 100) <= bot.agression:
                        hodor_card = card_index_beat_possible[1]
                    else:
                        hodor_card = card_index_beat_possible[0]
                else:
                    hodor_card = card_index_beat_possible[0]
            else:
                hodor_card = card_index_beat_possible[0]
        else:
            hodor_card = card_index_possible[0]
        if cards[hodor_card] == 0:
            for i in range(0, 4):
                if cards[i] != 0 and sandbox_bot_turn_checking(game.card_players, game.card_place, game.current_hodor, cards[i], player_index):                
                    hodor_card = i
                    break
    card_hodor_id = cards[hodor_card]
    game.card_players[player_index*4 + hodor_card] = 0
    game.card_place[player_index] = card_hodor_id
    game.status[player_index] = 4
    game.save()

def sandbox_bot_turn2(user_id):
    game = SandboxGame.objects.get(user_id=user_id)
    bot = BotPlayers.objects.get(id=game.players[game.speaker])
    player_index = game.speaker
    cards = game.card_players[player_index*4: player_index*4 + 4]
    players = game.status.count(4) + game.status.count(5)
    beat_hands = game.status.count(4) - 1
    if game.current_hodor == player_index:
        card_index_possible = []
        for ind in range(0, 4):
            if cards[ind] != 0:
                card_index_possible.append(ind)
        hodor_card = card_index_possible[0]
    else:
        card_index_possible = []
        for ind in range(0, 4):
            if cards[ind] != 0:
                if sandbox_bot_turn_checking(game.card_players, game.card_place, game.current_hodor, cards[ind], player_index):
                    card_index_possible.append(ind)
        card_index_beat_possible = []
        for idx in card_index_possible:
            if sandbox_beat_checking(game.card_players, game.card_place, game.current_hodor, cards[idx]):
                card_index_beat_possible.append(idx)
        beat_variant = len(card_index_beat_possible)
        if beat_variant != 0:
            if players > 2 and beat_hands >=1:
                if beat_variant == 2:
                    if random.randint(1, 100) <= bot.agression or random.randint(1, 100) <= bot.risking or random.randint(1, 100) <= bot.greed:
                        hodor_card = card_index_beat_possible[1]
                    else:
                        hodor_card = card_index_beat_possible[0]
                else:
                    hodor_card = card_index_beat_possible[0]
            else:
                hodor_card = card_index_beat_possible[0]
        else:
            hodor_card = card_index_possible[0]
        if cards[hodor_card] == 0:
            for i in range(0, 4):
                if cards[i] != 0 and sandbox_bot_turn_checking(game.card_players, game.card_place, game.current_hodor, cards[i], player_index):                
                    hodor_card = i
                    break
    card_hodor_id = cards[hodor_card]
    game.card_players[player_index*4 + hodor_card] = 0
    game.card_place[player_index] = card_hodor_id
    game.status[player_index] = 5
    game.save()

def sandbox_bot_turn3(user_id):
    game = SandboxGame.objects.get(user_id=user_id)    
    player_index = game.speaker
    cards = game.card_players[player_index*4: player_index*4 + 4]
    card_index_possible = []
    for ind in range(0, 4):
        if cards[ind] != 0:
            card_index_possible.append(ind)
    hodor_card = card_index_possible[0]
    card_hodor_id = cards[hodor_card]
    game.card_players[player_index*4 + hodor_card] = 0
    game.card_place[player_index] = card_hodor_id
    game.status[player_index] = 6
    game.save()

def sandbox_bots_azi_solution(user_id):
    game = SandboxGame.objects.get(user_id=user_id)
    for i in range(1, game.max_players):
        if sandbox_get_bot_azi_solution(user_id, i):
            sandbox_bot_azi_burst(user_id, i)        
        else:
            sandbox_bot_azi_refuse(user_id, i)
    all_bots_are_ready = True
    for k in range(1, game.max_players):
        if game.players[k] != -1 and (game.status[i] == 8 or game.status[i] == 11):
            all_bots_are_ready = False
    return all_bots_are_ready

def sandbox_get_bot_azi_solution(user_id, index):
    game = SandboxGame.objects.get(user_id=user_id)
    bot = BotPlayers.objects.get(id=game.players[index])
    if bot.democoin <= game.azi_price:
        return False
    else:
        pot_margin = round(game.pot / game.min_bet)
        if bot.thrift >= 95:
            return False
        elif bot.greed + 50 < bot.thrift:
            return False
        elif (pot_margin > bot.thrift) or (bot.greed > bot.thrift):
            if random.randint(1, 80) <= bot.greed:
                return True
        else:
            if random.choice([True, False]):
                return True
            else:
                return False

def sandbox_bot_azi_burst(user_id, index):
    try:
        game = SandboxGame.objects.get(user_id=user_id)
        player = BotPlayers.objects.get(id=game.players[index])
        player_index = index
        value = game.azi_price
        if not (game.status[player_index] == 8 or game.status[player_index] == 11):
            print(f'!!! error !!! --------- SANDBOX BOT AZI BURST - line 615')
            return {"status": False, "error": 0}
        if player.democoin < value:
            print(f'!!! error !!! --------- SANDBOX BOT AZI BURST - line 618')
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
    except Exception as e:
        print(f'!!! error !!! --------- SANDBOX BOT AZI BURST - Exceptions: {e}')
        return {"status": False, "error": 0}
    

def sandbox_bot_azi_refuse(user_id, index):
    try:
        game = SandboxGame.objects.get(user_id=user_id)        
        player_index = index
        if not (game.status[player_index] == 8 or game.status[player_index] == 11):
            print(f'!!! error !!! --------- SANDBOX BOT AZI REFUSE - line 639')
            return {"status": False, "error": 0}
        game.usersays[player_index] = 12
        game.usersays_value[player_index] = 0
        game.status[player_index] = 10
        game.save()        
        return {"status": True}
    except Exception as e:
        print(f'!!! error !!! --------- SANDBOX BOT AZI REFUSE - Exceptions: {e}')
        return {"status": False, "error": 0}