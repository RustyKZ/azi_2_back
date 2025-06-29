from rest_framework import serializers
from .models import Header, Footer, Languages, SingupForm, LoginForm, ModalError, UserProfile, UserReview, Homepage, TablesHall, PlayTable, CreateTable, AccessDenied, PageNotFound, ServerError, SandboxTable, UserHistory, Toplist, RecoveryForm
import json

class HeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Header
        fields = '__all__'

class FooterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Footer
        fields = '__all__'

class LanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = '__all__'

class SignupFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingupForm
        fields = '__all__'

class LoginFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginForm
        fields = '__all__'

class ErrorSerializer(serializers.Serializer):
    number = serializers.IntegerField()
    title = serializers.CharField(max_length=100)
    content = serializers.CharField()
    button = serializers.CharField()

class ModalErrorSerializer(serializers.ModelSerializer):
    error = serializers.SerializerMethodField()
    class Meta:
        model = ModalError
        fields = ['label', 'error']
    def get_error(self, obj):
        # Проверяем, что поле error не пусто
        if obj.error:
            # Преобразуем строку JSON в список объектов
            return json.loads(obj.error)
        else:
            return []

class UserProfileSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    states = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ['label', 'form', 'states']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)    
        else:
            return []
    def get_states(self, obj):        
        if obj.states:            
            return json.loads(obj.states)
        else:
            return []

class UserReviewSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    class Meta:
        model = UserReview
        fields = ['label', 'form']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)
        else:
            return []
    
class HomepageSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    class Meta:
        model = Homepage
        fields = ['label', 'form']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)
        else:
            return []

class TablesHallSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    class Meta:
        model = TablesHall
        fields = ['label', 'form']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)
        else:
            return []

class PlayTableSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    class Meta:
        model = PlayTable
        fields = ['label', 'form']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)
        else:
            return []

class CreateTableSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    class Meta:
        model = CreateTable
        fields = ['label', 'form']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)
        else:
            return []

class AccessDeniedSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    class Meta:
        model = AccessDenied
        fields = ['label', 'form']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)
        else:
            return []

class PageNotFoundSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    class Meta:
        model = PageNotFound
        fields = ['label', 'form']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)
        else:
            return []

class ServerErrorSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    class Meta:
        model = ServerError
        fields = ['label', 'form']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)
        else:
            return []

class SandboxTableSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    class Meta:
        model = SandboxTable
        fields = ['label', 'form']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)
        else:
            return []

class UserHistorySerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    class Meta:
        model = UserHistory
        fields = ['label', 'form']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)
        else:
            return []

class ToplistSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    class Meta:
        model = Toplist
        fields = ['label', 'form']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)
        else:
            return []
        
class RecoveryFormSerializer(serializers.ModelSerializer):
    form = serializers.SerializerMethodField()
    class Meta:
        model = RecoveryForm
        fields = ['label', 'form']
    def get_form(self, obj):
        if obj.form:            
            return json.loads(obj.form)
        else:
            return []