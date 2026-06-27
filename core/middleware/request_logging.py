import json
import logging
import time


logger = logging.getLogger("requests")


class RequestLoggingMiddleware:
    sensitive_fields = {
        'password',
        'token',
        'access',
        'refresh',
        'authorization',
        'secret',
        'api_key',
        'client_secret',
        'jwt',
        'session',
        'cookie',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def redact_sensitive_fields(self, data):
        if isinstance(data, dict):
            redacted = {}

            for key, value in data.items():
                normalized_key = str(key).lower()

                if any(field in normalized_key for field in self.sensitive_fields):
                    redacted[key] = '***REDACTED***'
                else:
                    redacted[key] = self.redact_sensitive_fields(value)

            return redacted

        if isinstance(data, list):
            return [self.redact_sensitive_fields(item) for item in data]

        return data

    def parse_request_body(self, request):
        try:
            body = request.body.decode('utf-8')

            if not body:
                return {}

            data = json.loads(body)

            return self.redact_sensitive_fields(data)

        except Exception:
            return {}

    def parse_response_body(self, response):
        try:
            if not hasattr(response, "content"):
                return {}

            content = response.content.decode('utf-8')

            if not content:
                return {}

            data = json.loads(content)

            return self.redact_sensitive_fields(data)

        except Exception:
            return {}

    def __call__(self, request):
        start_time = time.time()

        request_body = self.parse_request_body(request)

        response = self.get_response(request)

        duration = time.time() - start_time

        response_body = self.parse_response_body(response)

        log_data = {
            'method': request.method,
            'path': request.path,
            'query_params': self.redact_sensitive_fields(dict(request.GET)),
            'request_body': request_body,
            'response_body': response_body,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
        }

        if hasattr(request, "user") and request.user.is_authenticated:
            log_data['user_id'] = str(request.user.id)

        logger.info(json.dumps(log_data))

        return response
