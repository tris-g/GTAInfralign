from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages

def permission_required(permission, redirect_to=None, message='Incorrect permissions.'):
    """
    Decorator to check if a user has a specific permission.

    Args:
        permission (str): The required permission in the format 'app_label.permission_codename'.
        redirect_to (str): The URL to redirect to if the user lacks the permission. Defaults to None (raises PermissionDenied).
        message (str): The error message to display if permission is missing. Defaults to 'Incorrect permissions.'.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_perm(permission):
                if redirect_to:
                    if message:
                        messages.error(request, message)
                    return redirect(redirect_to)
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator