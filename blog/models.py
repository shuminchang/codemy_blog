from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, date
from ckeditor.fields import RichTextField
from django.template.defaultfilters import slugify
from unidecode import unidecode

def custom_slugify(value):
    return slugify(unidecode(value))

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('home')

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    bio = models.TextField()
    profile_pic = models.ImageField(null=True, blank=True, upload_to="images/profile/")
    website_url = models.CharField(max_length=255, null=True, blank=True)
    facebook_url = models.CharField(max_length=255, null=True, blank=True)
    twitter_url = models.CharField(max_length=255, null=True, blank=True)
    instagram_url = models.CharField(max_length=255, null=True, blank=True)
    pinterest_url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.user)
    
    def get_absolute_url(self):
        return reverse('home')

class Post(models.Model):
    title = models.CharField(max_length=255)
    header_image = models.ImageField(null=True, blank=True, upload_to="images/")
    # title_tag = models.CharField(max_length=255, default="My Blog")
    # title_tag = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # body = models.TextField()
    body = RichTextField(blank=True, null=True)
    post_date = models.DateField(auto_now_add=True)
    category = models.CharField(max_length=255, default='coding')
    snippet = models.CharField(max_length=255)
    likes = models.ManyToManyField(User, related_name='blog_posts')
    slug = models.SlugField(unique=True, max_length=255, blank=True)

    def total_like(self):
        return self.likes.count()

    def __str__(self):
        return self.title + ' | ' + str(self.author) # self.author is an object, should turn it into a string
    
    def get_absolute_url(self):
        return reverse('article-detail', args=[self.slug])
        # return reverse('home')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = custom_slugify(self.title)
        else:
            self.slug = custom_slugify(self.slug)
        super(Post, self).save(*args, **kwargs)

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    body = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.post.title, self.name)