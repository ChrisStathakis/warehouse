from django.views.generic import ListView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from account.models import User, CostumerAccount


@method_decorator(staff_member_required, name='dispatch')
class UsersPage(ListView):
    model = CostumerAccount
    template_name = 'dashboard/user_section/index.html'

    def get_context_data(self, **kwargs):
        context = super(UsersPage, self).get_context_data(**kwargs)

        return context

