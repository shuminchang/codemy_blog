from django.test import TestCase, Client
from django.urls import reverse
from .models import LifeStylePredResults, IrisPredResults
from unittest.mock import patch, MagicMock
from .views import symbol_preprocess, unicodedata_full2half

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()

    def test_prediction_page(self):
        response = self.client.get(reverse('predict:prediction_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'predict.html')

    def test_iris_prediction_page(self):
        response = self.client.get(reverse('predict:iris_prediction_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'iris_predict.html')

    def test_life_style_prediction_page(self):
        response = self.client.get(reverse('predict:life_style_prediction_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'life_style_predict.html')

    @patch('predict.apps.life_style_model')
    def test_life_style_process(self, mock_life_style_model):
        # Mock the model's behavior
        mock_model_instance = MagicMock()
        mock_model_instance.return_value.cats = {'negative': 0.8, 'positive': 0.2}
        mock_life_style_model.return_value = mock_model_instance

        # Prepare data for POST request
        data = {'action': 'post', 'emr_text': 'I don\'t smoke'}

        # Make POST request and check response
        response = self.client.post(reverse('predict:life_style_process'), data)
        self.assertEqual(response.status_code, 200)

        # Parse JSON response
        json_response = response.json()
        self.assertEqual(json_response['result'], 'negative')
        self.assertEqual(json_response['emr_text'], 'I don\'t smoke')

        # Check if object is created in the database
        self.assertEqual(LifeStylePredResults.objects.count(), 1)
        created_object = LifeStylePredResults.objects.first()
        self.assertEqual(created_object.emr_text, 'I don\'t smoke')

    @patch('predict.apps.iris_model')
    def test_iris_process(self, mock_iris_model):
        # Mock the model's predict method
        mock_iris_model.predict.return_value = ['Iris-virginica']

        data = {
            'action': 'post', 
            'sepal_length': 3.0, 
            'sepal_width': 3.0, 
            'petal_length': 4.0, 
            'petal_width': 4.0
        }
        
        response = self.client.post(reverse('predict:iris_process'), data)
        self.assertEqual(response.status_code, 200)

        # Parse JSON response
        json_response = response.json()
        self.assertEqual(json_response['result'], 'Iris-virginica')
        
        # Check if object is created in the database
        self.assertEqual(IrisPredResults.objects.count(), 1)
        created_object = IrisPredResults.objects.first()
        self.assertEqual(created_object.classification, 'Iris-virginica')

    def test_view_results(self):
        response = self.client.get(reverse('predict:results'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'results.html')

    def test_view_iris_results(self):
        # Create a sample IrisPredResults object if needed
        # IrisPredResults.objects.create(...)

        response = self.client.get(reverse('predict:iris_results'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'iris_results.html')
        self.assertTrue('dataset' in response.context)

    def test_view_life_style_results(self):
        # Create a sample LifeStylePredResults object if needed
        # LifeStylePredResults.objects.create(...)

        response = self.client.get(reverse('predict:life_style_results'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'life_style_results.html')
        self.assertTrue('dataset' in response.context)

class TestUtilityFunctions(TestCase):

    def test_symbol_preprocess(self):
        input_text = "Sample text with symbols & characters."
        expected_output = "Sample text with symbols characters"  # Replace with expected output
        self.assertEqual(symbol_preprocess(input_text), expected_output)

    def test_unicodedata_full2half(self):
        input_text = "Ｔｅｓｔ　ｆｕｌｌｗｉｄｔｈ"
        expected_output = "Test fullwidth"
        self.assertEqual(unicodedata_full2half(input_text), expected_output)
