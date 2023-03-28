import json

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

def api_response(data: dict, code: int = 200):
    response = JsonResponse(data=data, status=code)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'POST'
    response['Access-Control-Allow-Headers'] = 'Authorization'
    response['Content-Type'] = 'application/json; charset=utf-8'
    return response

def api_error(data: dict):
    return api_response({
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "severity": data.get("severity", "None"),
        "success": False
    }, code=data.get("code", 500))

def error_from(response: JsonResponse) -> dict:
    data = json.loads(response.content)
    return {
        'code': response.status_code,
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "severity": data.get("severity", "Medium"),
        "success": False,
        "color": "bg-orange-lt",           
    }