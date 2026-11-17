
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return [
            "home",
            "about",
            "how_it_works",
            "contact",
            "privacy_policy",
        ]

    def location(self, item):
        return reverse(item)
