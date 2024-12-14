from django import forms

from .models import Task, TaskAnswer, AnswerComment, Tag


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'status', 'priority', 'assignees',
                  'tags']  # Добавляем 'tags' к полям формы

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if current_user:
            # Ограничиваем список доступных исполнителей только подчиненными текущего пользователя
            self.fields['assignees'].queryset = current_user.subordinates.all()

        # Устанавливаем queryset для тегов (если это необходимо)
        self.fields['tags'].queryset = Tag.objects.all()  # Здесь можно настроить ограничения, если нужно


class TaskAnswerForm(forms.ModelForm):
    class Meta:
        model = TaskAnswer
        fields = ['comment', 'file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AnswerCommentForm(forms.ModelForm):
    class Meta:
        model = AnswerComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Оставьте комментарий', 'rows': 3}),
        }
