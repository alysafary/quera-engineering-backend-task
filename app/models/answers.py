from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models

from .questions import Question, QuestionType


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.TextField()

    def clean(self):
        config = self.question.configuration
        if config.question_type == QuestionType.TEXT:
            self._validate_text_answer(config=config)
        else:
            self._validate_number_answer(config=config)

    def _validate_text_answer(self, config):
        if config.answer_max_length and len(self.value) > config.answer_max_length:
            raise ValidationError(f"Answer exceeds max length of {config.answer_max_length}")

        if config.text_format == 'email':
            validator = EmailValidator(
                message="The provided answer is not a valid email address."
            )
            try:
                validator(self.value)
            except ValidationError as e:
                raise ValidationError(
                    {"answer": f"Invalid email: {', '.join(e.messages)}"}
                )

    def _validate_number_answer(self, config):
        try:
            num_value = float(self.value)
        except ValueError:
            raise ValidationError("Invalid number format")

        if not config.is_decimal_allowed and not num_value.is_integer():
            raise ValidationError("Decimal numbers are not allowed")

        if config.min_value is not None and num_value < config.min_value:
            raise ValidationError(f"Value must be at least {config.min_value}")

        if config.max_value is not None and num_value > config.max_value:
            raise ValidationError(f"Value must not exceed {config.max_value}")


