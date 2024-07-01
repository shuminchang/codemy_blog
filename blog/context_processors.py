from django.contrib.auth.models import User
from blog.models import Post, Category

def sidebar_data(request):
    superuser = User.objects.filter(is_superuser=True).first()
    latest_posts = Post.objects.all().order_by('-post_date')[:3]
    categories = Category.objects.all()

    superuser_profile = None
    if superuser:
        superuser_profile = getattr(superuser, 'profile', None)

    return {
        'superuser': superuser,
        'superuser_profile': superuser_profile,
        'latest_posts': latest_posts,
        'categories': categories,
    }
