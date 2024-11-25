from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects', views.view_all_projects, name='view_all_projects'),
    path('projects/new', views.add_project, name='add_project'),
    path('projects/<int:project_pk>', views.view_project, name='view_project'),
    path('projects/<int:project_pk>/delete', views.delete_project, name='delete_project'),
    path('reports', views.view_all_reports, name='view_all_reports'),
    path('reports/new', views.add_report, name='add_report'),
    path('reports/<int:report_pk>/delete', views.delete_report, name='delete_report'),
    path('reports/data/<int:report_pk>', views.report_data, name='report_data'),
]