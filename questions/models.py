from django.db import models
from django.urls import reverse
from core.models import Profile
from .managers import QuestionManager, AnswerManager, TagManager


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True, verbose_name='Название')
    objects=TagManager 

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class BasePost(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Автор')
    rating = models.IntegerField(default=0, verbose_name='Рейтинг')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    content = models.CharField(max_length=2048, verbose_name='Контент')

    class Meta:
        abstract = True


class Question(BasePost):
    title = models.CharField(max_length=128, verbose_name='Заголовок')
    tags = models.ManyToManyField(Tag, blank=True, related_name='questions', verbose_name='Теги')
    objects = QuestionManager()
    all_objects=models.Manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('question', kwargs={'question_id': self.pk})

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Answer(BasePost):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')
    objects = AnswerManager()
    all_objects = models.Manager()

    def __str__(self):
        return f'Ответ #{self.pk}'

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'


class BaseLike(models.Model):
    LIKE_CHOICES = (
        (-1, 'Дизлайк'),
        (0, 'Ничего'),
        (1, 'Лайк'),
    )
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Пользователь')
    like = models.SmallIntegerField(choices=LIKE_CHOICES, default=0, verbose_name='Оценка')

    class Meta:
        abstract = True


class QuestionLike(BaseLike):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes', verbose_name='Вопрос')

    class Meta:
        verbose_name = 'Оценка вопроса'
        verbose_name_plural = 'Оценки вопросов'
        unique_together = ('user', 'question')


class AnswerLike(BaseLike):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes', verbose_name='Ответ')

    class Meta:
        verbose_name = 'Оценка ответа'
        verbose_name_plural = 'Оценки ответов'
        unique_together = ('user', 'answer')