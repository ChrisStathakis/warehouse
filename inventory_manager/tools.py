from django.db.models import Q
from .models import *


def initial_date(request, months=3):
    #gets the initial last three months or the session date
    date_now = datetime.datetime.today()
    try:
        date_range = request.session['date_range']
        date_range = date_range.split('-')
        date_range[0] = date_range[0].replace(' ','')
        date_range[1] = date_range[1].replace(' ','')
        date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end = datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
    except:
        date_three_months_ago = date_now - relativedelta(months=months)
        date_start = date_three_months_ago
        date_end = date_now
        date_range = '%s - %s' % (str(date_three_months_ago).split(' ')[0].replace('-','/'),str(date_now).split(' ')[0].replace('-','/'))
        request.session['date_range'] = '%s - %s'%(str(date_three_months_ago).split(' ')[0].replace('-','/'),str(date_now).split(' ')[0].replace('-','/'))
    return [date_start, date_end, date_range]


def clean_date_filter(request, date_pick, date_start=None, date_end=None, date_range=None):
    try:
        date_range = date_pick.split('-')
        date_range[0] = date_range[0].replace(' ', '')
        date_range[1] = date_range[1].replace(' ', '')
        date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end = datetime.datetime.strptime(date_range[1], '%m/%d/%Y')
        date_range = '%s - %s' % (date_range[0], date_range[1])
    except:
        date_start, date_end, date_range = [date_start, date_end, date_range] if date_start and date_end else \
            initial_date(request)
    return [date_start, date_end, date_range]


def estimate_date_start_end_and_months(request):
    day_now, start_year = datetime.datetime.now(), datetime.datetime(datetime.datetime.now().year, 2, 1)
    date_pick = request.GET.get('date_pick', None)
    start_year, day_now, date_range = clean_date_filter(request, date_pick, date_start=start_year, date_end=day_now)
    months_list=12
    # gets the total months of the year
    '''
    months_list, month = [], 1
    months = diff_month(start_year, day_now)
    while month <= months + 1:
        months_list.append(datetime.datetime(datetime.datetime.now().year, month, 1).month)
        month += 1
    '''
    return [start_year, day_now, date_range, months_list]

