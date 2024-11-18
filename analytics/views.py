import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.postgres.search import SearchVector

from .models import AutodeskConstructionCloudProject
from .forms import AutodeskConstructionCloudProjectForm

logger = logging.getLogger(__name__)

def verbose_user(request) -> str:
    """Returns a unique string representing the user within the request. Meant for logging purposes."""
    return f"{request.user.pk}:{request.user.username}"

@login_required
def index(request):
    return render(request, 'index.html', {'username': request.user.username})

@login_required
def projects(request):
    if not request.user.has_perm('analytics.view_autodeskconstructioncloudproject'):
        raise PermissionDenied
    can_add_projects = True if request.user.has_perm('analytics.add_autodeskconstructioncloudproject') else False
    if request.GET.get('search'):
        p = AutodeskConstructionCloudProject.objects.annotate(search=SearchVector('name', 'org'),).filter(search=request.GET.get('search'))
    else:
        p = AutodeskConstructionCloudProject.objects.all()
    return render(request, 'projects.html', {'can_add_projects': can_add_projects, 'projects': p})

@login_required
def project(request, pk):
    if not request.user.has_perm('analytics.view_autodeskconstructioncloudproject'):
        raise PermissionDenied
    return render(request, 'project.html', {'project': AutodeskConstructionCloudProject.objects.get(pk=pk)})

@login_required
def add_project(request):
    if not request.user.has_perm('analytics.add_autodeskconstructioncloudproject'):
        raise PermissionDenied
    if request.method == "POST":
        print(request.POST)
        form = AutodeskConstructionCloudProjectForm(data=request.POST)
        print(form.errors)
        if form.is_valid():
            proj = form.save()
            return redirect('projects')
    else:
        form = AutodeskConstructionCloudProjectForm()
    return render(request, "add_project.html", {"form": form})

@login_required
def delete_project(request, project_pk):
    if not request.user.has_perm('analytics.delete_autodeskconstructioncloudproject'):
        raise PermissionDenied
    proj = AutodeskConstructionCloudProject.objects.get(pk=project_pk)
    proj.delete()
    logger.info(f"{verbose_user(request)} sucessfully deleted {proj.pk}:{proj.name}.")
    # messages.success(request, f"{software} was deleted successfully.")
    return redirect('projects')