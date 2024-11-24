from django.contrib.auth import get_user_model
import os

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'root')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'root')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser {username} created successfully.")
else:
    print(f"Superuser {username} already exists.")
