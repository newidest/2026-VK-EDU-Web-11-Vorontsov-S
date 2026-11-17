from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count

from .models import Question, Answer, Tag
from core.models import Profile


def get_base_context():
    return {
        'popular_tags': Tag.objects.annotate(num_questions=Count('questions')).order_by('-num_questions')[:10],
        'best_members': Profile.objects.select_related('user').order_by('-id')[:5],
    }


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages or 1)

    if page.object_list and hasattr(page.object_list[0], 'title'):
        ids = [q.id for q in page.object_list]
        counts = dict(
            Question.objects.filter(id__in=ids)
            .annotate(cnt=Count('answers'))
            .values_list('id', 'cnt')
        )
        for q in page.object_list:
            q.answer_count = counts.get(q.id, 0)

    return page


def render_page(request, template_name, queryset=None, per_page=10, extra_context=None):
    context = get_base_context()
    if queryset is not None:
        context['page_obj'] = paginate(queryset, request, per_page=per_page)
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


def index(request):
    return render_page(request, 'questions/index.html', Question.objects.new(), per_page=4)


def hot(request):
    return render_page(request, 'questions/hot.html', Question.objects.hot(), per_page=5)


def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    return render_page(
        request,
        'questions/tag.html',
        Question.objects.by_tag(tag_obj.name),
        per_page=4,
        extra_context={'tag_name': tag_obj.name},
    )


def question(request, question_id):
    item = get_object_or_404(Question.objects.with_details(), pk=question_id)
    item.answer_count = item.answers.count()
    return render_page(
        request,
        'questions/question.html',
        Answer.objects.for_question(item),
        per_page=5,
        extra_context={'question': item},
    )


def ask(request):
    return render_page(request, 'questions/ask.html')