from tasks.models import Task, Tag, TaskAnswer, AnswerComment
from users.models import User
from tasks.utils import q_search
from .forms import TaskForm, AnswerCommentForm, TaskAnswerForm

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_change.html'

    def form_valid(self, form):
        """
        Метод, который вызывается при успешной валидации формы.
        Здесь мы сохраняем задачу и связываем ее с текущим пользователем.
        """
        task = form.save(commit=False)
        task.creator = self.request.user  # Устанавливаем текущего пользователя как создателя задачи
        task.save()
        form.save_m2m()  # Сохраняем ManyToMany связь для полей 'assignees' и 'tags'
        return redirect('tasks:task_list')  # Перенаправляем на список задач

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание задачи'
        return context


class EditTaskView(LoginRequiredMixin, FormView):
    template_name = 'tasks/task_change.html'
    form_class = TaskForm
    success_url = reverse_lazy('tasks:task_list')

    def get_task(self):
        """
        Получает задачу по `task_id`, если она существует.
        """
        task_id = self.kwargs.get('task_id')
        if task_id:
            task = get_object_or_404(Task, id=task_id)
            if task.creator != self.request.user:
                return None  # Возвращаем None, если пользователь не создатель
            return task
        return None

    def get_form_kwargs(self):
        """
        Добавляем текущую задачу (для редактирования) в форму.
        """
        kwargs = super().get_form_kwargs()
        task = self.get_task()
        if task:
            kwargs['instance'] = task
        return kwargs

    def form_valid(self, form):
        """
        Сохраняет редактируемую задачу.
        """
        task = form.save(commit=False)
        task.save()  # Обновляем существующую задачу
        form.save_m2m()  # Сохраняем связи ManyToMany
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Передаем дополнительный контекст в шаблон.
        """
        context = super().get_context_data(**kwargs)
        task = self.get_task()
        context['title'] = 'Редактирование задачи'
        context['form'] = self.get_form()
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяет, есть ли доступ к редактируемой задаче.
        """
        task = self.get_task()
        if self.kwargs.get('task_id') and not task:
            return redirect('tasks:task_list')
        return super().dispatch(request, *args, **kwargs)



class DeleteTaskView(View):
    """
    Представление для удаления задачи.
    Проверяет, является ли текущий пользователь создателем задачи, и если да, то удаляет задачу.
    """

    def post(self, request, task_id):
        """
        Обработка POST-запроса для удаления задачи.
        """
        task = get_object_or_404(Task, id=task_id)

        # Проверяем, является ли текущий пользователь создателем задачи
        if task.creator != request.user:
            messages.error(request, "У вас нет прав на удаление этой задачи.")
            return redirect('tasks:task_list')

        # Если пользователь является создателем задачи, удаляем задачу
        task.delete()

        # Сообщаем об успешном удалении
        messages.success(request, "Задача успешно удалена.")
        return redirect('tasks:task_list')


