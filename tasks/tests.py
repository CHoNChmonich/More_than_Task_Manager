from django.test import TestCase
from django.urls import reverse
from users.models import User
from tasks.models import Task
from tasks.forms import TaskForm
from django.utils import timezone

class TaskCreateViewTests(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.url = reverse(
            'tasks:task_create')  # Замените 'tasks:task_create' на вашу именованную ссылку для создания задачи

    def test_access_denied_for_anonymous(self):
        """Проверка: анонимный пользователь не имеет доступа."""
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f'/users/login/?next={self.url}')  # Проверьте ваш URL для логина

    def test_access_granted_for_authenticated_user(self):
        """Проверка: авторизованный пользователь имеет доступ."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tasks/task_change.html')

    def test_context_data(self):
        """Проверка: в контексте передается заголовок."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['title'], 'Создание задачи')

    def test_task_creation(self):
        """Проверка: задача создается и связывается с текущим пользователем."""
        self.client.login(username='testuser', password='password123')
        form_data = {
            'title': 'Test Task',
            'description': 'Test description',
            'due_date': '2025-06-06',
            'status': 1,
            'priority': 1,
            # Добавьте другие поля формы, если нужно
        }
        response = self.client.post(self.url, form_data)

        # Проверяем редирект
        self.assertRedirects(response,
                             reverse('tasks:task_list'))  # Замените 'tasks:task_list' на вашу ссылку списка задач

        # Проверяем, что задача создана
        task = Task.objects.get(title='Test Task')
        self.assertEqual(task.creator, self.user)
        self.assertEqual(task.description, 'Test description')
        self.assertEqual(task.status, 1)
        self.assertEqual(task.priority, 1)

    def test_invalid_form_submission(self):
        """Проверка: некорректные данные не создают задачу."""
        self.client.login(username='testuser', password='password123')
        form_data = {
            'title': '',  # Оставляем обязательное поле пустым
            'description': 'Test description',
        }
        response = self.client.post(self.url, form_data)

        # Проверяем, что статус ответа - 200 (форма должна быть показана с ошибками)
        self.assertEqual(response.status_code, 200)

        # Проверяем, что форма содержит ошибку на поле 'title'
        form = response.context.get('form')  # Достаём форму из контекста ответа
        self.assertIsNotNone(form, "Форма должна быть в контексте ответа.")
        self.assertTrue(form.errors, "Ожидается наличие ошибок в форме.")
        self.assertIn('title', form.errors, "Ошибка должна быть связана с полем 'title'.")
        self.assertEqual(form.errors['title'], ['This field is required.'])  # Замените текст ошибки, если он другой

        # Убедимся, что задача не создана
        self.assertEqual(Task.objects.count(), 0)


class EditTaskViewTests(TestCase):

    def setUp(self):
        """
        Устанавливаем начальные данные для тестов.
        """
        # Создаем пользователей
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')

        # Создаем задачу для пользователя user1
        self.task = Task.objects.create(
            title="Test Task",
            description="Task description",
            due_date=timezone.now() + timezone.timedelta(days=1),
            creator=self.user1
        )

    def test_edit_task_get(self):
        """
        Проверяем, что редактирование задачи происходит только если пользователь является создателем.
        """
        # Входим как user1
        self.client.login(username='user1', password='password')

        url = reverse('tasks:edit_task', kwargs={'task_id': self.task.id})
        response = self.client.get(url)

        # Проверяем, что форма для редактирования задачи отображается
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Редактирование задачи')
        self.assertContains(response, 'value="Test Task"')

    def test_edit_task_access_denied(self):
        """
        Проверяем, что пользователь не может редактировать чужую задачу.
        """
        # Входим как user2
        self.client.login(username='user2', password='password')

        url = reverse('tasks:edit_task', kwargs={'task_id': self.task.id})
        response = self.client.get(url)

        # Проверяем, что редирект на список задач
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tasks:task_list'))

    def test_edit_task_not_found(self):
        """
        Проверяем, что если задача не найдена, то редирект на список задач.
        """
        # Входим как user1
        self.client.login(username='user1', password='password')

        # Попытка редактировать задачу, которая не существует
        url = reverse('tasks:edit_task', kwargs={'task_id': 9999})
        response = self.client.get(url)

        # Проверяем редирект на список задач
        self.assertEqual(response.status_code, 404)
        self.assertRedirects(response, reverse('tasks:task_list'))

    def test_edit_task_post(self):
        """
        Проверяем успешное редактирование задачи.
        """
        # Входим как user1
        self.client.login(username='user1', password='password')

        url = reverse('tasks:edit_task', kwargs={'task_id': self.task.id})

        # Отправляем обновленные данные
        data = {
            'title': 'Updated Test Task',
            'description': 'Updated description',
            'due_date': timezone.now() + timezone.timedelta(days=2),
        }

        response = self.client.post(url, data)

        # Проверяем редирект после успешного сохранения
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('tasks:task_list'))

        # Проверяем, что задача была обновлена
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Test Task')
        self.assertEqual(self.task.description, 'Updated description')

    def test_invalid_form_submission(self):
        """
        Проверяем обработку некорректных данных формы.
        """
        # Входим как user1
        self.client.login(username='user1', password='password')

        url = reverse('tasks:edit_task', kwargs={'task_id': self.task.id})

        # Отправляем некорректные данные
        data = {
            'title': '',  # Пустое название, что является ошибкой
            'description': 'Updated description',
            'due_date': timezone.now() + timezone.timedelta(days=2),
        }

        response = self.client.post(url, data)

        # Проверяем, что форма возвращает ошибку
        self.assertFormError(response, 'form', 'title', 'Это поле обязательно.')




