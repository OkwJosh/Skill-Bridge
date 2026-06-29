from django.urls import path

from .views import IndustryListView, SkillListCreateView, UploadSignView, CategoryListView


app_name = 'core'

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('skills/', SkillListCreateView.as_view(), name='skills'),
    path('industries/', IndustryListView.as_view(), name='industries'),
    path('uploads/sign/', UploadSignView.as_view(), name='upload-sign'),
]
