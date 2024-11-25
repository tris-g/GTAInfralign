import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from .forms import AuthenticationForm

logger = logging.getLogger(__name__)

def verbose_user(request) -> str:
    """Returns a unique string representing the user within the request. Meant for logging purposes."""
    return f"{request.user.pk}:{request.user.username}"

@require_http_methods(['GET', 'POST'])
def login_user(request):
    """Django view for logging a User in."""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        print(form.error_messages)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user is not None:
                login(request, user)
                logger.info(f"{verbose_user(request)} sucessfully logged in.")
                messages.info(request, f"Welcome {user}.")
                return redirect('dashboard')
        logger.info(f"Failed login attempt for {form.cleaned_data.get('username')}.")
    elif request.user.is_authenticated:
        return redirect('dashboard')
    else:
        form = AuthenticationForm(request)
    return render(request, "login.html", {"form": form})