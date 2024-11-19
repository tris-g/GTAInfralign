from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects', views.view_all_projects, name='view_all_projects'),
    path('projects/new', views.add_project, name='add_project'),
    path('projects/<int:project_pk>', views.view_project, name='view_project'),
    path('projects/<int:project_pk>/delete', views.delete_project, name='delete_project'),
]