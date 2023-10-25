from django.contrib import admin
from .models import Post, Category, Profile, Comment

# let Post entry show up at admin page
admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Profile)
admin.site.register(Comment)
