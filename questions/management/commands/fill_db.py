import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker

from core.models import Profile
from questions.models import Tag, Question, Answer, QuestionLike, AnswerLike


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        ratio = options['ratio']
        fake = Faker('ru_RU')

        u_offset = User.objects.count()
        t_offset = Tag.objects.count()

        names_pool = [fake.user_name() for _ in range(1000)]
        words_pool = [fake.word() for _ in range(1000)]
        titles_pool = [fake.sentence(nb_words=random.randint(4, 8))[:128] for _ in range(1000)]
        texts_pool = [fake.text(max_nb_chars=250) for _ in range(1000)]

        users = [
            User(username=f'{random.choice(names_pool)}_{u_offset + i}', password='password123')
            for i in range(ratio)
        ]
        User.objects.bulk_create(users, batch_size=5000)

        profiles = [
            Profile(user=u, nickname=u.username)
            for u in users
        ]
        Profile.objects.bulk_create(profiles, batch_size=5000)

        tags = [
            Tag(name=f'{random.choice(words_pool)}_{t_offset + i}'[:32])
            for i in range(ratio)
        ]
        Tag.objects.bulk_create(tags, batch_size=5000)

        questions = [
            Question(
                user=random.choice(profiles),
                title=random.choice(titles_pool),
                content=random.choice(texts_pool),
                rating=random.randint(0, 100),
            )
            for _ in range(ratio * 10)
        ]
        Question.objects.bulk_create(questions, batch_size=5000)

        ThroughModel = Question.tags.through
        question_tags = []
        for q in questions:
            for t in random.sample(tags, k=min(2, len(tags))):
                question_tags.append(ThroughModel(question_id=q.id, tag_id=t.id))
        ThroughModel.objects.bulk_create(question_tags, batch_size=5000, ignore_conflicts=True)

        answers = [
            Answer(
                question=random.choice(questions),
                user=random.choice(profiles),
                content=random.choice(texts_pool),
                rating=random.randint(0, 50),
            )
            for _ in range(ratio * 100)
        ]
        Answer.objects.bulk_create(answers, batch_size=5000)

        q_likes = [
            QuestionLike(
                user=random.choice(profiles),
                question=random.choice(questions),
                like=random.choice([-1, 1]),
            )
            for _ in range(ratio * 200)
        ]
        QuestionLike.objects.bulk_create(q_likes, batch_size=5000, ignore_conflicts=True)

        a_likes = [
            AnswerLike(
                user=random.choice(profiles),
                answer=random.choice(answers),
                like=random.choice([-1, 1]),
            )
            for _ in range(ratio * 200)
        ]
        AnswerLike.objects.bulk_create(a_likes, batch_size=5000, ignore_conflicts=True)