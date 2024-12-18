from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.models import Form, Question, QuestionConfiguration, Answer, QuestionType


class AnswerModelTestCase(TestCase):
    def setUp(self):
        self.form = Form.objects.create(title="Test Form")
        self.text_config = QuestionConfiguration.objects.create(
            question_type=QuestionType.TEXT,
            text_format="email",
            answer_max_length=50,
        )

        self.text_question = Question.objects.create(
            text="What is your email?",
            configuration=self.text_config,
            is_required=True,
            form=self.form,
        )

        self.number_config = QuestionConfiguration.objects.create(
            question_type=QuestionType.NUMBER,
            min_value=10,
            max_value=100,
            is_decimal_allowed=False,
        )

        self.number_question = Question.objects.create(
            text="What is your age?",
            configuration=self.number_config,
            form=self.form,
            is_required=True,
        )

    def test_valid_text_answer(self):
        answer = Answer.objects.create(question=self.text_question, value="test@example.com")
        answer.full_clean()
        self.assertEqual(answer.value, "test@example.com")

    def test_invalid_text_answer_exceeds_max_length(self):
        answer = Answer(question=self.text_question, value="a" * 51)
        with self.assertRaises(ValidationError):
            answer.full_clean()

    def test_invalid_text_answer_invalid_email_format(self):
        answer = Answer(question=self.text_question, value="invalid_email")
        with self.assertRaises(ValidationError):
            answer.full_clean()

    def test_invalid_number_answer_invalid_format(self):
        answer = Answer(question=self.number_question, value="invalid_number")
        with self.assertRaises(ValidationError):
            answer.full_clean()

    def test_invalid_number_answer_below_min_value(self):
        answer = Answer(question=self.number_question, value="5")
        with self.assertRaises(ValidationError):
            answer.full_clean()

    def test_invalid_number_answer_above_max_value(self):
        answer = Answer(question=self.number_question, value="150")
        with self.assertRaises(ValidationError):
            answer.full_clean()


class SubmitAnswerAPIViewTests(APITestCase):
    def setUp(self):
        self.form = Form.objects.create(title="Test Form")
        self.text_config = QuestionConfiguration.objects.create(
            question_type=QuestionType.TEXT,
            answer_max_length=100,
            text_format="short",
        )
        self.number_config = QuestionConfiguration.objects.create(
            question_type=QuestionType.NUMBER,
            min_value=1,
            max_value=10,
        )
        self.text_question = Question.objects.create(
            form=self.form,
            text="What is your name?",
            is_required=True,
            configuration=self.text_config,
        )
        self.number_question = Question.objects.create(
            form=self.form,
            text="Pick a number between 1 and 10.",
            is_required=False,
            configuration=self.number_config,
        )

        self.submit_url = reverse("submit-answers", kwargs={"form_id": self.form.id})

    def test_submit_valid_answers(self):
        data = {
            "answers": [
                {"question": self.text_question.id, "value": "John Doe"},
                {"question": self.number_question.id, "value": "5"},
            ]
        }
        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Answer.objects.count(), 2)

    def test_missing_required_question(self):
        data = {"answers": [{"question": self.number_question.id, "value": "5"}]}
        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("missing_answers", response.data)

    def test_invalid_question_id(self):
        data = {"answers": [{"question": 999, "value": "Invalid Question"}]}
        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_text_answer_exceeds_max_length(self):
        data = {
            "answers": [
                {"question": self.text_question.id, "value": "A" * 101},
            ]
        }
        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_number_answer_out_of_range(self):
        data = {
            "answers": [
                {"question": self.number_question.id, "value": "20"},
            ]
        }
        response = self.client.post(self.submit_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
