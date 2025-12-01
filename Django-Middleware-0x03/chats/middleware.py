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
    
    
import time
from collections import defaultdict
from django.http import JsonResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Data structures for rate limiting
        self.message_counts = defaultdict(list)  # {ip: [timestamp1, timestamp2, ...]}
        self.max_messages_per_minute = 5  # Rate limit: 5 messages per minute
        self.time_window_seconds = 60  # 1 minute window
        
        # Cache for blocked IPs to avoid repeated processing
        self.blocked_ips = {}
        
        # Path to monitor (chat/message endpoints)
        self.restricted_paths = [
            '/api/messages/',
            '/api/chat/',
            '/api/send-message/',
            '/messages/',
            '/chat/'
        ]
        
        # Cleanup interval (clean old entries every 100 requests)
        self.request_counter = 0
        self.cleanup_interval = 100
    
    def __call__(self, request):
        # Get client IP address
        ip_address = self.get_client_ip(request)
        
        # Only process POST requests to restricted paths
        if request.method == 'POST' and self.is_restricted_path(request.path):
            current_time = time.time()
            
            # Clean old entries periodically
            self.request_counter += 1
            if self.request_counter >= self.cleanup_interval:
                self.cleanup_old_entries()
                self.request_counter = 0
            
            # Check if IP is currently blocked
            if ip_address in self.blocked_ips:
                block_info = self.blocked_ips[ip_address]
                if current_time < block_info['blocked_until']:
                    # Still blocked
                    remaining_time = int(block_info['blocked_until'] - current_time)
                    logger.warning(f"IP {ip_address} is blocked for {remaining_time} more seconds")
                    
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': f'You have sent too many messages. Please try again in {remaining_time} seconds.',
                        'status': 'blocked',
                        'blocked_until': block_info['blocked_until'],
                        'retry_after': remaining_time
                    }, status=429)
                else:
                    # Block expired, remove from blocked list
                    del self.blocked_ips[ip_address]
            
            # Check rate limiting
            if self.is_rate_limited(ip_address, current_time):
                # Block the IP for 1 minute
                block_duration = 60  # 1 minute block
                self.blocked_ips[ip_address] = {
                    'blocked_at': current_time,
                    'blocked_until': current_time + block_duration,
                    'message_count': len(self.message_counts[ip_address])
                }
                
                logger.warning(f"IP {ip_address} blocked for {block_duration} seconds due to rate limit violation")
                
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': 'You have exceeded the limit of 5 messages per minute. Please wait 1 minute before sending more messages.',
                    'status': 'blocked',
                    'blocked_until': current_time + block_duration,
                    'retry_after': block_duration,
                    'limit': self.max_messages_per_minute,
                    'window': '1 minute'
                }, status=429)
            
            # Add current request timestamp
            self.message_counts[ip_address].append(current_time)
            
            # Log for monitoring (optional)
            message_count = len(self.message_counts[ip_address])
            logger.info(f"IP {ip_address} sent message {message_count} at {current_time}")
        
        # Process the request normally
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        
        if x_forwarded_for:
            # In case of multiple proxies, take the first IP
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip or 'unknown'
    
    def is_restricted_path(self, path):
        """Check if the requested path is a chat/message endpoint"""
        # Check exact paths or path prefixes
        return any(
            path.startswith(restricted_path) or 
            path == restricted_path.rstrip('/') or
            path == restricted_path
            for restricted_path in self.restricted_paths
        )
    
    def is_rate_limited(self, ip_address, current_time):
        """Check if IP has exceeded rate limit"""
        if ip_address not in self.message_counts:
            return False
        
        # Filter timestamps within the time window
        timestamps = self.message_counts[ip_address]
        window_start = current_time - self.time_window_seconds
        
        # Count messages in the last minute
        recent_messages = [ts for ts in timestamps if ts >= window_start]
        
        # Update the list to only keep recent messages
        self.message_counts[ip_address] = recent_messages
        
        # Check if limit exceeded
        if len(recent_messages) >= self.max_messages_per_minute:
            logger.warning(f"IP {ip_address} exceeded limit: {len(recent_messages)} messages in last minute")
            return True
        
        return False
    
    def cleanup_old_entries(self):
        """Remove old entries to prevent memory leak"""
        current_time = time.time()
        window_start = current_time - self.time_window_seconds
        
        # Clean message counts
        for ip in list(self.message_counts.keys()):
            self.message_counts[ip] = [
                ts for ts in self.message_counts[ip] 
                if ts >= window_start
            ]
            if not self.message_counts[ip]:
                del self.message_counts[ip]
        
        # Clean blocked IPs
        for ip in list(self.blocked_ips.keys()):
            if current_time > self.blocked_ips[ip]['blocked_until']:
                del self.blocked_ips[ip]
        
        logger.debug("Cleaned up old rate limiting entries")
    
    def get_rate_limit_info(self, ip_address):
        """Get current rate limit status for an IP (for monitoring/debugging)"""
        if ip_address not in self.message_counts:
            return {
                'ip': ip_address,
                'current_count': 0,
                'limit': self.max_messages_per_minute,
                'is_blocked': False
            }
        
        current_time = time.time()
        window_start = current_time - self.time_window_seconds
        
        recent_messages = [
            ts for ts in self.message_counts[ip_address] 
            if ts >= window_start
        ]
        
        is_blocked = ip_address in self.blocked_ips
        blocked_info = None
        
        if is_blocked:
            blocked_info = {
                'blocked_until': self.blocked_ips[ip_address]['blocked_until'],
                'blocked_at': self.blocked_ips[ip_address]['blocked_at'],
                'remaining_block_time': max(0, self.blocked_ips[ip_address]['blocked_until'] - current_time)
            }
        
        return {
            'ip': ip_address,
            'current_count': len(recent_messages),
            'limit': self.max_messages_per_minute,
            'window_seconds': self.time_window_seconds,
            'is_blocked': is_blocked,
            'blocked_info': blocked_info,
            'all_time_count': len(self.message_counts[ip_address])
        }
        
        
