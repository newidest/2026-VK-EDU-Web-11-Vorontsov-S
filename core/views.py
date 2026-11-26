from django.shortcuts import render
from core.forms import LoginForm, RegisterForm, ProfileForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_POST
from questions.views import render_page
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    next_url = request.POST.get('next') or request.GET.get('next')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return HttpResponseRedirect(next_url)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = LoginForm()

    context = {
        'form': form,
        'next': next_url or '',
    }
    return render_page(request, 'core/login.html', extra_context=context)

def register_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method=='POST':
        form =RegisterForm(request.POST,request.FILES)
        if form.is_valid():
            user=form.save()
            login(request,user)
            return HttpResponseRedirect(reverse('index'))
    else:
        form=RegisterForm()
    
    return render_page(request,'core/register.html',extra_context={'form':form})


@require_POST
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def profile_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    profile=request.user.profile
    saved=False
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"{reverse('profile')}?saved=1")
    else:
        form = ProfileForm(instance=profile)
        saved = request.GET.get('saved') == '1'
    
    context={
        'form':form,
        'saved':saved,
    }
    return render_page(request,'core/profile.html',extra_context=context)