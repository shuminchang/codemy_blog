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

    @patch('predict.views.pd')
    def test_life_style_process(self, mock_pd):
        # Mock the model's behavior
        mock_model = mock_pd.read_pickle.return_value
        mock_model.return_value.cats = {'classification_1': 0.8, 'classification_2': 0.2}

        # Prepare data for POST request
        data = {'action': 'post', 'emr_text': 'sample text'}

        # Make POST request and check response
        response = self.client.post(reverse('predict:life_style_process'), data)
        self.assertEqual(response.status_code, 200)

        # Parse JSON response
        json_response = response.json()
        self.assertEqual(json_response['result'], 'classification_1')
        self.assertEqual(json_response['emr_text'], 'sample text')

        # Check if object is created in the database
        self.assertEqual(LifeStylePredResults.objects.count(), 1)
        created_object = LifeStylePredResults.objects.first()
        self.assertEqual(created_object.emr_text, 'sample text')

    @patch('predict.views.pd.read_pickle')
    def test_iris_process(self, mock_read_pickle):
        # Mock the model's predict method
        mock_model = MagicMock()
        mock_model.predict.return_value = ['classification_1']
        mock_read_pickle.return_value = mock_model

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
        self.assertEqual(json_response['result'], 'classification_1')
        
        # Check if object is created in the database
        self.assertEqual(IrisPredResults.objects.count(), 1)
        created_object = IrisPredResults.objects.first()
        self.assertEqual(created_object.classification, 'classification_1')


    # @patch('predict.views.pd')
    # def test_iris_process(self, mock_pd):

    #     mock_model = mock_pd.read_pickle.return_value
    #     mock_model.return_value.cats = ['classification_1']

    #     data = {'action': 'post', 
    #             'sepal_length': 3.0, 
    #             'sepal_width': 3.0, 
    #             'petal_length': 4.0, 
    #             'petal_width': 4.0}
        
    #     response = self.client.post(reverse('predict:iris_process'), data)
    #     self.assertEqual(response.status_code, 200)
        
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