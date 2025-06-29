from rest_framework import serializers
from .models import AboutpageArticle
import json

class AboutpageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutpageArticle
        fields = '__all__'
