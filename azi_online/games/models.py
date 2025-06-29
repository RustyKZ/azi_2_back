from django.db import models
from django.utils import timezone

def default_integer_array():
    return [0, 0, 0, 0, 0, 0]

def card_players_array():
    return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def check_players_array():
    return [False, False, False, False, False, False]

def nicknames_array():
    return ['', 'Didier', 'Ded Mazay', 'Eldorado', 'Skakun', 'Russo']

def empty_array():
    return []

# Create your models here.
class Tables(models.Model):
    number = models.IntegerField('Table ID (number)', unique=True)
    max_players = models.IntegerField('Table max players', default=6)
    drop_suit = models.IntegerField('Table dropped suit', default=0)
    cointype = models.IntegerField('Table cointype', default=0)
    min_bet = models.IntegerField('Table min bet', default=1)
    max_bet = models.IntegerField('Table max bet', default=10)
    table_password = models.CharField('Table password', max_length=255, blank=True, null=True)
    players = models.JSONField(default=default_integer_array)
    status = models.JSONField(default=default_integer_array)
    gamestage = models.IntegerField('Gamestage', default=0)
    blind_game = models.BooleanField('Blind game', default=True)
    dealing = models.IntegerField('Table dealer', default=0)
    currentgame = models.IntegerField('Table current game', default=0)
    players_now = models.IntegerField('Table players now', default=0)    
    time_stop = models.IntegerField('Table time_stop (0 if table active)', default=0)
    interval = models.IntegerField('Table interval, sec', default=30)
    lastdeal = models.IntegerField('Table lastdeal (0 if table inactive)', default=0)
    inactive_drop_interval = models.IntegerField(default=300)
    default_ready = models.JSONField(default=default_integer_array)
    default_ready_limit = models.IntegerField(default=3)

    def __unt__(self):
        return self.id

class Game(models.Model):
    start_game = models.DateTimeField(blank=True, null=True)
    table_id = models.IntegerField(default=0)
    cointype = models.IntegerField(default=0)
    players = models.JSONField(default=default_integer_array)
    min_bet = models.IntegerField(default=1)
    drop_suit = models.IntegerField(default=0)
    trump_suit = models.IntegerField(default=0)
    pot = models.IntegerField(default=0)
    betting = models.JSONField(blank=True, null=True)
    gaming = models.JSONField(blank=True, null=True)
    end_game = models.DateTimeField(default=None, blank=True, null=True)
    winner = models.IntegerField(default=-1)
    lastgame = models.IntegerField(default=0)
    actual_deck = models.JSONField(default = None, blank=True, null=True)
    card_players = models.JSONField(default=card_players_array)
    card_place1 = models.JSONField(default=default_integer_array)
    card_place2 = models.JSONField(default=default_integer_array)
    card_place3 = models.JSONField(default=default_integer_array)
    card_place = models.JSONField(default=default_integer_array)
    cards_now = models.JSONField(default=default_integer_array)
    speaker = models.IntegerField(default=-1)
    speaker_id = models.IntegerField(default=0)
    stage = models.IntegerField(default=0)    
    players_bet = models.JSONField(default=default_integer_array)    
    usersays = models.JSONField(default=default_integer_array)
    usersays_value = models.JSONField(default=default_integer_array)
    top_bet = models.BooleanField(default=False)
    check_status = models.JSONField(default=check_players_array)
    status = models.JSONField(default=default_integer_array)
    turn1win = models.IntegerField(default=-1)
    turn2win = models.IntegerField(default=-1)
    turn3win = models.IntegerField(default=-1)
    current_hodor = models.IntegerField(default=-1)
    azi_price = models.IntegerField(default=0)
    log = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'Game id: {self.id}'
    

class SandboxGame(models.Model):
    start_game = models.DateTimeField(blank=True, null=True)
    user_id = models.IntegerField(default=0)
    max_players = models.IntegerField(default=6)
    players = models.JSONField(default=default_integer_array)
    min_bet = models.IntegerField(default=1)
    drop_suit = models.IntegerField(default=0)
    trump_suit = models.IntegerField(default=0)
    pot = models.IntegerField(default=0)
    end_game = models.DateTimeField(default=None, blank=True, null=True)
    winner = models.IntegerField(default=-1)
    lastgame = models.IntegerField(default=0)
    actual_deck = models.JSONField(default = None, blank=True, null=True)
    card_players = models.JSONField(default=card_players_array)
    card_place1 = models.JSONField(default=default_integer_array)
    card_place2 = models.JSONField(default=default_integer_array)
    card_place3 = models.JSONField(default=default_integer_array)
    card_place = models.JSONField(default=default_integer_array)
    cards_now = models.JSONField(default=default_integer_array)
    speaker = models.IntegerField(default=-1)
    speaker_id = models.IntegerField(default=-1)
    stage = models.IntegerField(default=0)
    players_bet = models.JSONField(default=default_integer_array)    
    usersays = models.JSONField(default=default_integer_array)
    usersays_value = models.JSONField(default=default_integer_array)
    top_bet = models.BooleanField(default=False)
    check_status = models.JSONField(default=check_players_array)
    status = models.JSONField(default=default_integer_array)
    turn1win = models.IntegerField(default=-1)
    turn2win = models.IntegerField(default=-1)
    turn3win = models.IntegerField(default=-1)
    current_hodor = models.IntegerField(default=-1)
    azi_price = models.IntegerField(default=0)  
    blind_game = models.BooleanField('Blind game', default=True)
    dealing = models.IntegerField('Table dealer', default=0)
    bot_nicknames = models.JSONField(default=nicknames_array)
    blind_complete = models.BooleanField('Blind bet is complete', default=False)
    gamestage_complete = models.BooleanField('Gamestage is complete', default=True)


    def __str__(self):
        return f'Game id: {self.id}'
    

class BotPlayers(models.Model):
    nickname = models.CharField('Bot nickname', max_length=50)
    rating = models.IntegerField('Bot rating', default=0, blank=True, null=True)
    gamemodel = models.IntegerField('Game model', default=0, blank=True, null=True)
    democoin = models.IntegerField('Democoins', default=100000)
    blinding = models.IntegerField('Blinding', default=50)
    greed = models.IntegerField('Greed', default=50)            #1        
    risking = models.IntegerField('Risking', default=50)        #2
    agression = models.IntegerField('Agression', default=50)    #3
    fearless = models.IntegerField('Fearless', default=50)      #4  
    bluffing = models.IntegerField('Bluffing', default=50)      #5
    thrift = models.IntegerField('Thrift', default=50)          #6
    deposit_log = models.JSONField(default=empty_array)

    def __str__(self):
        return self.nickname
