from django.core.exceptions import ValidationError
from django.db import models


class Form(models.Model):
    title = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class BaseQuestionType(models.IntegerChoices):
    TEXT = 1, "Text"
    NUMBER = 4, "Number"


class BaseQuestion(models.Model):
    form = models.ForeignKey(
        Form, related_name="questions", on_delete=models.CASCADE
    )
    text = models.TextField()
    is_required = models.BooleanField(default=False)
    question_type = models.IntegerField(
        choices=BaseQuestionType.choices, default=BaseQuestionType.TEXT
    )

    class Meta:
        abstract = True


class TextQuestionType(models.IntegerChoices):
    SHORT_TEXT = 1, "Short Text"
    LONG_TEXT = 2, "Long Text"
    EMAIL = 3, "Email"


class TextQuestion(BaseQuestion):
    text_type = models.IntegerField(
        choices=TextQuestionType.choices, default=TextQuestionType.SHORT_TEXT
    )
    form = models.ForeignKey(
        Form, related_name="text_questions", on_delete=models.CASCADE
    )
    answer_max_length = models.PositiveIntegerField()

    def map_text_type_to_max_length(self):
        """Map text type to corresponding maximum length."""
        text_type_map = {
            self.TextQuestionType.SHORT_TEXT: 200,
            self.TextQuestionType.LONG_TEXT: 5000,
            self.TextQuestionType.EMAIL: 320,
        }
        return text_type_map.get(self.text_type, 200)

    def clean(self):
        """Validate answer_max_length based on text type."""
        if self.question_type != self.BaseQuestionType.TEXT:
            raise ValidationError("Invalid question type for TextQuestion.")

        mapped_max_length = self.map_text_type_to_max_length()
        if self.answer_max_length and self.answer_max_length > mapped_max_length:
            raise ValidationError(
                f"Answer max length cannot exceed {mapped_max_length} characters for {self.get_text_type_display()} type."
            )
        super().clean()

    def save(self, *args, **kwargs):
        """Automatically set answer_max_length based on text_type before saving."""
        if not self.answer_max_length:
            self.answer_max_length = self.map_text_type_to_max_length()
        super().save(*args, **kwargs)


class NumericQuestion(BaseQuestion):
    form = models.ForeignKey(
        Form, related_name="numeric_questions", on_delete=models.CASCADE
    )
    is_float_allowed = models.BooleanField(
        default=True,
        help_text="Check if floating-point numbers are allowed.",
    )
    min_value = models.FloatField(
        null=True,
        blank=True,
        help_text="Optional minimum numeric value.",
    )
    max_value = models.FloatField(
        null=True,
        blank=True,
        help_text="Optional maximum numeric value.",
    )

    def clean(self):
        """Custom validation for min_value and max_value."""
        if self.question_type != self.BaseQuestionType.NUMBER:
            raise ValidationError("Invalid question type for NumericQuestion.")
        if self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                raise ValidationError(
                    {
                        "min_value": "Minimum value cannot be greater than the maximum value."
                    }
                )

        if not self.is_float_allowed:
            if self.min_value is not None and not float(self.min_value).is_integer():
                raise ValidationError(
                    {"min_value": "Minimum value must be an integer."}
                )
            if self.max_value is not None and not float(self.max_value).is_integer():
                raise ValidationError(
                    {"max_value": "Maximum value must be an integer."}
                )

        super().clean()
