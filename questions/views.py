from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

QUESTIONS=[
    {
        'id':i,
        'title':f'How to build a moon park #{i}',
        'text': f'Lorem ipsum dolor sit amet, consectetuer adipiscing elit asfadfadsfjhaewfheiufhyiasdhfehiufhaseuifhilseuahflskaehufli7esufhakdjshflieuafsfhliuesaf. Question text number {i}.',
        'answer_count':i*2,
        'rating':i*3,
        'tags':['black-jack', 'bender', 'python'],
    }
    for i in range(0,30)
]

ANSWERS = [
    {
        'id': i,
        'text': f'First of all I would like to thank you for the invitation ({i}). Russia is a huge territory.',
        'rating': 5 if i == 1 else 2,
        'is_correct': (i == 1),
    }
    for i in range(1, 15)
]

def paginate(objects_list,request,per_page=10):
    paginator=Paginator(objects_list,per_page)
    page_number=request.GET.get('page',1)
    try:
        page=paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page

def index(request):
    page=paginate(QUESTIONS,request,per_page=4)
    return render(request,'questions/index.html',{'page_obj':page})

def hot(request):
    hot_questions = sorted(QUESTIONS, key=lambda q: q['rating'], reverse=True)
    page = paginate(hot_questions, request, per_page=5)
    return render(request, 'questions/hot.html', {'page_obj': page})

def tag(request, tag_name):
    tagged_questions = [q for q in QUESTIONS if tag_name in q['tags']] or QUESTIONS
    page = paginate(tagged_questions, request, per_page=5)
    return render(request, 'questions/tag.html', {'page_obj': page, 'tag_name': tag_name})

def question(request, question_id):
    item = next((q for q in QUESTIONS if q['id'] == question_id), QUESTIONS[0])
    page = paginate(ANSWERS, request, per_page=5)
    return render(request, 'questions/question.html', {'question': item, 'page_obj': page})

def ask(request):
    return render(request, 'questions/ask.html')