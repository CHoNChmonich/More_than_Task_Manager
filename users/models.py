from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Новое поле для изображения пользователя
    profile_image = models.ImageField(
        upload_to='media/profile_images/',  # Папка, куда будут загружаться изображения
        null=True,
        blank=True,
        default='profile_images/default.png'  # Укажите путь к изображению по умолчанию
    )
    subordinates = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        null=True,
        related_name='superiors'
    )

    def __str__(self):
        return self.username
