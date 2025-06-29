from django.contrib import admin

# Register your models here.
from .models import Players, PlayersData, MailServerSettings, TokenSettings, DepositWithdrawSettings, TransactionsLog, TransactionsError, WithdrawsGold, PaypalTransactionsError, PaypalTransactionsLog, PlayersStats, Airdrops, BlacklistIP, GreylistIP

class PlayersAdmin(admin.ModelAdmin):
    list_display = ['id', 'nickname', 'email']

class PlayersDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id']

class MailServerSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'host', 'username']

class TokenSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'cointype', 'contract']

class DepositWithdrawSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'paypal_account']

class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'transaction_hash']

class TransactionErrorAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'user_id', 'transaction_hash']

class WithdrawsGoldAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_request', 'user_id', 'completed']

class PaypalTransactionLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'transaction_id', 'amount']

class PaypalTransactionErrorAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'user_id', 'transaction_id']

class PlayersStatsAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'rate']

class AirDropsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'regular', 'value', 'date', 'completed']

class BlacklistIPAdmin(admin.ModelAdmin):
    list_display = ['id', 'ip_address', 'date']

class GreylistIPAdmin(admin.ModelAdmin):
    list_display = ['id', 'ip_address', 'reset_try']


admin.site.register(Players, PlayersAdmin)
admin.site.register(PlayersData, PlayersDataAdmin)
admin.site.register(MailServerSettings, MailServerSettingsAdmin)
admin.site.register(TokenSettings, TokenSettingsAdmin)
admin.site.register(DepositWithdrawSettings, DepositWithdrawSettingsAdmin)
admin.site.register(TransactionsLog, TransactionLogAdmin)
admin.site.register(TransactionsError, TransactionErrorAdmin)
admin.site.register(WithdrawsGold, WithdrawsGoldAdmin)
admin.site.register(PaypalTransactionsLog, PaypalTransactionLogAdmin)
admin.site.register(PaypalTransactionsError, PaypalTransactionErrorAdmin)
admin.site.register(PlayersStats, PlayersStatsAdmin)
admin.site.register(Airdrops, AirDropsAdmin)
admin.site.register(BlacklistIP, BlacklistIPAdmin)
admin.site.register(GreylistIP, GreylistIPAdmin)

