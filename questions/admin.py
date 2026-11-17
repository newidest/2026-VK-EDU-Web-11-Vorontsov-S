from django.contrib import admin
from .models import Tag,Question,Answer,QuestionLike,AnswerLike

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display=('id','name')
    search_fields=('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display=('id','title','user','rating','is_active','created')
    list_filter=('is_active','created')
    search_fields=('title','content')
    filter_horizontal = ('tags',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'user', 'rating', 'is_active', 'created')
    list_filter = ('is_active', 'created')
    search_fields=('content',)

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'like')
    list_filter = ('like',)
    raw_id_fields = ('user', 'question')

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'answer', 'like')
    list_filter = ('like',)
    raw_id_fields = ('user', 'answer')