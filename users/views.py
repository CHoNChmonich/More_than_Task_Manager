from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages, auth
from django.urls import reverse
from django.views import View
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from tasks.models import Task
from users.forms import ProfileUpdateForm, UserRegistrationForm


# Create your views here.
class UserLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True  # Перенаправление уже аутентифицированных пользователей
    next_page = reverse_lazy('users:profile')  # Перенаправление после успешного входа

    def form_invalid(self, form):
        """
        Обрабатывает случай, когда форма некорректна.
        Добавляет сообщение об ошибке.
        """
        messages.error(self.request, 'Неверное имя пользователя или пароль.')
        return super().form_invalid(form)

    def form_valid(self, form):
        """
        Добавляет сообщение об успешном входе.
        """
        messages.success(self.request, 'Вы успешно вошли в систему!')
        return super().form_valid(form)


class UserRegisterView(View):
    template_name = 'users/register.html'

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET-запрос для отображения формы регистрации."""
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос для регистрации нового пользователя."""
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Создание пользователя
            login(request, user)  # Авторизация пользователя
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('users:profile')  # Перенаправление в личный кабинет
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'users/profile.html'

    def get(self, request, *args, **kwargs):
        """Обрабатывает GET-запрос для отображения профиля пользователя."""
        user_form = ProfileUpdateForm(instance=request.user)
        tasks = self.get_user_tasks(request.user)
        context = {
            'title': 'Личный кабинет',
            'form': user_form,
            'tasks': tasks,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос для обновления профиля пользователя."""
        user_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect('users:profile')
        tasks = self.get_user_tasks(request.user)
        context = {
            'title': 'Личный кабинет',
            'form': user_form,
            'tasks': tasks,
        }
        return render(request, self.template_name, context)

    def get_user_tasks(self, user):
        """Получает задачи, связанные с пользователем."""
        return Task.objects.filter(creator=user) | Task.objects.filter(assignees=user)


@login_required
def logout(request):
    messages.success(request, f'{request.user.username}, Вы вышли из аккаунта')
    auth.logout(request)
    return redirect(reverse('main:index'))
