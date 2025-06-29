from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from interface.models import Header, Languages, Footer, SingupForm, LoginForm, ModalError, UserProfile, UserReview, Homepage, TablesHall, PlayTable, CreateTable, AccessDenied, PageNotFound, ServerError, SandboxTable, UserHistory, Toplist, RecoveryForm
from interface.serializers import HeaderSerializer, LanguagesSerializer, FooterSerializer, SignupFormSerializer, LoginFormSerializer, ModalErrorSerializer, UserProfileSerializer, UserReviewSerializer, HomepageSerializer, TablesHallSerializer, PlayTableSerializer, CreateTableSerializer, AccessDeniedSerializer, PageNotFoundSerializer, ServerErrorSerializer, SandboxTableSerializer, UserHistorySerializer, ToplistSerializer, RecoveryFormSerializer

from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
@api_view(['GET'])
def api_get_header(request, languageID):
    header_instance = Header.objects.filter(id=languageID).first()
    if not header_instance:
        header_instance = Header.objects.filter(id=1).first()
    if header_instance:
        serializer = HeaderSerializer(header_instance)
        return JsonResponse(serializer.data)
    else:
        return JsonResponse({'message': 'Header not found for the specified language ID'}, status=404)

@api_view(['GET'])
def api_get_languages(request):
    languages_instance = Languages.objects.all()
    serializer = LanguagesSerializer(languages_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_errors(request):
    errors_instance = ModalError.objects.all()
    serializer = ModalErrorSerializer(errors_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_footer(request, languageID):
    footer_instance = Footer.objects.filter(id=languageID).first()
    if not footer_instance:
        footer_instance = Footer.objects.filter(id=1).first()
    if footer_instance:
        serializer = FooterSerializer(footer_instance)
        return JsonResponse(serializer.data)
    else:
        return JsonResponse({'message': 'Header not found for the specified language ID'}, status=404)

def api_about(request):
    return JsonResponse({'message': 'Welcome to the API AboutPage!'})

@api_view(['GET'])
def api_get_signup_form(request, languageID):
    sf_instance = SingupForm.objects.filter(id=languageID).first()
    if not sf_instance:
        sf_instance = SingupForm.objects.filter(id=1).first()
    if sf_instance:
        serializer = SignupFormSerializer(sf_instance)
        return JsonResponse(serializer.data)
    else:
        return JsonResponse({'message': 'Header not found for the specified language ID'}, status=404)

@api_view(['GET'])
def api_get_login_form(request, languageID):
    lf_instance = LoginForm.objects.filter(id=languageID).first()
    if not lf_instance:
        lf_instance = LoginForm.objects.filter(id=1).first()
    if lf_instance:
        serializer = LoginFormSerializer(lf_instance)
        return JsonResponse(serializer.data)
    else:
        return JsonResponse({'message': 'Header not found for the specified language ID'}, status=404)

@api_view(['GET'])
def api_get_user_profile_form(request):
    profile_instance = UserProfile.objects.all()
    serializer = UserProfileSerializer(profile_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_user_review_form(request):
    profile_instance = UserReview.objects.all()
    serializer = UserReviewSerializer(profile_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_homepage_form(request, languageID):
    homepage_instance = Homepage.objects.all()
    serializer = HomepageSerializer(homepage_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_aboutpage_form(request, languageID):
    homepage_instance = Homepage.objects.all()
    serializer = HomepageSerializer(homepage_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_rulespage_form(request, languageID):
    homepage_instance = Homepage.objects.all()
    serializer = HomepageSerializer(homepage_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_tables_interface(request):
    print('API GET TABLES INTERFACE')
    tables_instance = TablesHall.objects.all()
    serializer = TablesHallSerializer(tables_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_playtable_interface(request):
    print('API GET PLAYTABLE INTERFACE')
    table_instance = PlayTable.objects.all()
    serializer = PlayTableSerializer(table_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_createtable_interface(request):
    print('API GET CREATETABLE INTERFACE')
    table_instance = CreateTable.objects.all()
    serializer = CreateTableSerializer(table_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_accessdenied_interface(request):
    print('API GET PAGE ACCESS DENIED INTERFACE')
    table_instance = AccessDenied.objects.all()
    serializer = AccessDeniedSerializer(table_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_pagenotfound_interface(request):
    print('API GET PAGE 404 INTERFACE')
    table_instance = PageNotFound.objects.all()
    serializer = PageNotFoundSerializer(table_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_servererror_interface(request):
    print('API GET PAGE 500 INTERFACE')
    table_instance = ServerError.objects.all()
    serializer = ServerErrorSerializer(table_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_sandboxtable_interface(request):
    print('API GET SANDBOX TABLE INTERFACE')
    table_instance = SandboxTable.objects.all()
    serializer = SandboxTableSerializer(table_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_user_history_interface(request):
    profile_instance = UserHistory.objects.all()
    serializer = UserHistorySerializer(profile_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_toplist_interface(request):
    profile_instance = Toplist.objects.all()
    serializer = ToplistSerializer(profile_instance, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def api_get_recovery_interface(request):
    profile_instance = RecoveryForm.objects.all()
    serializer = RecoveryFormSerializer(profile_instance, many=True)
    return JsonResponse(serializer.data, safe=False)
