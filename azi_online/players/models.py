from django.db import models

# Create your models here.
class Players(models.Model):
    nickname = models.CharField('Player nickname', max_length=50)
    email = models.EmailField('Player email', unique=True, blank=True, null=True)
    password = models.CharField('Player password hash', max_length=255, blank=True, null=True)
    reg_date = models.DateTimeField('Player registation date')
    ip_address = models.CharField('Player IP Address', max_length=255)
    phone = models.CharField('Player phone', max_length=50, blank=True, null=True)
    country = models.IntegerField('Player country', blank=True, null=True)
    silvercoin = models.IntegerField('Player silver balance')
    goldcoin = models.IntegerField('Player goldcoin balance')
    bonuscoin = models.IntegerField('Player bonuscoin balance')
    democoin = models.IntegerField('Player democoin balance')
    active_table = models.IntegerField('Player active table')
    reputation = models.IntegerField('Player reputation')
    rating = models.IntegerField('Player rating')
    wallet = models.CharField('Player wallet address', max_length=255, blank=True, null=True)
    django_name = models.CharField('Player Django username', max_length=255, blank=True, null=True)
    google_uid = models.CharField('Player google account ID', max_length=255, blank=True, null=True)
    online_mail = models.BooleanField('Player online by email')
    online_google = models.BooleanField('Player online by Google')
    online_metamask = models.BooleanField('Player online by Metamask')
    email_is_verified = models.BooleanField('Email address is verified')
    phone_is_verified = models.BooleanField('Phone is verified')
    referer_id = models.IntegerField('Referer user ID', blank=True, null=True)
    referal_code = models.CharField('Personnel referal code', unique=True, max_length=255, blank=True, null=True)
    last_activity = models.IntegerField('Player last activity')
    language = models.IntegerField('Player language', default=1)
    sid = models.CharField('Socket SID', max_length=255, blank=True, null=True)
    verification_code = models.CharField(max_length=10, blank=True, null=True)
    verification_time = models.IntegerField(default=0)
    verification_try = models.IntegerField(default=0)
    reset_code = models.CharField(max_length=10, blank=True, null=True)
    reset_time = models.IntegerField(default=0)
    reset_try = models.IntegerField(default=0)
    global_reset_try = models.IntegerField(default=0)
    

    def __str__(self):
        return self.nickname

class PlayersData(models.Model):
    user_id = models.IntegerField('Player ID number', unique=True)
    coin_activity = models.JSONField(blank=True, null=True)
    airdrop_silver = models.IntegerField(default=0)
    airdrop_gold = models.IntegerField(default=0)
    airdrop_bonus = models.IntegerField(default=0)
    ref_silver = models.IntegerField(default=0)
    ref_gold = models.IntegerField(default=0)
    ref_bonus = models.IntegerField(default=0)
    history_silver = models.JSONField(blank=True, null=True)
    history_gold = models.JSONField(blank=True, null=True)
    history_bonus = models.JSONField(blank=True, null=True)
    history_free = models.JSONField(blank=True, null=True)
    bonusgamehistory = models.JSONField(blank=True, null=True)
    comments = models.JSONField(blank=True, null=True)

    def __int__(self):
        return self.user_id

class MailServerSettings(models.Model):
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    admin_mail = models.CharField(max_length=255, blank=True, null=True)
    moderator_mail = models.CharField(max_length=255, blank=True, null=True)
    use_tls = models.BooleanField(default=False)
    use_ssl = models.BooleanField(default=False)
    mail_subject = models.CharField(max_length=255, blank=True, null=True)
    mail_text_before = models.TextField(blank=True, null=True)
    mail_text_after = models.TextField(blank=True, null=True)
    reset_subject = models.CharField(max_length=255, blank=True, null=True)
    reset_text_before = models.TextField(blank=True, null=True)
    reset_text_after = models.TextField(blank=True, null=True)
    user_mail_server = models.CharField(max_length=255)
    google_auth_client_id = models.CharField(max_length=255)
    app_client_url = models.CharField(max_length=255)
    def __str__(self):
        return self.username
    
class TokenSettings(models.Model):
    contract = models.CharField(max_length=100, default='0xE8544773D7217Ff4Bb6A19636779139460A87ecd')
    host_wallet = models.CharField(max_length=100, default='0x5B4c138eb869Cb2Ad29414912d21E40ecAB4BFbA')
    abi = models.JSONField(blank=True, null=True)
    gas = models.IntegerField(default=50000)
    cointype = models.IntegerField('1 = goldcoin; 2 = bonuscoin', unique=True, default=1)
    def __str__(self):
        return self.contract
    
