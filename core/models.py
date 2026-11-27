from django.utils import timezone
import os
import uuid
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('default_user', 'Пользователь'),
        ('admin', 'Администратор'),
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь',
    )
    nickname = models.CharField(max_length=64, verbose_name='Никнейм')

    def avatar_upload_to(instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        date_path = timezone.now().strftime('%Y/%m/%d')
        return f'avatars/{date_path}/{uuid.uuid4().hex}{ext}'
    avatar = models.ImageField(
        upload_to=avatar_upload_to,
        blank=True,
        null=True,
        verbose_name='Аватар',
    )
    role = models.CharField(
        max_length=32,
        choices=ROLE_CHOICES,
        default='default_user',
        verbose_name='Роль',
    )

    def __str__(self):
        return self.nickname or self.user.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'