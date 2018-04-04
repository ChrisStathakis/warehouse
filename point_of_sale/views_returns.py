from django.shortcuts import HttpResponseRedirect, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import ListView, UpdateView

from .models import *
from .forms import *
from account.models import *
