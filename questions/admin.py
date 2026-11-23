from django.contrib import admin
from .models import Tag,Question,Answer,QuestionLike,AnswerLike

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display=('id','name')
    search_fields=('name',)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    raw_id_fields = ('user',)
    fields = ('user', 'content', 'rating', 'is_active')

    def get_queryset(self, request):
        return self.model.all_objects.select_related('user', 'user__user')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'rating', 'is_active', 'created')
    list_filter = ('is_active', 'created')
    search_fields = ('title', 'content')
    autocomplete_fields = ('tags',)
    raw_id_fields = ('user',)
    inlines = (AnswerInline,)

    def get_queryset(self, request):
        return self.model.all_objects.select_related('user', 'user__user')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'user', 'rating', 'is_active', 'created')
    list_filter = ('is_active', 'created')
    search_fields = ('content',)
    raw_id_fields = ('question', 'user')

    def get_queryset(self, request):
        return self.model.all_objects.select_related('question', 'user', 'user__user')

@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'like')
    list_filter = ('like',)
    raw_id_fields = ('user', 'question')
    list_select_related=('user','user__user','question')

@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'answer', 'like')
    list_filter = ('like',)
    raw_id_fields = ('user', 'answer')
    list_select_related = ('user', 'user__user', 'answer')