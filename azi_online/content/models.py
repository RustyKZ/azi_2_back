from django.db import models

# Create your models here.
class HomepageArticles(models.Model):
    title = models.CharField('Article title', max_length=255, blank=True, null=True)
    subtitle = models.TextField('Article subtitle', blank=True, null=True)
    text = models.TextField('Article html text', blank=True, null=True)
    publicdate = models.DateTimeField('Publication date')
    image = models.ImageField('Image', upload_to='article_images/home/', blank=True, null=True)
    language = models.IntegerField('Language ID')

    def __str__(self):
        return self.title

class AboutpageArticle(models.Model):
    title = models.CharField('Article title', max_length=255, blank=True, null=True)
    subtitle = models.TextField('Article subtitle', blank=True, null=True)
    text = models.TextField('Article html text', blank=True, null=True)    
    image = models.ImageField('Image', upload_to='article_images/about/', blank=True, null=True)
    language = models.IntegerField('Language ID')

    def __str__(self):
        return self.title

class RulespageArticles(models.Model):
    step = models.IntegerField('Point of rules', unique=True)
    title = models.CharField('Article title', max_length=255, blank=True, null=True)
    subtitle = models.TextField('Article subtitle', blank=True, null=True)
    text = models.TextField('Article html text', blank=True, null=True)    
    image = models.ImageField('Image', upload_to='article_images/rules/', blank=True, null=True)
    language = models.IntegerField('Language ID')

    def __str__(self):
        return self.title
    

class TermspageArticle(models.Model):
    step = models.IntegerField('Article No', unique=True)
    title = models.CharField('Article title', max_length=255, blank=True, null=True)
    subtitle = models.TextField('Article subtitle', blank=True, null=True)
    text = models.TextField('Article html text', blank=True, null=True)    
    image = models.ImageField('Image', upload_to='article_images/terms/', blank=True, null=True)
    language = models.IntegerField('Language ID')

    def __str__(self):
        return self.title

class TokenpageArticle(models.Model):
    step = models.IntegerField('Article No', unique=True)
    title = models.CharField('Article title', max_length=255, blank=True, null=True)
    subtitle = models.TextField('Article subtitle', blank=True, null=True)
    text = models.TextField('Article html text', blank=True, null=True)    
    image = models.ImageField('Image', upload_to='article_images/token/', blank=True, null=True)
    language = models.IntegerField('Language ID')

    def __str__(self):
        return self.title

class SupportpageArticle(models.Model):
    step = models.IntegerField('Article No')
    title = models.CharField('Article title', max_length=255, blank=True, null=True)
    subtitle = models.TextField('Article subtitle', blank=True, null=True)
    text = models.TextField('Article html text', blank=True, null=True)    
    image = models.ImageField('Image', upload_to='article_images/support/', blank=True, null=True)
    language = models.IntegerField('Language ID')

    def __str__(self):
        return self.title
    
class PrivacypolicypageArticle(models.Model):
    step = models.IntegerField('Article No')
    title = models.CharField('Article title', max_length=255, blank=True, null=True)
    subtitle = models.TextField('Article subtitle', blank=True, null=True)
    text = models.TextField('Article html text', blank=True, null=True)    
    image = models.ImageField('Image', upload_to='article_images/support/', blank=True, null=True)
    language = models.IntegerField('Language ID')

    def __str__(self):
        return self.title
