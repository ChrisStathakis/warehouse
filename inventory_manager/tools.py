from django.db.models import Q
from .models import *

def warehouse_orders_query(queryset, search_pro):
    new_queryset = queryset.filter(Q(title__icontains=search_pro) |
                                   Q(vendor__title__icontains=search_pro) |
                                   Q(code__icontains=search_pro) |
                                   Q(notes__icontains=search_pro)
                                   ).distinct()
    return new_queryset