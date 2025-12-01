from datetime import datetime

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