from django.contrib import admin
from django.forms import ModelForm

from .models import Form, Question, QuestionConfiguration


class QuestionConfigurationInlineForm(ModelForm):
    class Meta:
        model = QuestionConfiguration
        fields = "__all__"


class QuestionConfigurationInline(admin.StackedInline):
    model = QuestionConfiguration
    form = QuestionConfigurationInlineForm
    extra = 0
    can_delete = False


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    inlines = [QuestionConfigurationInline]

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class CustomFormSet(formset):
            def save_new(self, form, commit=True):
                question = super().save_new(form, commit=False)

                if not hasattr(question, "configuration"):
                    config = QuestionConfiguration.objects.create()
                    question.configuration = config

                if commit:
                    question.save()
                return question

        return CustomFormSet


class FormAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ("title", "created_date", "question_count")
    search_fields = ("title",)

    def question_count(self, obj):
        return obj.questions.count()

    question_count.short_description = "Number of Questions"


admin.site.register(Form, FormAdmin)
admin.site.register(Question)
admin.site.register(QuestionConfiguration)
