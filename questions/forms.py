from django import forms
from questions.models import Answer,Question, Tag
from django.core.exceptions import ValidationError
from django.core.validators import validate_unicode_slug


class AnswerForm(forms.ModelForm):
    content = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'class': 'settings-form',
            'rows': 4,
            'placeholder': 'Введите свой ответ',
        }),
        required=False,
    )

    class Meta:
        model = Answer
        fields = ('content',)

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if len(content) < 5:
            raise forms.ValidationError('Ответ слишком короткий. Минимум 5 символов.')

        if len(content) > 2000:
            raise forms.ValidationError('Ответ слишком длинный. Максимум 2000 символов.')
        return content

    def save(self, author, question, commit=True):
        answer = super().save(commit=False)
        answer.user = author
        answer.question = question
        if commit:
            answer.save()
        return answer


class AskForm(forms.ModelForm):
    title=forms.CharField(
        label='title',
        max_length=128,
        help_text='4-128 символов',
        widget=forms.TextInput(attrs={'id': 'question-title'}),
        required=True
    )
    content = forms.CharField(
        label='content',
        help_text='max 2048 символов',
        widget=forms.Textarea(attrs={
            'id': 'question-text',
            'rows': 4,
            'placeholder': 'Введите свой вопрос',
        }),
        required=True,
    )
    tags=forms.CharField(
        label='tags',
        min_length=4,
        max_length=128,
        help_text='через запятую, например: Django, Python, SQL',
        widget=forms.TextInput(attrs={'id': 'question-tags','placeholder':'Перечислите теги',}),
        required=False
    )
    class Meta:
        model=Question
        fields=('title','content')

    def clean_title(self):
        title=self.cleaned_data.get('title','').strip()
        if len(title)<4:
            raise forms.ValidationError('минимум 4 символа')
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if len(content) < 5:
            raise ValidationError('Описание слишком короткое. Минимум 5 символов.')
        if len(content) > 2048:
            raise ValidationError('Описание слишком длинное. Максимум 2048 символов.')
        return content

    def clean_tags(self):
        raw_tags = self.cleaned_data.get('tags', '')
        tag_names = []
        seen=set()
        for tag in raw_tags.split(','):
            tag = tag.strip().lower()
            if not tag:
                continue
            if len(tag) > 32:
                raise ValidationError(f'Тег "{tag}" длиннее 32 символов.')
            try:
                validate_unicode_slug(tag)
            except ValidationError:
                raise ValidationError(f'Недопустимый тег "{tag}". Разрешены только буквы, цифры, дефис и подчёркивание.')
            if tag not in seen:
                seen.add(tag)
                tag_names.append(tag)
        if len(seen)>3:
            raise ValidationError('Максимум 3 тега')
        return tag_names

    def save(self, author, commit=True):
        question = super().save(commit=False)
        question.user = author
        tag_names = self.cleaned_data.get('tags', [])
        if commit:
            question.save()
            tag_objects = [
                Tag.objects.get_or_create(name=name)[0]
                for name in tag_names
            ]
            question.tags.set(tag_objects)

        return question

class VoteForm(forms.Form):
    vote_choices = (('like', 'Like'),('dislike', 'Dislike'),)
    vote_type = forms.ChoiceField(choices=vote_choices)

class MarkCorrectForm(forms.Form):
    question_id = forms.IntegerField(min_value=1)
    answer_id = forms.IntegerField(min_value=1)