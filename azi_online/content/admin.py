from django.contrib import admin

# Register your models here.
from .models import HomepageArticles, AboutpageArticle, RulespageArticles, TermspageArticle, TokenpageArticle, SupportpageArticle, PrivacypolicypageArticle

class HomepageArticlesAdmin(admin.ModelAdmin):
    list_display = ['id', 'language', 'title', 'publicdate']

class AboutpageArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'language', 'title']

class RulespageArticlesAdmin(admin.ModelAdmin):
    list_display = ['id', 'language', 'step', 'title']

class TermspageArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'language', 'step', 'title']

class TokenpageArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'language', 'step', 'title']

class SupportpageArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'language', 'step', 'title']

class PrivacypolicypageArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'language', 'step', 'title']



admin.site.register(HomepageArticles, HomepageArticlesAdmin)
admin.site.register(AboutpageArticle, AboutpageArticleAdmin)
admin.site.register(RulespageArticles, RulespageArticlesAdmin)
admin.site.register(TokenpageArticle, TokenpageArticleAdmin)
admin.site.register(TermspageArticle, TermspageArticleAdmin)
admin.site.register(SupportpageArticle, SupportpageArticleAdmin)
admin.site.register(PrivacypolicypageArticle, PrivacypolicypageArticleAdmin)
