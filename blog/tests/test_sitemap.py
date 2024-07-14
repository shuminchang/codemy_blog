from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.sitemaps import views as sitemap_views

class SitemapTestCase(TestCase):
    def test_sitemap_index(self):
        response = self.client.get(reverse('django.contrib.sitemaps.views.sitemap'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<urlset', html=False)

    def test_sitemap_urls(self):
        sitemap_url = reverse('django.contrib.sitemaps.views.sitemap')
        response = self.client.get(sitemap_url)
        sitemap_urls = [url.split('</loc>')[0].split('<loc>')[1] for url in response.content.decode().split('<url>')[1:]]

        for url in sitemap_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
