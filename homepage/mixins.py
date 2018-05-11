from django.urls import reverse
from urllib.parse import urlencode
from django.shortcuts import  HttpResponseRedirect

def custom_redirect(url_name, *args, **kwargs):
    url = reverse(url_name, args=args)
    params = urlencode(kwargs)
    return HttpResponseRedirect(url + "?%s" % params)


class SearchMixin:

    def get(self, *args, **kwargs):
        if 'search_name' in self.request.GET:
            search_name = self.request.GET.get('search_name')
            return custom_redirect('search_page', search_name=search_name)
        return super(SearchMixin, self).get(*args, **kwargs)