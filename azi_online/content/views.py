from django.shortcuts import render
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import HomepageArticles, AboutpageArticle, RulespageArticles, TermspageArticle, TokenpageArticle, SupportpageArticle, PrivacypolicypageArticle
from django.core.serializers import serialize

# Create your views here.
@api_view(['GET'])
def api_get_homepage_data(request, languageID):    
    try:       
        articles = HomepageArticles.objects.filter(language=languageID).order_by('-publicdate')        
        serialized_articles = serialize('json', articles)
        if articles.exists():
            data = {
                'result': True,
                'articles': serialized_articles
            }        
            return JsonResponse(data)
        else:
            return JsonResponse({'result': False, 'message': 'No articles found for the specified language ID'})        
    except HomepageArticles.DoesNotExist:
        return JsonResponse({'result': False, 'message': 'ERROR getting articles'})

@api_view(['GET'])
def api_get_aboutpage_data(request, languageID):
    try:
        article = AboutpageArticle.objects.get(language=languageID)
        print(f'API GET ABOUTPAGE DATA - Article: {article}')
        data_to_send = {
            'title': article.title,
            'subtitle': article.subtitle,
            'image': article.image.url,
            'text': article.text
        }        
        return JsonResponse({'result': True, 'message': 'Aboutpage data sent successfully', 'article': data_to_send})
    except:
        print(f'API GET ABOUTPAGE DATA - Article: No Article')
        return JsonResponse({'result': False, 'message': 'ERROR getting about article'})
    
@api_view(['GET'])
def api_get_rulespage_data(request, languageID):    
    try:       
        articles = RulespageArticles.objects.filter(language=languageID).order_by('step')
        serialized_articles = serialize('json', articles)
        if articles.exists():
            data = {
                'result': True,
                'articles': serialized_articles
            }        
            return JsonResponse(data)
        else:
            return JsonResponse({'result': False, 'message': 'No articles found for the specified language ID'})        
    except RulespageArticles.DoesNotExist:
        return JsonResponse({'result': False, 'message': 'ERROR getting articles'})


@api_view(['GET'])
def api_get_termspage_data(request, languageID):
    print('GET TERMS PAGE DATA')
    try:       
        articles = TermspageArticle.objects.filter(language=languageID).order_by('step')
        serialized_articles = serialize('json', articles)
        if articles.exists():
            data = {
                'result': True,
                'articles': serialized_articles
            }        
            return JsonResponse(data)
        else:
            return JsonResponse({'result': False, 'message': 'No articles found for the specified language ID'})        
    except TermspageArticle.DoesNotExist:
        return JsonResponse({'result': False, 'message': 'ERROR getting articles'})
    
@api_view(['GET'])
def api_get_tokenpage_data(request, languageID):    
    try:       
        articles = TokenpageArticle.objects.filter(language=languageID).order_by('step')
        serialized_articles = serialize('json', articles)
        if articles.exists():
            data = {
                'result': True,
                'articles': serialized_articles
            }        
            return JsonResponse(data)
        else:
            return JsonResponse({'result': False, 'message': 'No articles found for the specified language ID'})        
    except TokenpageArticle.DoesNotExist:
        return JsonResponse({'result': False, 'message': 'ERROR getting articles'})
    
@api_view(['GET'])
def api_get_supportpage_data(request, languageID):
    try:       
        articles = SupportpageArticle.objects.filter(language=languageID).order_by('step')
        serialized_articles = serialize('json', articles)
        if articles.exists():
            data = {
                'result': True,
                'articles': serialized_articles
            }        
            return JsonResponse(data)
        else:
            return JsonResponse({'result': False, 'message': 'No articles found for the specified language ID'})        
    except SupportpageArticle.DoesNotExist:
        return JsonResponse({'result': False, 'message': 'ERROR getting articles'})
    
@api_view(['GET'])
def api_get_privacypolicypage_data(request, languageID):
    try:       
        articles = PrivacypolicypageArticle.objects.filter(language=languageID).order_by('step')
        serialized_articles = serialize('json', articles)
        if articles.exists():
            data = {
                'result': True,
                'articles': serialized_articles
            }        
            return JsonResponse(data)
        else:
            return JsonResponse({'result': False, 'message': 'No articles found for the specified language ID'})        
    except SupportpageArticle.DoesNotExist:
        return JsonResponse({'result': False, 'message': 'ERROR getting articles'})