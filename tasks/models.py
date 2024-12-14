from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        (2, 'Новое'),
        (1, 'В процессе'),
        (0, 'Завершено'),
    ]

    PRIORITY_CHOICES = [
        (0, 'Низкий'),
        (1, 'Средний'),
        (2, 'Высокий'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.PositiveIntegerField(choices=STATUS_CHOICES, default=2)
    priority = models.PositiveIntegerField(choices=PRIORITY_CHOICES, default=0)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assignees = models.ManyToManyField(User, related_name='tasks', blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    tags = models.ManyToManyField(Tag, related_name='tasks', blank=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def get_priority_display(self):
        return dict(self.PRIORITY_CHOICES).get(self.priority, 'Неизвестно')


class TaskAnswer(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='answers')  # Связь с задачей
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')  # Связь с пользователем
    comment = models.TextField(blank=True, null=True)  # Комментарий
    file = models.FileField(upload_to='media/task_answers/', blank=True, null=True)  # Файл, связанный с ответом
    created_at = models.DateTimeField(auto_now_add=True)  # Дата и время ответа

    def __str__(self):
        return f"Ответ на задачу {self.task.title} от {self.user.username} ({self.user.first_name} {self.user.last_name})"


class AnswerComment(models.Model):
    answer = models.ForeignKey(TaskAnswer, on_delete=models.CASCADE, related_name='comments')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Комментарий от {self.manager.get_full_name()} к ответу на '{self.answer.task.title}'"
