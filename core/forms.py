from django import forms
from django.contrib.auth.models import User
import os
from core.models import Profile
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate


ALLOWED_IMAGE_EXT=('.jpg','.jpeg','.png',)
MAX_AVATAR_SIZE=2*1024*1024

def validate_avatar(avatar):
    if not avatar:
        return avatar
    ext=os.path.splitext(avatar.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXT:
        raise forms.ValidationError('Недопустимый формат файла. Разрешены только: jpg, jpeg, png')
    
    if avatar.size> MAX_AVATAR_SIZE:
        raise forms.ValidationError('Размер файла слишком большой. Максимум 2 мб')
    return avatar

class LoginForm(forms.Form):
    username = forms.CharField(
        min_length=4,
        max_length=32,
        label='Login',
        help_text='4-32 символа',
        widget=forms.TextInput(attrs={'class': 'settings-form'}),
    )
    password = forms.CharField(
        min_length=8,
        max_length=64,
        label='Password',
        help_text='Минимум 8 символов',
        widget=forms.PasswordInput(attrs={'class': 'settings-form'}),
    )

    def __init__(self,*args,**kwargs):
        self._user=None
        super().__init__(*args,**kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self._user = authenticate(username=username, password=password)
            if self._user is None:
                raise forms.ValidationError('Неправильные имя или пароль')

        return cleaned_data

    def get_user(self):
        return self._user


class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        min_length=4,
        max_length=32,
        label='Login',
        help_text='4-32 символа',
        widget=forms.TextInput(attrs={'class': 'settings-form'}),
    )
    email = forms.EmailField(
        max_length=64,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'settings-form'}),
    )
    nickname = forms.CharField(
        min_length=2,
        max_length=64,
        label='NickName',
        help_text='2-64 символа',
        widget=forms.TextInput(attrs={'class': 'settings-form'}),
    )
    password = forms.CharField(
        min_length=8,
        max_length=64,
        label='Password',
        help_text='Минимум 8 символов',
        widget=forms.PasswordInput(attrs={'class': 'settings-form'}),
    )
    password2 = forms.CharField(
        min_length=8,
        max_length=64,
        label='Repeat password',
        widget=forms.PasswordInput(attrs={'class': 'settings-form'}),
    )
    avatar = forms.ImageField(
        label='Avatar',
        required=False,
        help_text='JPG, JPEG или PNG, max 2 MB',
        widget=forms.ClearableFileInput(attrs={
            'class': 'settings-form',
            'accept': '.jpg,.jpeg,.png',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'nickname', 'password', 'password2', 'avatar')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email is required')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists')
        return email

    def clean_avatar(self):
        return validate_avatar(self.cleaned_data.get('avatar'))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This login is already taken')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError('Passwords do not match')

        if password:
            validate_password(password)

        return cleaned_data

    def save(self, commit=True):
        nickname = self.cleaned_data.pop('nickname')
        avatar = self.cleaned_data.pop('avatar', None)
        self.cleaned_data.pop('password2')

        user = User.objects.create_user(**self.cleaned_data)
        Profile.objects.create(user=user, nickname=nickname, avatar=avatar)
        return user

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(
        max_length=64,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'settings-form'}),
    )
    nickname = forms.CharField(
        min_length=2,
        max_length=64,
        label='NickName',
        help_text='2-64 символов',
        widget=forms.TextInput(attrs={'class': 'settings-form'}),
    )
    avatar = forms.ImageField(
        label='Avatar',
        required=False,
        help_text='JPG, JPEG or PNG, max 2 MB',
        widget=forms.FileInput(attrs={
            'class': 'settings-form',
            'accept': '.jpg,.jpeg,.png,.webp',
        }),
    )
    field_order=['nickname','email','avatar']
    class Meta:
        model = Profile
        fields = ('nickname', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields['email'].initial = self.instance.user.email

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.user_id).exists():
            raise forms.ValidationError('Email already exists')
        return email

    def clean_avatar(self):
        return validate_avatar(self.cleaned_data.get('avatar'))

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.email = self.cleaned_data['email']
        if commit:
            profile.user.save()
            profile.save()
        return profile

