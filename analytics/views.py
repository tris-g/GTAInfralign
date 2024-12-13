import logging, json

from django.shortcuts import render, redirect
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
@permission_required('analytics.add_autodeskconstructioncloudproject', 'view_all_projects')
def add_project(request):
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
@permission_required('analytics.delete_autodeskconstructioncloudproject', 'view_all_projects')
def delete_project(request, project_pk):
    project = AutodeskConstructionCloudProject.objects.get(pk=project_pk)
    project.delete()
    logger.info(f"{verbose_user(request)} sucessfully deleted {project.pk}:{project.name}.")
    messages.success(request, f"{project.name} was deleted successfully.")

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
            form.save()
            messages.success(request, "Sucessfully created report.")
            return redirect('view_all_reports')
        else:
            messages.error(request, "Incorrect form.")
    else:
        form = AutodeskConstructionCloudReportForm()
    return render(request, "add_report.html", {"form": form, 'projects_list': AutodeskConstructionCloudProject.objects.all()})

@login_required
@permission_required('analytics.delete_autodeskconstructioncloudreport', 'view_all_reports')
def delete_report(request, report_pk):
    rep = AutodeskConstructionCloudReport.objects.get(pk=report_pk)
    rep.delete()
    logger.info(f"{verbose_user(request)} sucessfully deleted {rep.pk}:{rep.name}.")
    messages.success(request, f"Report {rep.name} was deleted successfully.")

@login_required
@permission_required('analytics.view_autodeskconstructioncloudreport')
def report_data(request, report_pk):
    return JsonResponse(AutodeskConstructionCloudReport.objects.get(pk=report_pk).data[0])

@login_required
def dash_data(request):
    num_files = 0; num_data = 0; num_reports = 0
    for rep in AutodeskConstructionCloudReport.objects.all():
        file_size_data = json.loads(rep.data[0].get('file_sizes'))
        num_files += len(file_size_data)
        num_data += sum(file_size_data)
        num_reports += 1
    num_projects = len(AutodeskConstructionCloudProject.objects.all())
    return JsonResponse({'files': num_files, 'data': num_data, 'projects': num_projects, 'reports': num_reports})