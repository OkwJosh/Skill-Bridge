import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Category
from django.utils.text import slugify

categories = [
    {"name": "Design", "icon": "🎨"},
    {"name": "Engineering", "icon": "💻"},
    {"name": "Marketing", "icon": "📈"},
    {"name": "Product", "icon": "📦"},
    {"name": "Data", "icon": "📊"},
    {"name": "Sales", "icon": "🤝"},
]

for cat in categories:
    Category.objects.get_or_create(
        name=cat['name'],
        defaults={
            'slug': slugify(cat['name']),
            'icon': cat['icon']
        }
    )

print("Categories seeded successfully!")
