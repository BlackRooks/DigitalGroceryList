import logging
import time

from django.db import connection, reset_queries

import time
from django.utils.deprecation import MiddlewareMixin

class LogResponseTimeMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            response_time = time.time() - request.start_time
            total_queries = len(connection.queries)
            print(f"Response Time: {response_time:.3f} seconds")  # Logs to console
            print(f"Total Queries: {total_queries}")
        return response