class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        """
        Получает задачи для отображения, включая фильтры по тегам, статусу,
        приоритету, подчинённым и текстовому поиску.
        """
        query = self.request.GET.get('q', None)
        user = self.request.user
        tasks = q_search(query) if query else Task.objects.all()

        # Ограничиваем задачи только для текущего пользователя (созданные или назначенные)
        tasks = tasks.filter(Q(creator=user) | Q(assignees=user)).distinct()

        # Получаем фильтры из запроса
        selected_tags = self.request.GET.getlist('tags')
        selected_status = self.request.GET.get('status')
        selected_priority = self.request.GET.get('priority')
        selected_assignees = self.request.GET.getlist('assignees')

        # Применяем фильтры
        if selected_tags:
            tasks = tasks.filter(tags__id__in=selected_tags).distinct()
        if selected_status:
            tasks = tasks.filter(status=selected_status)
        if selected_priority:
            tasks = tasks.filter(priority=selected_priority)
        if selected_assignees:
            tasks = tasks.filter(assignees__id__in=selected_assignees).distinct()

        return tasks.order_by('due_date')

    def get_context_data(self, **kwargs):
        """
        Добавляем дополнительный контекст в шаблон, включая фильтры и их значения.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Передаём данные для фильтров в контекст
        context.update({
            'title': 'Ваши задачи',
            'tags': Tag.objects.all(),
            'statuses': Task.STATUS_CHOICES,
            'priorities': Task.PRIORITY_CHOICES,
            'assignees': user.subordinates.all(),
            'selected_tags': [int(tag) for tag in self.request.GET.getlist('tags')],
            'selected_status': int(self.request.GET.get('status')) if self.request.GET.get('status') else None,
            'selected_priority': int(self.request.GET.get('priority')) if self.request.GET.get('priority') else None,
            'selected_assignees': [int(assignee) for assignee in self.request.GET.getlist('assignees')],
        })

        return context


class TaskDetailView(DetailView):
    """
    Класс представления для отображения подробной информации о задаче.
    """
    model = Task
    template_name = 'tasks/task_detail.html'  # Указываем шаблон для отображения
    context_object_name = 'task'  # Имя переменной для объекта в контексте

    def get_context_data(self, **kwargs):
        """
        Метод для добавления данных в контекст.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = f'Задача: {context["task"].title}'  # Устанавливаем title с названием задачи
        return context


class AddAnswerView(LoginRequiredMixin, CreateView):
    model = TaskAnswer
    form_class = TaskAnswerForm
    template_name = 'tasks/task_answer.html'

    def dispatch(self, request, *args, **kwargs):
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)

        # Проверка, что пользователь является либо исполнителем, либо создателем задачи
        if request.user != task.creator and request.user not in task.assignees.all():
            return redirect('tasks:task_list')  # Если пользователь не связан с задачей, перенаправляем

        self.task = task  # Сохраняем задачу для использования в других методах
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.task = self.task  # Присваиваем задачу
        form.instance.user = self.request.user  # Присваиваем текущего пользователя как создателя ответа
        response = super().form_valid(form)  # Сохраняем ответ
        return redirect('tasks:task_detail', pk=self.task.id)  # Перенаправляем на страницу задачи

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = self.task  # Добавляем задачу в контекст
        return context

    def get_success_url(self):
        # Указываем перенаправление на детальную страницу задачи
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.task.id})


class AddCommentView(LoginRequiredMixin, CreateView):
    model = AnswerComment
    form_class = AnswerCommentForm
    template_name = 'tasks/add_comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.task_answer = get_object_or_404(TaskAnswer, id=self.kwargs['task_answer_id'])

        # Проверяем, что автор комментария является руководителем исполнителя
        if not request.user.subordinates.filter(id=self.task_answer.user.id).exists():
            return redirect('tasks:task_detail', pk=self.task_answer.task.id)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.answer = self.task_answer  # Привязываем комментарий к ответу
        form.instance.manager = self.request.user  # Указываем текущего пользователя как автора комментария
        return super().form_valid(form)

    def get_success_url(self):
        # Перенаправляем на детальную страницу задачи
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.task_answer.task.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_answer'] = self.task_answer  # Передаем ответ в контекст
        return context


@method_decorator(login_required, name='dispatch')
class SubordinatesTasksView(ListView):
    model = Task
    template_name = 'tasks/subordinate_tasks.html'
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        subordinate_id = self.kwargs['subordinate_id']
        subordinate = get_object_or_404(User, id=subordinate_id)

        # Получаем все задачи, назначенные подчиненному
        tasks = Task.objects.filter(assignees=subordinate).distinct()

        # Собираем список задач с ответами
        tasks_with_answers = []
        for task in tasks:
            answer = TaskAnswer.objects.filter(task=task, user=subordinate).first()
            tasks_with_answers.append({'task': task, 'answer': answer})

        context['subordinate'] = subordinate
        context['tasks_with_answers'] = tasks_with_answers
        return context
