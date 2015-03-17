import json
import urlparse
from django.http import JsonResponse
from decider_backend.settings import HOST_SCHEMA, HOST_ADDRESS, HOST_PORT

TOKEN_URL = urlparse.urlunparse((HOST_SCHEMA, HOST_ADDRESS + ':' + HOST_PORT, '/o/token/', '', '', ''))


def build_ok_response(data):
    return JsonResponse({
        'status': 200,
        'msg': 'ok',
        'data': data
    })


def build_402_response(error_text):
    return JsonResponse({
        'status': 402,
        'msg': 'incorrect data',
        'data': {
            'error_text': error_text
        }
    })


def build_403_response(error_text):
    return JsonResponse({
        'status': 403,
        'msg': 'insufficient data',
        'data': {
            'error_text': error_text
        }
    })


def build_501_response(error_text):
    return JsonResponse({
        'status': 501,
        'msg': 'internal error',
        'data': {
            'error_text': error_text
        }
    })