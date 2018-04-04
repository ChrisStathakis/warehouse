import datetime
from ..reports_tools import diff_month
from products.models import *
from inventory_manager.models import *
from django.conf import settings
from django.db.models import Q, F
from dateutil.relativedelta import relativedelta
currency = settings.CURRENCY


def date_pick_form(request, date_pick): # gets the day form date_pick input and convert it to string its
    if date_pick:
        try:
            date_range = date_pick.split('-')
            date_range[0]=date_range[0].replace(' ','')
            date_range[1]=date_range[1].replace(' ','')
            date_start =datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
            date_end =datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
            request.session['date_range'] = date_pick
            date_end = date_end + relativedelta(days=1)
            return [date_start, date_end]
        except:
            date_pick = None
            return [None,None]


def reports_initial_date(request):
    date_start = datetime.datetime.now().replace(month=1, day=1)
    date_end = datetime.datetime.now()
    date_range = '%s - %s' %(str(date_start).split(' ')[0].replace('-','/'), str(date_end).split(' ')[0].replace('-','/'))
    return [date_start, date_end, date_range]


def split_months(date_start , date_end):
    months_list = []
    month = date_end.month
    months = diff_month(date_start, date_end)
    for ele in range(months+1):
        months_list.append(datetime.datetime(datetime.datetime.now().year, month, 1).month)
        month -= 1
    return months_list





