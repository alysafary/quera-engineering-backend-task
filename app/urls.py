from django.urls import path
from app.views import FormListAPIView, SubmitAnswerAPIView

urlpatterns = [
    path("forms/", FormListAPIView.as_view(), name="forms-list"),
    path(
        "forms/<int:form_id>/answers/submit/",
        SubmitAnswerAPIView.as_view(),
        name="answers-submit",
    ),
]
