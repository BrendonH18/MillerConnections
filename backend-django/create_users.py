import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

def create_user(email, password, first_name, last_name, groups):
    user, created = User.objects.get_or_create(email=email, first_name=first_name, last_name=last_name)
    if created:
        user.set_password(password)
        user.save()
        print(f'User {email} created.')
    else:
        print(f'User {email} already exists.')

    for group_name in groups:
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
        print(f'User {email} added to group {group_name}.')
    user.save()

if __name__ == '__main__':
    # Create users
    users_data = [
        {'email': 'field_user@example.com', 'password': 'password123', 'first_name': 'Field', 'last_name': 'User', 'groups': ['Field']},
        {'email': 'phone_user@example.com', 'password': 'password123', 'first_name': 'Phone', 'last_name': 'User', 'groups': ['Phone']},
        {'email': 'internal_manager@example.com', 'password': 'password123', 'first_name': 'Internal', 'last_name': 'Manager', 'groups': ['Internal Manager', 'Phone']},
        {'email': 'external_manager@example.com', 'password': 'password123', 'first_name': 'External', 'last_name': 'Manager', 'groups': ['External Manager', 'Field']},
    ]

    for user_data in users_data:
        create_user(**user_data)