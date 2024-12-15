import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.postgres.search import SearchVector
from django.http import JsonResponse
from django.contrib import messages

from .models import AutodeskConstructionCloudProject, AutodeskConstructionCloudReport
from .forms import AutodeskConstructionCloudProjectForm, AutodeskConstructionCloudReportForm

from .wrappers import permission_required
from .utils import verbose_user, json_from_excel

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'username': request.user.username})

@login_required
@permission_required('analytics.view_autodeskconstructioncloudproject', 'dashboard')
def view_all_projects(request):
    if request.GET.get('search'):
        p = AutodeskConstructionCloudProject.objects.annotate(search=SearchVector('name', 'org'),).filter(search=request.GET.get('search'))
    else:
        p = AutodeskConstructionCloudProject.objects.all()
    return render(request, 'view_all_projects.html', {'projects_list': p})

@login_required
@permission_required('analytics.view_autodeskconstructioncloudproject', 'dashboard')
def view_project(request, project_pk):
    report_pk = request.GET.get('report')
    if request.GET.get('report'):
        report = get_object_or_404(AutodeskConstructionCloudProject, pk=report_pk)
    else:
        try:
            report = AutodeskConstructionCloudReport.objects.filter(project=project_pk).latest('uploaded_at')
        except ObjectDoesNotExist:
            logger.debug(f'No reports found for {project_pk}.')
            messages.warning(request, "No reports to show.")
            return redirect('view_all_projects')
    return render(request, 'view_project.html', {'project': AutodeskConstructionCloudProject.objects.get(pk=project_pk), 'reports': AutodeskConstructionCloudReport.objects.exclude(pk=report_pk), 'report': report})

@login_required
@permission_required('analytics.add_autodeskconstructioncloudproject', 'view_all_projects')
def add_project(request):
    if request.method == "POST":
        form = AutodeskConstructionCloudProjectForm(data=request.POST)
        if form.is_valid():
            project = form.save()
            logger.info(f"[{verbose_user(request)}] created {project.pk}:{project.name}.")
            messages.success(request, "Sucessfully created project.")
            return redirect('view_all_projects')
        else:
            for field, errors in form.errors.get_json_data().items():
                for error in errors:
                    logger.debug(f"[{verbose_user(request)}] [Form Error] {field}: {error['message']}")
                    messages.error(request, f"{field}: {error['message']}")
    else:
        form = AutodeskConstructionCloudProjectForm()
    return render(request, "add_project.html", {"form": form})

@login_required
@permission_required('analytics.delete_autodeskconstructioncloudproject', 'view_all_projects')
def delete_project(request, project_pk):
    project = get_object_or_404(AutodeskConstructionCloudProject, pk=project_pk)
    project.delete()
    logger.info(f"[{verbose_user(request)}] deleted {project.name}.")
    messages.success(request, f"{project.name} was deleted successfully.")
    return redirect('view_all_projects')

@login_required
@permission_required('analytics.view_autodeskconstructioncloudreport', 'dashboard')
def view_all_reports(request):
    r = AutodeskConstructionCloudReport.objects.all()
    return render(request, 'view_all_reports.html', {'reports_list': r})

@login_required
@permission_required('analytics.add_autodeskconstructioncloudreport', 'view_all_reports')
def add_report(request):
    if request.method == "POST":
        updated_request = request.POST.copy()
        if request.FILES.get('excel_report'):
            updated_request.update({'data': [json_from_excel(request.FILES.get('excel_report'))]})
        form = AutodeskConstructionCloudReportForm(data=updated_request)
        if form.is_valid():
            report = form.save()
            logger.info(f"[{verbose_user(request)}] created {report.pk}:{report.name}.")
            messages.success(request, "Sucessfully created report.")
            return redirect('view_all_reports')
        else:
            for field, errors in form.errors.get_json_data().items():
                for error in errors:
                    logger.debug(f"[{verbose_user(request)}] [Form Error] {field}: {error['message']}")
                    messages.error(request, f"{field}: {error['message']}")
    else:
        form = AutodeskConstructionCloudReportForm()
    return render(request, "add_report.html", {"form": form, 'projects_list': AutodeskConstructionCloudProject.objects.all()})

@login_required
@permission_required('analytics.delete_autodeskconstructioncloudreport', 'view_all_reports')
def delete_report(request, report_pk):
    rep = get_object_or_404(AutodeskConstructionCloudReport, pk=report_pk)
    rep.delete()
    logger.info(f"[{verbose_user(request)}] deleted {rep.pk}:{rep.name}.")
    messages.success(request, f"Report {rep.name} was deleted successfully.")
    return redirect('view_all_reports')

@login_required
@permission_required('analytics.view_autodeskconstructioncloudreport')
def report_data(request, report_pk):
    return JsonResponse(AutodeskConstructionCloudReport.objects.get(pk=report_pk).data[0])

@login_required
def dash_data(request):
    num_files = 0; num_data = 0; num_reports = 0
    for rep in AutodeskConstructionCloudReport.objects.all():
        file_size_data = rep.data[0].get('file_sizes').values()
        num_files += len(file_size_data)
        num_data += sum(file_size_data)
        num_reports += 1
    num_projects = len(AutodeskConstructionCloudProject.objects.all())
    return JsonResponse({'files': num_files, 'data': num_data, 'projects': num_projects, 'reports': num_reports})