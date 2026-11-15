from django.db import models
from django.db.models import Count

from django.db import models
from django.db.models import Count


class QuestionManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(is_active=True)
            .select_related('user', 'user__user')
            .prefetch_related('tags')
            .annotate(answers_count=Count('answers'))
        )

    def new(self):
        return self.get_queryset().order_by('-created')

    def hot(self):
        return self.get_queryset().order_by('-rating', '-created')

    def by_tag(self, tag_name):
        return self.get_queryset().filter(tags__name=tag_name).order_by('-created')

    def with_details(self):
        return self.get_queryset()


class AnswerManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(is_active=True)
            .select_related('user', 'user__user')
        )

    def for_question(self, question):
        return self.get_queryset().filter(question=question).order_by('-rating', '-created')