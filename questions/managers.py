from django.db import models
from django.db.models import Count

class TagManager(models.Manager):
    def popular(self,limit=10):
        return self.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10]

class QuestionManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(is_active=True)
            .select_related('user', 'user__user')
            .prefetch_related('tags')
        )
    def new(self):
        return self.get_queryset().order_by('-created')

    def hot(self):
        return self.get_queryset().order_by('-rating', '-created')

    def by_tag(self, tag_name):
        return self.get_queryset().filter(tags__name=tag_name).order_by('-rating')

    def with_details(self):
        return self.get_queryset().annotate(answer_count=Count('answers'))


class AnswerManager(models.Manager):
    def get_queryset(self):
        return (
            super().get_queryset()
            .filter(is_active=True)
            .select_related('user', 'user__user')
        )

    def for_question(self, question):
        return self.get_queryset().filter(question=question).order_by('-rating', '-created')