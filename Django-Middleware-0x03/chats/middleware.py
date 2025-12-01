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