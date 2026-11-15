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
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
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