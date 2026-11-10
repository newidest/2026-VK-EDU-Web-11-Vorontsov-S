from django.shortcuts import render


def login_view(request):
    return render(request, 'core/login.html')

def signup_view(request):
    return render(request, 'core/signup.html')

def profile_view(request):
    test_user={
        "username":"test_user",
        "email":"test@mail.ru",
        "is_authenticated":True,
    }
    context={
        "user":test_user,
    }
    return render(request, 'core/profile.html',context)