from django.contrib import admin
from app.models import Form, TextQuestion, NumericQuestion, BaseQuestionType


class TextQuestionInline(admin.TabularInline):
    model = TextQuestion
    extra = 0


class NumericQuestionInline(admin.TabularInline):
    model = NumericQuestion
    extra = 0


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    inlines = [TextQuestionInline, NumericQuestionInline]
    list_display = ("title", "created_date")
    search_fields = ("title",)


@admin.register(TextQuestion)
class TextQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "question_type", "text_type", "answer_max_length")
    list_filter = ("text_type", "question_type")
    search_fields = ("text",)
    exclude = ("question_type",)

    def save_model(self, request, obj, form, change):
        """Ensure `question_type` is always set to TEXT for TextQuestion."""
        obj.question_type = BaseQuestionType.TEXT
        super().save_model(request, obj, form, change)


@admin.register(NumericQuestion)
class NumericQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "question_type",
        "min_value",
        "max_value",
        "is_float_allowed"
    )
    list_filter = ("question_type", "is_float_allowed")
    search_fields = ("text",)
    exclude = ("question_type",)


    def save_model(self, request, obj, form, change):
        """Ensure `question_type` is always set to NUMBER for NumericQuestion."""
        obj.question_type = BaseQuestionType.NUMBER
        super().save_model(request, obj, form, change)

