from ..views import *
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models.functions import TruncMonth


def ajax_outcomes(request):
    print('its the view nab')
    data = dict()
    #date_start, date_end, date_range, months_list = estimate_date_start_end_and_months(request)
    #payment_orders = PaymentOrders.objects.filter(date_expired__range=[date_start, date_end], is_expense=True)
    #payment_total = payment_orders.aggregate(Sum('value'))['value__sum'] if payment_orders.exists() else 0
    #payment_paid = payment_orders.filter(is_paid=True).aggregate(Sum('value'))['value__sum'] if payment_orders.filter(is_paid=True).exists() else 0
    '''
    context = 'hello'
    data['last_year'] = render_to_string(request=request,
                                        template_name='report/ajax/outcomes/ajax_outcomes.html',
                                        context=context
                                        )
    '''
    return JsonResponse(data)     