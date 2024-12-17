from rest_framework import generics
from app.models import Form
from app.serializers import FormSerializer


class FormListAPIView(generics.ListAPIView):
    queryset = Form.objects.prefetch_related("questions__configuration").all()
    serializer_class = FormSerializer
