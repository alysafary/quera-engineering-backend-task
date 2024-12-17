from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.exceptions import FormNotFoundException
from app.models import Form
from app.serializers import SubmitAnswerSerializer


class SubmitAnswerAPIView(APIView):
    def get_form(self):
        form = (
            Form.objects.filter(id=self.kwargs["form_id"])
            .prefetch_related("questions")
            .first()
        )
        if not form:
            raise FormNotFoundException()
        return form

    def post(self, request, *args, **kwargs):
        serializer = SubmitAnswerSerializer(
            data=request.data, context={"form": self.get_form()}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
