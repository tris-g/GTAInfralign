from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects', views.view_all_projects, name='view_all_projects'),
    path('projects/new', views.add_project, name='add_project'),
    path('projects/<int:project_pk>', views.view_project, name='view_project'),
    path('projects/<int:project_pk>/update', views.update_project, name='update_project'),
    path('projects/<int:project_pk>/delete', views.delete_project, name='delete_project'),
    path('reports', views.view_all_reports, name='view_all_reports'),
    path('reports/new', views.add_report, name='add_report'),
    path('reports/<int:report_pk>/update', views.update_report, name='update_report'),
    path('reports/<int:report_pk>/delete', views.delete_report, name='delete_report'),
    path('data/report/<int:report_pk>', views.report_data, name='report_data'),
    path('data/dash', views.dash_data, name='dash_data'),
]