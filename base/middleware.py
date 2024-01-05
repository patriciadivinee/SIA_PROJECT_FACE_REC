from django.http import HttpResponseForbidden
from django.shortcuts import render

class EmpAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if request.user.is_authenticated and not user.emp_access:
            # Set a flag in the request object
            request.access_denied = True
        else:
            request.access_denied = False

        response = self.get_response(request)
        return response