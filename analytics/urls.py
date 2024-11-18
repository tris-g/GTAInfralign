from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('projects', views.projects, name='projects'),
    path('projects/new', views.add_project, name='add_project'),
    path('projects/<int:pk>', views.project, name='project'),
    path('projects/<int:project_pk>/delete', views.delete_project, name='delete-project'),
]