from datetime import datetime
from rest_framework import status
from django.http import JsonResponse
from django.utils import timezone

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        user = request.user
        
        try:
            file = open("/home/vboxuser/Development/alx-backend-python/alx-backend-python/Django-Middleware-0x03/requests.log", "a")
            file.write(f"{datetime.now()} - User: {user} - Path: {request.path}\n")
        except Exception as e:
            return ("Filed open file", e)
        
        response = self.get_response(request)
        
        return response
    

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        now = timezone.now()
        
        current_hour = now.hour
        current_minute = now.minute

        is_within_restricted_time = (
            (current_hour > 18 or (current_hour == 18 and current_minute >= 0)) and
            (current_hour < 21 or (current_hour == 21 and current_minute == 0))
        )
        
        restricted_path = '/api/message/'
        
        print(f"Time: {now.time()}, Path: {request.path}, Restricted: {is_within_restricted_time}")
        
        if is_within_restricted_time and request.path.startswith(restricted_path):
            return JsonResponse(
                {
                    'error': 'Access denied',
                    'message': 'This endpoint is only accessible outside of 6:00 PM to 9:00 PM',
                    'current_time': str(now.time()),
                    'restricted_period': '6:00 PM - 9:00 PM'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        response = self.get_response(request)
        return response
    