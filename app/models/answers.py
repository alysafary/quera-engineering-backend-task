from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models

from .questions import Form, TextQuestion, NumericQuestion


class UserAnswer(models.Model):
    form = models.ForeignKey(Form, related_name="answers", on_delete=models.CASCADE)
    submitted_date = models.DateTimeField(auto_now_add=True)


class TextAnswer(models.Model):
    user_answer = models.ForeignKey(
        UserAnswer, related_name="text_answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(TextQuestion, on_delete=models.CASCADE)
    answer = models.TextField()

    def clean(self):
        """Validate the text answer length based on the question's constraints."""
        if len(self.answer) > self.question.answer_max_length:
            raise ValidationError(
                f"Answer exceeds the maximum allowed length of {self.question.answer_max_length} characters."
            )
        if self.question.text_type == TextQuestion.TextQuestionType.EMAIL:
            validator = EmailValidator(
                message="The provided answer is not a valid email address."
            )
            try:
                validator(self.answer)
            except ValidationError as e:
                raise ValidationError(
                    {"answer": f"Invalid email: {', '.join(e.messages)}"}
                )
        super().clean()

    def __str__(self):
        return f"TextAnswer to '{self.question.text}': {self.answer}"


class NumericAnswer(models.Model):
    user_answer = models.ForeignKey(
        UserAnswer, related_name="numeric_answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(NumericQuestion, on_delete=models.CASCADE)
    answer = models.FloatField()

    def clean(self):
        """Validate the numeric answer based on the question's constraints."""
        if not self.question.is_float_allowed and not float(self.answer).is_integer():
            raise ValidationError(f"Answer must be an integer for this question.")
        if (
            self.question.min_value is not None
            and self.answer < self.question.min_value
        ):
            raise ValidationError(
                f"Answer cannot be less than the minimum value of {self.question.min_value}."
            )
        if (
            self.question.max_value is not None
            and self.answer > self.question.max_value
        ):
            raise ValidationError(
                f"Answer cannot exceed the maximum value of {self.question.max_value}."
            )
        super().clean()

    def __str__(self):
        return f"NumericAnswer to '{self.question.text}': {self.answer}"