class DepositWithdrawSettings(models.Model):
    withdraw_min_limit = models.IntegerField(default=100)
    deposit_min_limit_gold = models.IntegerField(default=1)
    deposit_min_limit_silver = models.IntegerField(default=100)
    paypal_account = models.CharField(max_length=100, default='azi-online@mail.ru')
    gold_transfer_rate = models.IntegerField(default=90)
    paypal_client_id = models.CharField(max_length=255, blank=True, null=True)
    paypal_client_secret = models.CharField(max_length=255, blank=True, null=True)
    paypal_merchant_id = models.CharField(max_length=100, default='')
    paypal_token_url = models.CharField(max_length=255, blank=True, null=True)
    paypal_order_url = models.CharField(max_length=255, blank=True, null=True)
    silver_bnb_rate = models.IntegerField(default=500000)
    silver_usd_rate = models.IntegerField(default=1000)
    def __str__(self):
        return self.paypal_account

class TransactionsLog(models.Model):
    transaction_hash = models.CharField(max_length=255, unique=True, null=True)
    sender = models.CharField(max_length=255, blank=True, null=True)
    recipient = models.CharField(max_length=255, blank=True, null=True)
    contract = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField()
    amount = models.FloatField(blank=True, null=True)
    
class TransactionsError(models.Model):
    date = models.DateTimeField()
    user_id = models.IntegerField(blank=True, null=True)
    sender = models.CharField(max_length=255, blank=True, null=True)
    transaction_hash = models.CharField(max_length=255, blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)
    ip_address = models.CharField(max_length=255, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    solved = models.BooleanField(default=False)
    solution = models.IntegerField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

class WithdrawsGold(models.Model):
    date_request = models.DateTimeField()
    user_id = models.IntegerField(blank=True, null=True)
    user_address = models.CharField(max_length=255, blank=True, null=True)
    amount_gold = models.IntegerField(blank=True, null=True)
    amount_token = models.FloatField(blank=True, null=True)
    ip_address = models.CharField(max_length=255, blank=True, null=True)
    date_response = models.DateTimeField(blank=True, null=True)
    transaction_hash = models.CharField(max_length=255, blank=True, null=True)
    completed = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)

class PaypalTransactionsLog(models.Model):
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    payer_mail = models.CharField(max_length=255, blank=True, null=True)
    payer_id = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField()
    amount = models.FloatField(blank=True, null=True)
    
class PaypalTransactionsError(models.Model):
    date = models.DateTimeField()
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    ip_address = models.CharField(max_length=255, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    solved = models.BooleanField(default=False)
    solution = models.IntegerField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

class PlayersStats(models.Model):
    user_id = models.IntegerField('Player ID number', unique=True)
    games_silver = models.IntegerField(default=0)
    games_gold = models.IntegerField(default=0)
    games_bonus = models.IntegerField(default=0)
    profit_silver = models.IntegerField(default=0)
    profit_gold = models.IntegerField(default=0)
    profit_bonus = models.IntegerField(default=0)
    relative_silver = models.FloatField(default=0)
    relative_gold = models.FloatField(default=0)
    relative_bonus = models.FloatField(default=0)
    wins_silver = models.FloatField(default=0)
    wins_gold = models.FloatField(default=0)
    wins_bonus = models.FloatField(default=0)
    rate = models.FloatField(default=1400)
    games_log = models.JSONField(blank=True, null=True)

class Airdrops(models.Model):
    name = models.CharField(max_length=50, unique=True)
    completed = models.BooleanField(default=False)
    regular = models.BooleanField(default=False)
    hour = models.IntegerField(default=0)
    day_of_week = models.IntegerField(default=0)
    day = models.IntegerField(default=0)
    date = models.DateTimeField(default=None, blank=True, null=True)
    cointype = models.IntegerField(default=0)
    value = models.IntegerField(default=0)
    to = models.JSONField(blank=True, null=True)

class BlacklistIP(models.Model):
    ip_address = models.CharField(max_length=255)
    date = models.DateTimeField(default=None, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

class GreylistIP(models.Model):
    ip_address = models.CharField(max_length=255)
    reset_try = models.IntegerField(default=0)
    log = models.JSONField(blank=True, null=True)