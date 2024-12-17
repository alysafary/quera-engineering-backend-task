from django.core.exceptions import ValidationError
from django.db import models


class Form(models.Model):
    title = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class QuestionType(models.IntegerChoices):
    TEXT = 1, "Text"
    NUMBER = 2, "Number"


class QuestionConfiguration(models.Model):
    question_type = models.IntegerField(
        choices=QuestionType.choices, default=QuestionType.TEXT
    )

    # Text-specific configurations
    answer_max_length = models.PositiveIntegerField(default=200)
    text_format = models.CharField(
        max_length=50,
        default="short",
        choices=[
            ("short", "Short Text"),
            ("long", "Long Text"),
            ("email", "Email"),
        ],
    )

    # Number-specific configurations
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    is_decimal_allowed = models.BooleanField(default=True)

    def __str__(self):
        return f"Config | Type:{self.get_question_type_display()} | ID: {self.pk}"

    def clean(self):
        if self.question_type == QuestionType.TEXT:
            self._validate_text_config()
        else:
            self._validate_number_config()

    def _validate_text_config(self):
        map_text_type_to_length = {
            "short": 200,
            "long": 5000,
            "email": 320,
        }
        expected_length = map_text_type_to_length[self.text_format]
        if self.answer_max_length and self.answer_max_length > expected_length:
            raise ValidationError(
                f"Answer max length cannot exceed {expected_length} characters for {self.text_format} type."
            )

    def _validate_number_config(self):
        if (
            self.min_value is not None
            and self.max_value is not None
            and self.min_value > self.max_value
        ):
            raise ValidationError("Minimum value cannot exceed maximum value.")



class Question(models.Model):
    form = models.ForeignKey(Form, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    is_required = models.BooleanField(default=False)
    configuration = models.OneToOneField(
        QuestionConfiguration,
        on_delete=models.CASCADE,
        related_name='question'
    )

    def __str__(self):
        return self.text