from django.db import models, transaction
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.urls import reverse
from core.models import Profile
from .managers import QuestionManager, AnswerManager, TagManager


class Tag(models.Model):
    name = models.CharField(max_length=32, unique=True, verbose_name='Название')
    objects=TagManager()

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

    def update_rating(self):
        self.rating = self.likes.aggregate(total=Sum('like'))['total'] or 0
        self.save(update_fields=['rating'])
        return self.rating

    def toggle_vote(self, profile, vote_type):
        value = 1 if vote_type == 'like' else -1
        with transaction.atomic():
            post = type(self).all_objects.select_for_update().get(pk=self.pk)
            vote, created = post.likes.get_or_create(user=profile,defaults={'like': value},)

            if not created and vote.like == value:
                vote.delete()
                vote_state = None
            else:
                if not created:
                    vote.like = value
                    vote.save(update_fields=['like'])
                vote_state = vote_type

            rating = post.update_rating()
            self.rating = rating
        return rating, vote_state

    @classmethod
    def attach_vote_state(cls, items, user):
        items = list(items)
        if not items or not user.is_authenticated or not hasattr(user, 'profile'):
            return items
        field = cls._meta.model_name
        votes = dict(
            cls.likes.rel.related_model.objects.filter(
                user=user.profile,
                **{f'{field}_id__in': [obj.id for obj in items]},
            ).values_list(f'{field}_id', 'like')
        )
        for obj in items:
            vote = votes.get(obj.id)
            obj.vote_state = 'like' if vote == 1 else 'dislike' if vote == -1 else None
        return items
    
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

    @classmethod
    def attach_answer_counts(cls, questions):
        items = list(questions)
        if not items:
            return items
        ids = [q.id for q in items]
        counts = dict(cls.objects.with_details().filter(id__in=ids).values_list('id', 'answer_count'))
        for q in items:
            q.answer_count = counts.get(q.id, 0)
        return items

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        indexes=[models.Index(fields=['-created']),]


class Answer(BasePost):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')
    objects = AnswerManager()
    all_objects = models.Manager()

    def __str__(self):
        return f'Ответ #{self.pk}'
    def toggle_correct(self):
        with transaction.atomic():
            Question.all_objects.select_for_update().get(pk=self.question_id)
            answer = Answer.all_objects.select_for_update().get(pk=self.pk)

            new_state = not answer.is_correct
            if new_state:
                Answer.all_objects.filter(question_id=self.question_id, is_correct=True).update(is_correct=False)

            answer.is_correct = new_state
            answer.save(update_fields=['is_correct'])
            self.is_correct = new_state
        return self.is_correct

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        constraints = [
            models.UniqueConstraint(
                fields=['question'],
                condition=Q(is_correct=True),
                name='unique_correct_answer_per_question',
            )
        ]


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