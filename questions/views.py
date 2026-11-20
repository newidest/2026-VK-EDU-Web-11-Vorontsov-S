from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.views.decorators.http import require_POST
from questions.forms import AnswerForm,AskForm
from .models import Question, Answer, Tag
from core.models import Profile
from django.views.decorators.csrf import ensure_csrf_cookie


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


@ensure_csrf_cookie
def question(request, question_id):
    item = get_object_or_404(Question.objects.with_details(), pk=question_id)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect(f"{reverse('login')}?next={request.path}")
        form = AnswerForm(request.POST)
        if form.is_valid():
            form.save(author=request.user.profile, question=item)
            return HttpResponseRedirect(reverse('question', args=[item.id]))
    else:
        form = AnswerForm()

    is_question_author = (
        request.user.is_authenticated
        and hasattr(request.user, 'profile')
        and item.user_id == request.user.profile.id
    )

    item.answer_count = item.answers.count()
    return render_page(
        request,
        'questions/question.html',
        Answer.objects.for_question(item),
        per_page=5,
        extra_context={
            'question': item,
            'form': form,
            'is_question_author': is_question_author,
        },
    )

def ask(request):
    if request.method=='POST':
        form=AskForm(request.POST)
        if form.is_valid():
            new_question=form.save(author=request.user.profile)
            return HttpResponseRedirect(reverse('question',args=[new_question.id]))
    else:
        form=AskForm()
    return render_page(request, 'questions/ask.html',extra_context={'form':form})

@login_required(login_url='/login')
@require_POST
def mark_correct_answer(request,question_id,answer_id):
    question = get_object_or_404(Question, id=question_id)

    if question.user != request.user.profile:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    answer = get_object_or_404(Answer, id=answer_id, question=question)
    answer.is_correct = not answer.is_correct
    answer.save(update_fields=['is_correct'])

    return JsonResponse({'is_correct': answer.is_correct})

from django.db.models import Sum
from .models import Question, Answer, QuestionLike, AnswerLike


def _toggle_vote(like_model, target_field, target_obj, profile, vote_type):
    if vote_type not in ('like', 'dislike'):
        return None, None

    value = 1 if vote_type == 'like' else -1
    vote, created = like_model.objects.get_or_create(
        user=profile,
        **{target_field: target_obj},
        defaults={'like': value},
    )

    if not created:
        if vote.like == value:
            vote.delete()
            vote_state = None
        else:
            vote.like = value
            vote.save(update_fields=['like'])
            vote_state = vote_type
    else:
        vote_state = vote_type

    rating = (
        like_model.objects.filter(**{target_field: target_obj})
        .aggregate(total=Sum('like'))['total']
        or 0
    )
    target_obj.rating = rating
    target_obj.save(update_fields=['rating'])

    return rating, vote_state


@require_POST
def vote_question(request, question_id, vote_type):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    item = get_object_or_404(Question, id=question_id)
    rating, vote_state = _toggle_vote(
        QuestionLike, 'question', item, request.user.profile, vote_type
    )
    if rating is None:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)

    return JsonResponse({'rating': rating, 'vote_state': vote_state})


@require_POST
def vote_answer(request, answer_id, vote_type):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    item = get_object_or_404(Answer, id=answer_id)
    rating, vote_state = _toggle_vote(
        AnswerLike, 'answer', item, request.user.profile, vote_type
    )
    if rating is None:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)

    return JsonResponse({'rating': rating, 'vote_state': vote_state})

