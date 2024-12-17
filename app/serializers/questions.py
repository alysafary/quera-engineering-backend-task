from rest_framework import serializers

from app.models import Form, Question, QuestionConfiguration


class QuestionConfigurationSerializer(serializers.ModelSerializer):
    question_type = serializers.SerializerMethodField()

    class Meta:
        model = QuestionConfiguration
        fields = (
            "question_type",
            "answer_max_length",
            "text_format",
            "min_value",
            "max_value",
            "is_decimal_allowed",
        )

    def get_question_type(self, obj):
        return obj.get_question_type_display()


class QuestionSerializer(serializers.ModelSerializer):
    configuration = QuestionConfigurationSerializer()

    class Meta:
        model = Question
        fields = ("id", "text", "is_required", "configuration")


class FormSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = ("id", "title", "created_date", "questions")
