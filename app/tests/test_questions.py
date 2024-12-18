from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from app.models import Form, QuestionConfiguration, QuestionType, Question


class QuestionConfigurationTestCase(TestCase):
    def setUp(self):
        self.form = Form.objects.create(title="Sample Form")

    def test_text_config_validation(self):
        config = QuestionConfiguration.objects.create(
            question_type=QuestionType.TEXT, text_format="short", answer_max_length=200
        )
        config.clean()

        config_invalid = QuestionConfiguration(
            question_type=QuestionType.TEXT, text_format="short", answer_max_length=201
        )
        with self.assertRaises(ValidationError):
            config_invalid.clean()

        config_email = QuestionConfiguration.objects.create(
            question_type=QuestionType.TEXT,
            text_format="email",
        )
        config_email.clean()

    def test_number_config_validation(self):
        config = QuestionConfiguration.objects.create(
            question_type=QuestionType.NUMBER,
            min_value=10,
            max_value=20,
            is_decimal_allowed=False,
        )
        config.clean()

        config_invalid = QuestionConfiguration(
            question_type=QuestionType.NUMBER, min_value=30, max_value=20
        )
        with self.assertRaises(ValidationError):
            config_invalid.clean()


class FormListAPIViewTestCase(TestCase):
    def setUp(self):
        self.config_text = QuestionConfiguration.objects.create(
            question_type=QuestionType.TEXT, text_format="short", answer_max_length=200
        )
        self.config_number = QuestionConfiguration.objects.create(
            question_type=QuestionType.NUMBER, min_value=10, max_value=100
        )

        self.form = Form.objects.create(title="Test Form")
        self.question1 = Question.objects.create(
            form=self.form,
            text="What is your favorite color?",
            is_required=True,
            configuration=self.config_text,
        )
        self.question2 = Question.objects.create(
            form=self.form,
            text="What is your age?",
            is_required=False,
            configuration=self.config_number,
        )

    def test_form_list_api(self):
        response = self.client.get(reverse("forms-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        form_data = data[0]
        self.assertEqual(form_data["id"], self.form.id)
        self.assertEqual(form_data["title"], "Test Form")

        question1_data = form_data["questions"][0]
        question2_data = form_data["questions"][1]

        self.assertEqual(question1_data["text"], "What is your favorite color?")
        self.assertTrue(question1_data["is_required"])
        self.assertEqual(question1_data["configuration"]["question_type"], "Text")
        self.assertEqual(question1_data["configuration"]["answer_max_length"], 200)

        self.assertEqual(question2_data["text"], "What is your age?")
        self.assertFalse(question2_data["is_required"])
        self.assertEqual(question2_data["configuration"]["question_type"], "Number")
        self.assertEqual(question2_data["configuration"]["min_value"], 10)
        self.assertEqual(question2_data["configuration"]["max_value"], 100)
