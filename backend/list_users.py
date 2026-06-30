
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

print(f'{"Email":<40} | {"Full Name":<20} | {"Role":<15} | {"Password"}\n' + '-'*100)
for user in User.objects.all():
    role = 'Talent' if getattr(user, 'is_talent', False) else 'Org Admin' if getattr(user, 'is_org_admin', False) else 'Superuser' if user.is_superuser else 'Other'
    name = (user.full_name or '')[:19]
    pwd = (user.password or '')[:20]
    print(f'{user.email:<40} | {name:<20} | {role:<15} | [Hashed: {pwd}...]')

