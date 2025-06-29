from django.contrib import admin
from .models import Tables, Game, SandboxGame, BotPlayers

# Register your models here.
class TablesAdmin(admin.ModelAdmin):    
    list_display = ['id', 'players', 'number', 'currentgame']

class GameAdmin(admin.ModelAdmin):
    list_display = ['id', 'players', 'table_id', 'cointype']

class SandboxGameAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'players']

class BotPlayersGameAdmin(admin.ModelAdmin):
    list_display = ['id', 'nickname', 'rating', 'democoin']

admin.site.register(Tables, TablesAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(SandboxGame, SandboxGameAdmin)
admin.site.register(BotPlayers, BotPlayersGameAdmin)

