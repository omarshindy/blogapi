from rest_framework import response

class DefaultResponse(response.Response):
    def __init__(self, message, data="", status=None, status_code="", template_name=None, headers=None, exception=False, content_type=None):
        data = {
            "message": message,
            "data": data,
            "status_code": status_code,
        }

        super().__init__(data, status, template_name, headers, exception, content_type)