from django.db import models


class Header(models.Model):
    label = models.CharField('label', max_length=5)
    home = models.CharField('home', max_length=50)
    play = models.CharField('play', max_length=50)
    rules = models.CharField('rules', max_length=50)
    top = models.CharField('top', max_length=50)
    about = models.CharField('about', max_length=50)
    terms = models.CharField('terms', max_length=50)
    table = models.CharField('table', max_length=50)
    signup = models.CharField('singup', max_length=50)
    login = models.CharField('login', max_length=50)
    logout = models.CharField('loguot', max_length=50)
    wallet = models.CharField('wallet', max_length=50)
    disconnect = models.CharField('disconnect', max_length=50)
    hint_wallet = models.CharField('hint_wallet', max_length=250)
    hall = models.CharField('hall', max_length=50, blank=True, null=True)
    sandbox = models.CharField('sandbox', max_length=50, blank=True, null=True)

    def __str__(self):
        return self.label


class Languages(models.Model):
    label = models.CharField('label', max_length=5)
    english_name = models.CharField('english_name', max_length=50)
    name = models.CharField('name (native name)', max_length=50)
    status = models.BooleanField('status (is available?)')

    def __str__(self):
        return self.english_name


class Footer(models.Model):
    label = models.CharField('label', max_length=5)
    text_copyright = models.CharField('text_copyright', max_length=250, blank=True, null=True)
    path_facebook = models.CharField('path_facebook', max_length=250, blank=True, null=True)
    path_reddit = models.CharField('path_reddit', max_length=250, blank=True, null=True)
    path_telegram = models.CharField('path_telegram', max_length=250, blank=True, null=True)
    path_x = models.CharField('path_x', max_length=250, blank=True, null=True)
    path_discord = models.CharField('path_discord', max_length=250, blank=True, null=True)
    path_instagram = models.CharField('path_instagram', max_length=250, blank=True, null=True)
    path_appstore = models.CharField('path_appstore', max_length=250, blank=True, null=True)
    path_googleplay = models.CharField('path_googleplay', max_length=250, blank=True, null=True)
    path_support = models.CharField('path_support', max_length=250, blank=True, null=True)
    hint_facebook = models.CharField('hint_facebook', max_length=250, blank=True, null=True)
    hint_reddit = models.CharField('hint_reddit', max_length=250, blank=True, null=True)
    hint_telegram = models.CharField('hint_telegram', max_length=250, blank=True, null=True)
    hint_x = models.CharField('hint_x', max_length=250, blank=True, null=True)
    hint_discord = models.CharField('hint_discord', max_length=250, blank=True, null=True)
    hint_instagram = models.CharField('hint_instagram', max_length=250, blank=True, null=True)
    hint_appstore = models.CharField('hint_appstore', max_length=250, blank=True, null=True)
    hint_googleplay = models.CharField('hint_googleplay', max_length=250, blank=True, null=True)
    hint_support = models.CharField('hint_support', max_length=250, blank=True, null=True)


class SingupForm(models.Model):
    label = models.CharField('label', max_length=5)
    title = models.CharField('title', max_length=100)
    nickname = models.CharField('nickname', max_length=100)
    nickname_hint = models.CharField('nickname_hint', max_length=250)
    email = models.CharField('email', max_length=250)
    email_hint = models.CharField('email_hint', max_length=250)
    ref_code = models.CharField('ref_code', max_length=50)
    ref_code_hint = models.CharField('ref_code_hint', max_length=250)
    password = models.CharField('password', max_length=50)
    repassword = models.CharField('reasswood', max_length=50)
    submit = models.CharField('submit', max_length=50)
    signup_with = models.CharField('singup_with', max_length=250)
    google_hint = models.CharField('google_hint', max_length=250)
    metamask_hint = models.CharField('metamask_hint', max_length=250)
    alert_congrats = models.CharField(max_length=250)
    alert_successful = models.CharField(max_length=250)
    privacy_text = models.TextField(blank=True, null=True)
    privacy_link = models.CharField(max_length=250, blank=True, null=True)
    terms_link = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.label


class LoginForm(models.Model):
    label = models.CharField('label', max_length=5)
    title = models.CharField('title', max_length=100)
    email = models.CharField('email', max_length=250)
    password = models.CharField('password', max_length=50)
    submit = models.CharField('submit', max_length=50)
    login_with = models.CharField('login_with', max_length=250)
    google_hint = models.CharField('google_hint', max_length=250)
    metamask_hint = models.CharField('metamask_hint', max_length=250)
    forgot_password = models.CharField('forgot_password', max_length=100)
    forgot_password_hint = models.CharField('forgot_password_hint', max_length=250)

    def __str__(self):
        return self.label

class ModalError(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    error = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"ModalError - {self.label}"

class UserProfile(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения
    states = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"UserProfile - {self.label}"

class UserReview(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"UserProfile - {self.label}"

class Homepage(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"UserProfile - {self.label}"
    
class TablesHall(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"Language - {self.label}"
    
class PlayTable(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"Language - {self.label}"
    
class CreateTable(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"Language - {self.label}"
    

class AccessDenied(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"Language - {self.label}"
    
class PageNotFound(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"Language - {self.label}"
    
class ServerError(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"Language - {self.label}"

class SandboxTable(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"Language - {self.label}"
    
class UserHistory(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"Language - {self.label}"
    
class Toplist(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"Language - {self.label}"
    
class RecoveryForm(models.Model):
    label = models.CharField('label', max_length=5) #языковая метка
    form = models.TextField(blank=True, null=True) # Поле для хранения JSON данных, допускающее пустые значения

    def __str__(self):
        return f"Language - {self.label}"