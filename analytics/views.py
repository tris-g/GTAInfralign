import logging, json

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.postgres.search import SearchVector
from django.http import JsonResponse
from django.contrib import messages

from .models import AutodeskConstructionCloudProject, AutodeskConstructionCloudReport
from .forms import AutodeskConstructionCloudProjectForm, AutodeskConstructionCloudReportForm

from .utils import json_from_excel

logger = logging.getLogger(__name__)

def verbose_user(request) -> str:
    """Returns a unique string representing the user within the request. Meant for logging purposes."""
    return f"{request.user.pk}:{request.user.username}"

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'username': request.user.username})

@login_required
def view_all_projects(request):
    if not request.user.has_perm('analytics.view_autodeskconstructioncloudproject'):
        raise PermissionDenied
    if request.GET.get('search'):
        p = AutodeskConstructionCloudProject.objects.annotate(search=SearchVector('name', 'org'),).filter(search=request.GET.get('search'))
    else:
        p = AutodeskConstructionCloudProject.objects.all()
    return render(request, 'view_all_projects.html', {'projects_list': p})

@login_required
def view_project(request, project_pk):
    if not request.user.has_perm('analytics.view_autodeskconstructioncloudproject'):
        raise PermissionDenied
    try:
        if request.GET.get('report'):
            report = AutodeskConstructionCloudReport.objects.get(pk=request.GET.get('report'), project=project_pk)
        else:
            report = AutodeskConstructionCloudReport.objects.filter(project=project_pk).latest('uploaded_at')
    except ObjectDoesNotExist:
        messages.error(request, f"No reports to show.")
        return redirect('view_all_projects')
    other_reports = [r for r in AutodeskConstructionCloudReport.objects.filter(project=project_pk) if r.pk != report.pk]
    return render(request, 'view_project.html', {'project': AutodeskConstructionCloudProject.objects.get(pk=project_pk), 'reports': other_reports, 'report': report})

@login_required
def add_project(request):
    if not request.user.has_perm('analytics.add_autodeskconstructioncloudproject'):
        raise PermissionDenied
    if request.method == "POST":
        form = AutodeskConstructionCloudProjectForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sucessfully created project.")
            return redirect('view_all_projects')
        else:
            messages.error(request, "Incorrect form.")
    else:
        form = AutodeskConstructionCloudProjectForm()
    return render(request, "add_project.html", {"form": form})

@login_required
def delete_project(request, project_pk):
    if not request.user.has_perm('analytics.delete_autodeskconstructioncloudproject'):
        raise PermissionDenied
    project = AutodeskConstructionCloudProject.objects.get(pk=project_pk)
    project.delete()
    logger.info(f"{verbose_user(request)} sucessfully deleted {project.pk}:{project.name}.")
    messages.success(request, f"{project.name} was deleted successfully.")
    return redirect('view_all_projects')

@login_required
def view_all_reports(request):
    if not request.user.has_perm('analytics.view_autodeskconstructioncloudreport'):
        raise PermissionDenied
    r = AutodeskConstructionCloudReport.objects.all()
    return render(request, 'view_all_reports.html', {'reports_list': r})

@login_required
def add_report(request):
    if not request.user.has_perm('analytics.add_autodeskconstructioncloudreport'):
        raise PermissionDenied
    if request.method == "POST":
        updated_request = request.POST.copy()
        if request.FILES.get('excel_report'):
            updated_request.update({'data': [json_from_excel(request.FILES.get('excel_report'))]})
        form = AutodeskConstructionCloudReportForm(data=updated_request)
        if form.is_valid():
            form.save()
            messages.success(request, "Sucessfully created report.")
            return redirect('view_all_reports')
        else:
            messages.error(request, "Incorrect form.")
    else:
        form = AutodeskConstructionCloudReportForm()
    return render(request, "add_report.html", {"form": form, 'projects_list': AutodeskConstructionCloudProject.objects.all()})

@login_required
def report_data(request, report_pk):
    if not request.user.has_perm('analytics.view_autodeskconstructioncloudreport'):
        raise PermissionDenied
    return JsonResponse(AutodeskConstructionCloudReport.objects.get(pk=report_pk).data[0])

@login_required
def delete_report(request, report_pk):
    if not request.user.has_perm('analytics.delete_autodeskconstructioncloudreport'):
        raise PermissionDenied
    rep = AutodeskConstructionCloudReport.objects.get(pk=report_pk)
    rep.delete()
    logger.info(f"{verbose_user(request)} sucessfully deleted {rep.pk}:{rep.name}.")
    messages.success(request, f"Report {rep.name} was deleted successfully.")
    return redirect('view_all_reports')