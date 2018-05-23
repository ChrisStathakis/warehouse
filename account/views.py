from django.shortcuts import render
from django.contrib import auth
from django.views.generic import ListView, CreateView, UpdateView
from django.template.context_processors  import csrf
from django.shortcuts import HttpResponse, HttpResponseRedirect, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator


from .forms import CreateUserAdmin, CostumerAccountAdminForm
from .models import User, CostumerAccount, ExtendsUser

# Create your views here.

def register_or_login(request):
    login_form = LoginForm()
    register_form = RegisterForm()
    if 'login_button' in request.POST:
        login_form = LoginForm(request.POST or None)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username_login')
            password = login_form.cleaned_data.get('password_login')
            print(username, password)
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
            return HttpResponseRedirect(reverse('profile-page'))
    if 'register_button' in request.POST:
        register_form = RegisterForm(request.POST or None)
        if register_form.is_valid():
            user = register_form.save()
            username = register_form.cleaned_data.get('username')
            password = register_form.cleaned_data.get('password')
            # user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse('profile-page'))
    context = locals()
    return render(request, 'home/login.html', context)


def create_user(request):
    username = request.POST['username']
    password = request.POST['password']
    email =request.POST['email']
    user_auth = auth.authenticate(username=username,password=password)
    if user_auth is not None:
        auth.login(request,user_auth)
        return HttpResponseRedirect(request,'logged_in.html')
    else:
        return render(request,'invalid_log.html')


def auth_view(request):
    username = request.POST['username']
    password= request.POST['password']

    user = auth.authenticate(username=username,password=password)
    if user:
        auth.login(request,user)
        return HttpResponseRedirect('/accounts/logged_in/')
    else:
        return render(request,'invalid_log.html')


def logged_in(request):
    context = {
        'full_name':request.user.username
    }
    return render(request,'logged_in.html',context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



#  dashboard urls

@method_decorator(staff_member_required, name='dispatch')
class UserListView(ListView):
    template_name = 'accounts/dash_user_list.html'
    model = CostumerAccount
    paginate_by = 50

    
@method_decorator(staff_member_required, name='dispatch')
class UserUpdateView(UpdateView):
    template_name = 'dash_ware/form.html'
    model = CostumerAccount
    form_class = CostumerAccountAdminForm
    success_url = reverse_lazy('accounts:dash_list')

    def get_initial(self):
        initial = super(UserUpdateView,self).get_initial()
        initial['email'] = self.object.user.email
        print(self.object.user.email)
        return initial

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        page_title = f'{self.object}'
        back_url = self.success_url
        context.update(locals())
        return context




@method_decorator(staff_member_required, name='dispatch')
class UserCreateView(CreateView):
    template_name = 'dash_ware/form.html'
    model = User
    form_class = CreateUserAdmin
 

    def get_success_url(self):
        get_last_object = User.objects.last()
        return reverse('accounts:dash_update', kwargs={'pk': get_last_object.id})


@staff_member_required
def delete_user(request, pk):
    pass