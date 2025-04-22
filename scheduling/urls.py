

from django.urls import path
from .views import index, process_scheduling

urlpatterns = [
    path('', index, name='index'),
    path('process/', process_scheduling, name='process_scheduling'),
]