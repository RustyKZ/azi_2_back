from django.contrib import admin

from .models import Header, Languages, Footer, SingupForm, LoginForm, ModalError, UserProfile, UserReview, Homepage, TablesHall, PlayTable, CreateTable, AccessDenied, PageNotFound, ServerError, SandboxTable, UserHistory, Toplist, RecoveryForm

class HeaderAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class LanguagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'english_name', 'name', 'label', 'status']

class FooterAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class SignupFormAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class LoginFormAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class ModalErrorAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class UserReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class HomepageAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class TablesHallAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class PlayTableAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class CreateTableAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class AccessDeniedAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class PageNotFoundAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class ServerErrorAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class SandboxTableAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class ToplistAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']

class RecoveryFormAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']


admin.site.register(Header, HeaderAdmin)
admin.site.register(Languages, LanguagesAdmin)
admin.site.register(Footer, FooterAdmin)
admin.site.register(SingupForm, SignupFormAdmin)
admin.site.register(LoginForm, LoginFormAdmin)
admin.site.register(ModalError, ModalErrorAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserReview, UserReviewAdmin)
admin.site.register(Homepage, HomepageAdmin)
admin.site.register(TablesHall, TablesHallAdmin)
admin.site.register(PlayTable, PlayTableAdmin)
admin.site.register(CreateTable, CreateTableAdmin)
admin.site.register(AccessDenied, AccessDeniedAdmin)
admin.site.register(PageNotFound, PageNotFoundAdmin)
admin.site.register(ServerError, ServerErrorAdmin)
admin.site.register(SandboxTable, SandboxTableAdmin)
admin.site.register(UserHistory, UserHistoryAdmin)
admin.site.register(Toplist, ToplistAdmin)
admin.site.register(RecoveryForm, RecoveryFormAdmin)
