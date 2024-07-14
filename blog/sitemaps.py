from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from .models import Post
from predict.models import IrisPredResults, LifeStylePredResults

class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Post.objects.all()
    
    def lastmod(self, obj):
        return obj.post_date
    
    def location(self, obj):
        return reverse('article-detail', args=[obj.slug])
    
class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'monthly'

    def items(self):
        return ['home', 'add_post', 'add_category', 'category-list', 'search-articles']
    
    def location(self, obj):
        return reverse(obj)

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Post.objects.values_list('category', flat=True).distinct()
    
    def location(self, obj):
        return reverse('category', args=[obj])
    
class PredictViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return [
            'predict:prediction_page', 
            'predict:iris_prediction_page', 
            'predict:life_style_prediction_page', 
            'predict:results',
            'predict:iris_results',
            'predict:life_style_results',
        ]
    
    def location(self, obj):
        return reverse(obj)