class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define role-based permissions
        self.role_permissions = {
            'admin': {
                'allowed_paths': [
                    '/admin/',
                    '/api/admin/',
                    '/api/users/',
                    '/api/settings/',
                    '/api/reports/',
                    '/api/analytics/',
                    '/dashboard/',
                ],
                'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
                'description': 'Full access to all admin functions'
            },
            'moderator': {
                'allowed_paths': [
                    '/api/moderate/',
                    '/api/content/',
                    '/api/comments/',
                    '/api/posts/',
                    '/moderator/',
                ],
                'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE'],
                'description': 'Content moderation access'
            },
            'user': {
                'allowed_paths': [
                    '/api/profile/',
                    '/api/messages/',
                    '/api/comments/',
                    '/api/posts/',
                    '/api/likes/',
                ],
                'allowed_methods': ['GET', 'POST', 'PUT'],
                'description': 'Regular user access'
            },
            'guest': {
                'allowed_paths': [
                    '/api/public/',
                    '/api/posts/public/',
                    '/api/comments/public/',
                    '/',
                ],
                'allowed_methods': ['GET'],
                'description': 'Read-only public access'
            }
        }
        
        # Define public paths that don't require role checking
        self.public_paths = [
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/auth/token/refresh/',
            '/api/public/',
            '/admin/login/',
            '/health/',
            '/robots.txt',
            '/favicon.ico',
        ]
        
        # Define admin-only paths (extra protection)
        self.admin_only_paths = [
            '/api/admin/',
            '/api/system/',
            '/api/settings/global/',
            '/api/users/bulk/',
            '/api/database/',
        ]
        
        # Map roles to required permissions
        self.required_permissions_map = {
            '/api/users/delete/': ['admin'],
            '/api/settings/update/': ['admin'],
            '/api/content/delete/': ['admin', 'moderator'],
            '/api/comments/moderate/': ['admin', 'moderator'],
            '/api/posts/publish/': ['admin', 'moderator'],
        }
    
    def __call__(self, request):
        # Get the requested path and method
        path = request.path
        method = request.method
        
        # Skip public paths
        if self.is_public_path(path):
            return self.get_response(request)
        
        # Get user from request
        user = request.user
        
        # Check if user is authenticated
        if not user.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to {path}")
            return JsonResponse({
                'error': 'Authentication required',
                'message': 'You must be logged in to access this resource',
                'status': 401
            }, status=401)
        
        # Determine user's role
        user_role = self.get_user_role(user)
        
        # Check if user has access to the requested path
        if not self.has_permission(user_role, path, method):
            logger.warning(
                f"Permission denied - User: {user.username}, "
                f"Role: {user_role}, Path: {path}, Method: {method}"
            )
            
            return JsonResponse({
                'error': 'Permission denied',
                'message': f'You do not have permission to access this resource',
                'required_role': self.get_required_role_for_path(path),
                'your_role': user_role,
                'path': path,
                'method': method,
                'status': 403
            }, status=403)
        
        # Check for specific permission requirements
        required_permissions = self.get_required_permissions(path)
        if required_permissions and user_role not in required_permissions:
            logger.warning(
                f"Insufficient permissions - User: {user.username}, "
                f"Role: {user_role}, Required: {required_permissions}"
            )
            
            return JsonResponse({
                'error': 'Insufficient permissions',
                'message': 'Your role does not have sufficient permissions for this action',
                'required_roles': required_permissions,
                'your_role': user_role,
                'action': self.get_action_description(path),
                'status': 403
            }, status=403)
        
        # Add role information to request for use in views
        request.user_role = user_role
        request.user_permissions = self.get_user_permissions(user_role)
        
        # Log successful access (optional, for auditing)
        if path in self.admin_only_paths or user_role == 'admin':
            logger.info(
                f"Admin access - User: {user.username}, "
                f"Role: {user_role}, Path: {path}"
            )
        
        # Process the request
        response = self.get_response(request)
        
        # Add role information to response headers (optional)
        response['X-User-Role'] = user_role
        response['X-User-Permissions'] = ','.join(request.user_permissions)
        
        return response
    
    def get_user_role(self, user):
        """
        Determine the user's role.
        This can be customized based on your user model structure.
        """
        # Method 1: Check if user is staff/superuser
        if user.is_superuser:
            return 'admin'
        elif user.is_staff:
            return 'moderator'  # or 'staff' based on your logic
        
        # Method 2: Check user groups
        if user.groups.filter(name='Administrators').exists():
            return 'admin'
        elif user.groups.filter(name='Moderators').exists():
            return 'moderator'
        elif user.groups.filter(name='Premium Users').exists():
            return 'premium_user'
        
        # Method 3: Check custom profile field (if you have one)
        try:
            # Assuming you have a UserProfile model with a 'role' field
            return user.profile.role
        except AttributeError:
            pass
        
        # Method 4: Check based on username or email pattern
        if hasattr(user, 'email') and user.email.endswith('@admin.com'):
            return 'admin'
        
        # Default role
        return 'user'
    
    def has_permission(self, role, path, method):
        """
        Check if the role has permission to access the path with given method
        """
        if role not in self.role_permissions:
            return False
        
        role_config = self.role_permissions[role]
        
        # Check if path is allowed for this role
        path_allowed = any(
            path.startswith(allowed_path) or 
            path == allowed_path.rstrip('/')
            for allowed_path in role_config['allowed_paths']
        )
        
        if not path_allowed:
            return False
        
        # Check if method is allowed for this role
        if method not in role_config['allowed_methods']:
            return False
        
        return True
    
    def is_public_path(self, path):
        """
        Check if the path is public and doesn't require authentication
        """
        # Check exact match or path starts with
        return any(
            path == public_path.rstrip('/') or
            path.startswith(public_path)
            for public_path in self.public_paths
        )
    
    def get_required_role_for_path(self, path):
        """
        Determine which roles can access a specific path
        """
        allowed_roles = []
        for role, config in self.role_permissions.items():
            if any(path.startswith(allowed_path) for allowed_path in config['allowed_paths']):
                allowed_roles.append(role)
        return allowed_roles
    
    def get_required_permissions(self, path):
        """
        Get required permissions for a specific path
        """
        for permission_path, required_roles in self.required_permissions_map.items():
            if path.startswith(permission_path):
                return required_roles
        return None
    
    def get_action_description(self, path):
        """
        Get a human-readable description of the action
        """
        action_map = {
            '/api/users/delete/': 'Delete users',
            '/api/settings/update/': 'Update system settings',
            '/api/content/delete/': 'Delete content',
            '/api/comments/moderate/': 'Moderate comments',
            '/api/posts/publish/': 'Publish posts',
        }
        
        for action_path, description in action_map.items():
            if path.startswith(action_path):
                return description
        
        return 'Perform action'
    
    def get_user_permissions(self, role):
        """
        Get list of permissions for a specific role
        """
        if role not in self.role_permissions:
            return []
        
        permissions = []
        role_config = self.role_permissions[role]
        
        # Convert allowed paths to permission names
        for path in role_config['allowed_paths']:
            permission_name = path.strip('/').replace('/', '_').replace('-', '_')
            if permission_name:
                permissions.append(permission_name)
        
        # Add method-based permissions
        for method in role_config['allowed_methods']:
            permissions.append(f"can_{method.lower()}")
        
        return permissions