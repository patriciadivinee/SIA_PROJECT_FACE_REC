from functools import wraps
from django.http import HttpResponseForbidden

def emp_access(view_func):
    #Decorator to restrict access to views based on emp_access attribute.
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if request.user.is_authenticated and (user.emp_access or user.is_staff or user.is_superuser):
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You don't have permission to access this page.")

    return _wrapped_view