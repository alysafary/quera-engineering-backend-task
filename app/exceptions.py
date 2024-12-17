from rest_framework.exceptions import APIException
from rest_framework import status


class FormNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Form not found"
    default_code = "not_found"


class QuestionNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Question not found"
    default_code = "not_found"
