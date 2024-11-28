from django.urls import path
from tasks.views import TaskListView, TaskDetailView, CreateOrEditTaskView, DeleteTaskView, TaskCreateView, \
    AddAnswerView, SubordinatesTasksView, AddCommentView

app_name = 'tasks'

urlpatterns = [
    path('search_task_list/', TaskListView.as_view(), name='search_task_list'),
    path('task_create/', TaskCreateView.as_view(), name='task_create'),
    path('edit/<int:task_id>/', CreateOrEditTaskView.as_view(), name='edit_task'),
    path('task_list/', TaskListView.as_view(), name='task_list'),
    path('task_detail/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('task/answer/<int:task_id>/', AddAnswerView.as_view(), name='add_answer'),
    path('task_answer/add_comment/<int:task_answer_id>/', AddCommentView.as_view(), name='add_comment'),
    path('delete/<int:task_id>/', DeleteTaskView.as_view(), name='delete_task'),
    path('subordinate/tasks/<int:subordinate_id>/', SubordinatesTasksView.as_view(), name='subordinate_tasks'),
]
