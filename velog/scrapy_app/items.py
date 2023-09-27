from scrapy_djangoitem import DjangoItem
from testapp.models import Search

class ScrapyAppItem(DjangoItem):
    django_model = Search
    pass