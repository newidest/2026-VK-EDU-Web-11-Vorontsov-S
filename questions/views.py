from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from questions.forms import AnswerForm,AskForm, MarkCorrectForm, VoteForm
from .models import Question, Answer, Tag
from django.views.decorators.csrf import ensure_csrf_cookie

def get_base_context():
    return {'popular_tags': Tag.objects.popular()}


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(1)


def render_page(request, template_name, queryset=None, per_page=20, extra_context=None, with_answer_counts=False):
    context = get_base_context()
    if queryset is not None:
        context['page_obj'] = paginate(queryset, request, per_page=per_page)
        context['page_obj'].object_list = queryset.model.attach_vote_state(context['page_obj'].object_list, request.user)
        if with_answer_counts:
            context['page_obj'].object_list = Question.attach_answer_counts(context['page_obj'].object_list)
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


def index(request):
    return render_page(request, 'questions/index.html', Question.objects.new(), per_page=20,with_answer_counts=True)


def hot(request):
    return render_page(request, 'questions/hot.html', Question.objects.hot(), per_page=20,with_answer_counts=True)


def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    return render_page(
        request,
        'questions/tag.html',
        Question.objects.by_tag(tag_obj.name),
        per_page=20,
        extra_context={'tag_name': tag_obj.name},
        with_answer_counts=True
    )


@ensure_csrf_cookie
def question(request, question_id):
    item = get_object_or_404(Question.objects.with_details(), pk=question_id)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect(f"{reverse('login')}?next={request.path}")
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer=form.save(author=request.user.profile, question=item)
            ids = list(Answer.objects.for_question(item).values_list('id', flat=True))
            page = ids.index(answer.id) // 30 +1
            return HttpResponseRedirect(f"{reverse('question', args=[item.id])}?page={page}#answer-{answer.id}")
    else:
        form = AnswerForm()

    is_question_author = (
        request.user.is_authenticated
        and hasattr(request.user, 'profile')
        and item.user_id == request.user.profile.id
    )
    Question.attach_vote_state([item], request.user)
    return render_page(
        request,
        'questions/question.html',
        Answer.objects.for_question(item),
        per_page=30,
        extra_context={
            'question': item,
            'form': form,
            'is_question_author': is_question_author,
        },
    )

@login_required
def ask(request):
    if request.method=='POST':
        form=AskForm(request.POST)
        if form.is_valid():
            new_question=form.save(author=request.user.profile)
            return HttpResponseRedirect(reverse('question',args=[new_question.id]))
    else:
        form=AskForm()
    return render_page(request, 'questions/ask.html',extra_context={'form':form})


def csrf_failure(request, reason=''):
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({'error': 'Ошибка CSRF'}, status=403)
    return HttpResponseForbidden(reason or 'Ошибка CSRF')

def mark_correct_answer(request, question_id, answer_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Нужен POST-запрос'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Нужна авторизация', 'login_url': reverse('login')}, status=401)

    form = MarkCorrectForm({'question_id': question_id, 'answer_id': answer_id})
    if not form.is_valid():
        return JsonResponse({'error': 'Неверные параметры'}, status=400)

    q = Question.objects.filter(id=form.cleaned_data['question_id']).first()
    if not q:
        return JsonResponse({'error': 'Вопрос не найден'}, status=404)
    if q.user_id != request.user.profile.id:
        return JsonResponse({'error': 'Нет прав'}, status=403)

    answer = Answer.objects.filter(id=form.cleaned_data['answer_id'], question=q).first()
    if not answer:
        return JsonResponse({'error': 'Ответ не найден'}, status=404)

    try:
        is_correct = answer.toggle_correct()
    except IntegrityError:
        return JsonResponse({'error': 'Конфликт при сохранении'}, status=409)

    return JsonResponse({'is_correct': is_correct, 'answer_id': answer.id})

def _vote(request, model, object_id, vote_type):
    if request.method != 'POST':
        return JsonResponse({'error': 'Нужен POST-запрос'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Нужна авторизация', 'login_url': reverse('login')}, status=401)

    form = VoteForm({'vote_type': vote_type})
    if not form.is_valid():
        return JsonResponse({'error': 'Неверный тип голоса'}, status=400)

    item = model.objects.filter(id=object_id).first()
    if not item:
        return JsonResponse({'error': 'Объект не найден'}, status=404)

    try:
        rating, vote_state = item.toggle_vote(request.user.profile, form.cleaned_data['vote_type'])
    except IntegrityError:
        return JsonResponse({'error': 'Конфликт при сохранении'}, status=409)

    return JsonResponse({'rating': rating, 'vote_state': vote_state})



def vote_question(request, question_id, vote_type):
    return _vote(request, Question, question_id, vote_type)



def vote_answer(request, answer_id, vote_type):
    return _vote(request, Answer, answer_id, vote_type)

