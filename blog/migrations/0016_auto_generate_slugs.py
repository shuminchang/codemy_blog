from django.db import migrations
from django.utils.text import slugify

def generate_slugs(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    for post in Post.objects.all():
        if not post.slug:
            post.slug = slugify(post.title)
            post.save()

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0015_alter_post_slug'),
    ]

    operations = [
        migrations.RunPython(generate_slugs),
    ]

