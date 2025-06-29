from rest_framework import serializers
from .models import Players
from games.models import Game
import json

class PlayersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = '__all__'


def get_player_games_history(player_id):
    all_games = Game.objects.all()
    player_games = []    
    print('GET PLAYER GAMES HISTORY')
    for game in all_games:
        game_players = []
        player_game = {
            "game_id": 0,
            "date": None,
            "players": 0,
            "ante": 0,
            "pot": 0,
            "profit": 0,
            "player_bet": 0,
            "cointype": None
        }
        try:
            game_players = game.log[0]["betting"]["players"]
            if player_id in game_players:                
                player_game["game_id"] = game.id
                player_game["date"] = game.end_game.isoformat()
                player_game["players"] = len([p for p in game_players if p != 0])
                player_game["ante"] = game.min_bet
                player_game["pot"] = game.pot
                player_game["cointype"] = game.cointype
                index_player = game_players.index(player_id)
                bet_player = 0
                game_log = game.log
                for iteration in game_log:                   
                    try:
                        if iteration["betting"]["ante"][index_player] > 0:
                            bet_player += iteration["betting"]["ante"][index_player]
                    except:
                        pass
                    try:
                        if iteration["betting"]["blind"][index_player] > 0:
                            bet_player += iteration["betting"]["blind"][index_player]
                    except:
                        pass
                    try:
                        for trade_iteration in iteration["betting"]["trade"]:
                            if trade_iteration[index_player] > 0:
                                bet_player += trade_iteration[index_player]
                    except:
                        pass
                    try:
                        if iteration["gaming"]["azi_price"][index_player] > 0:
                            bet_player += iteration["gaming"]["azi_price"][index_player]
                    except:
                        pass
                player_game["player_bet"] = bet_player                
                last_gaming = game_log[-1]
                if last_gaming["gaming"]["winner"] == index_player:
                    player_game["profit"] = game.pot - bet_player
                else:
                    player_game["profit"] = 0 - bet_player
                player_games.append(player_game)
        except:
            pass    
    return player_games
