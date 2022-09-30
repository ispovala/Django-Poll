from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """

        return Question.objects.filter(pk__in=[x.question.pk for x in Choice.objects.all()],
                                       pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


#     def get_queryset(self):
#         """
#         Return the last five published questions (not including those set to be
#         published in the future).
#         """
#
#         cursor = connection.cursor()
#         sql = """SELECT DISTINCT `polls_question`.`id`, `polls_question`.`question_text`, `polls_question`.`pub_date`
# FROM `polls_question`
# INNER JOIN `polls_choice`
# ON `polls_question`.`id`=`polls_choice`.`question_id`
# WHERE `polls_question`.`pub_date` <= STR_TO_DATE("2022-09-29 09:13:51", "%Y-%m-%d %H:%i:%s")
# ORDER BY `polls_question`.`pub_date` DESC LIMIT 5;"""
#
#         cursor.execute(sql)
#         dic = []
#         detalles = cursor.fetchall()
#         print(detalles)
#         for row in detalles:
#             diccionario = dict(zip([col[0] for col in cursor.description], row))
#             print(cursor.description)
#             dic.append(diccionario)
#         cursor.close()
#         print(dic)
#         return dic


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_context_data(self, **kwargs):
        match = 0
        context = super(DetailView, self).get_context_data(**kwargs)
        for q in Question.objects.filter(pk__in=[x.question.pk for x in Choice.objects.all()]):
            if q.pk == self.kwargs['pk']:
                match += 1
        if match == 0:
            context['error_message'] = "ERROR: This question has no choices, you can't vote"
        return context


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
# Create your views here.
