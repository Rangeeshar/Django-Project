import json

from django.http import HttpResponse
from tastypie.http import (
    HttpUnauthorized,
    HttpForbidden,
    HttpMethodNotAllowed,
    HttpApplicationError,
    HttpBadRequest,
)


class APIResponse(object):
    @classmethod
    def unauthorized(cls, msg, extend_dict=None):
        error_dict = {
            "status": "error",
            "message": msg,
        }
        if extend_dict:
            error_dict.update(extend_dict)
        msg_json = json.dumps(error_dict)
        return HttpUnauthorized(msg_json, content_type="application/json")

    @classmethod
    def forbidden(cls, msg):
        msg_json = '{"status": "error", "message": "%s" }' % msg
        return HttpForbidden(msg_json, content_type="application/json")

    @classmethod
    def not_supported(cls, msg):
        msg_json = '{"status": "error", "message": "%s" }' % msg
        return HttpMethodNotAllowed(msg_json, content_type="application/json")

    @classmethod
    def bad_request(cls, msg, extend_dict=None, err_code=None):
        error_dict = {
            "status": "error",
            "message": msg,
        }
        if extend_dict:
            error_dict.update(extend_dict)

        if err_code is not None:
            error_dict["err_code"] = err_code

        msg_json = json.dumps(error_dict)

        return HttpBadRequest(msg_json, content_type="application/json")

    @classmethod
    def failed_dependency(cls, msg, extend_dict=None):
        error_dict = {
            "status": "error",
            "message": msg,
        }
        if extend_dict:
            error_dict.update(extend_dict)
        msg_json = json.dumps(error_dict)
        return HttpResponse(msg_json, status=424, content_type="application/json")

    @classmethod
    def server_error(cls, msg):
        msg_json = '{"status": "error", "message": "%s" }' % msg
        return HttpApplicationError(msg_json, content_type="application/json")

    @classmethod
    def service_unavailable(cls, msg):
        error_dict = {"status": "error", "message": msg}
        msg_dump = json.dumps(error_dict)
        return HttpResponse(msg_dump, status=503, content_type="application/json")

    @classmethod
    def bad_gateway(cls, msg):
        error_dict = {"status": "error", "message": msg}
        msg_dump = json.dumps(error_dict)
        return HttpResponse(msg_dump, status=502, content_type="application/json")

    @classmethod
    def no_content(cls, msg):
        msg_dict = {"status": "success", "message": msg}
        msg_dump = json.dumps(msg_dict)
        return HttpResponse(msg_dump, status=204, content_type="application/json")

    @classmethod
    def ok(cls, msg=None, extend_dict=None):
        msg_dict = {"status": "success"}
        if msg is not None:
            msg_dict.update({"message": msg})
        if extend_dict:
            msg_dict.update(extend_dict)
        msg_json = json.dumps(msg_dict)

        return HttpResponse(msg_json, content_type="application/json")

    @classmethod
    def accepted(cls, msg, extend_dict=None):
        msg_dict = {"status": "accepted", "message": "%s" % msg}
        if extend_dict:
            msg_dict.update(extend_dict)
        msg_dump = json.dumps(msg_dict)
        return HttpResponse(msg_dump, status=202, content_type="application/json")
