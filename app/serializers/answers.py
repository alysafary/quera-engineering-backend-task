from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from app.models import Answer


class SubmitAnswerSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
    )

    class Meta:
        fields = ("answers",)

    def validate(self, data):
        form = self.context.get("form")
        submitted_answers = data.get("answers", [])

        form_questions = form.questions.in_bulk(field_name="id")

        required_questions = set(
            form.questions.filter(is_required=True).values_list("id", flat=True)
        )
        submitted_question_ids = {answer["question"] for answer in submitted_answers}

        # Check for missing required questions
        if missing_questions := required_questions - submitted_question_ids:
            missing_question_texts = list(
                form.questions.filter(id__in=missing_questions).values_list(
                    "text", flat=True
                )
            )
            raise serializers.ValidationError(
                {
                    "missing_answers": f"Answers required for: {', '.join(missing_question_texts)}"
                }
            )

        for answer_data in submitted_answers:
            question_id = answer_data["question"]

            if question_id not in form_questions:
                raise serializers.ValidationError(
                    {
                        "question": f"Question {question_id} does not belong to this form."
                    }
                )

            try:
                question = form_questions[question_id]
                Answer(question=question, value=answer_data["value"]).clean()
            except ValidationError as e:
                raise serializers.ValidationError(
                    {f"question_{question_id}": e.message_dict or e.messages}
                )

        return data

    def create(self, validated_data):
        form = self.context.get("form")
        answers_data = validated_data["answers"]

        # Fetch questions in a single query to avoid repeated database hits
        questions = form.questions.in_bulk(field_name="id")

        answers = [
            Answer(question=questions[answer["question"]], value=answer["value"])
            for answer in answers_data
        ]

        created_answers = Answer.objects.bulk_create(answers)

        submitted_answers = [
            {
                "question": answer["question"],
                "value": answer["value"],
            }
            for answer in answers_data
        ]

        return {
            "status": "success",
            "message": "Answers submitted successfully.",
            "submitted_answers": submitted_answers,
            "count": len(created_answers),
        }
