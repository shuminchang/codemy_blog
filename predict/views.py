from django.shortcuts import render
from django.http import JsonResponse
from .models import IrisPredResults, LifeStylePredResults
import unicodedata
import re
import logging
from .apps import iris_model, life_style_model

# Set up logging
logger = logging.getLogger(__name__)

# Views
def prediction_page(request):
    return render(request, 'predict.html')

def iris_prediction_page(request):
    return render(request, 'iris_predict.html')

def life_style_prediction_page(request):
    return render(request, 'life_style_predict.html')

def life_style_process(request):
    if request.POST.get('action') == 'post':
        try:
            emr_text = str(request.POST.get('emr_text'))
            processed_text = symbol_preprocess(emr_text)

            # Make prediction
            global life_style_model  # Ensure global variable is referenced
            test_doc = life_style_model(processed_text)
            classification = max(test_doc.cats, key=test_doc.cats.get)

            LifeStylePredResults.objects.create(emr_text=emr_text, 
                                                processed_text=processed_text, 
                                                classification=classification)

            return JsonResponse({'result': classification, 'emr_text': emr_text, 'processed_text': processed_text},
                                safe=False)
        except Exception as e:
            logger.error(f"Error processing life style prediction: {e}")
            return JsonResponse({'error': str(e)}, status=500)

def iris_process(request):
    if request.POST.get('action') == 'post':
        try:
            sepal_length = float(request.POST.get('sepal_length'))
            sepal_width = float(request.POST.get('sepal_width'))
            petal_length = float(request.POST.get('petal_length'))
            petal_width = float(request.POST.get('petal_width'))

            # Make prediction
            global iris_model  # Ensure global variable is referenced
            result = iris_model.predict([[sepal_length, sepal_width, petal_length, petal_width]])
            classification = result[0]

            IrisPredResults.objects.create(sepal_length=sepal_length, sepal_width=sepal_width, petal_length=petal_length,
                                           petal_width=petal_width, classification=classification)

            return JsonResponse({'result': classification, 'sepal_length': sepal_length,
                                 'sepal_width': sepal_width, 'petal_length': petal_length, 'petal_width': petal_width},
                                safe=False)
        except Exception as e:
            logger.error(f"Error processing iris prediction: {e}")
            return JsonResponse({'error': str(e)}, status=500)

def view_results(request):
    return render(request, 'results.html')

def view_iris_results(request):
    data = {"dataset": IrisPredResults.objects.all()}
    return render(request, "iris_results.html", data)

def view_life_style_results(request):
    data = {"dataset": LifeStylePredResults.objects.all()}
    return render(request, "life_style_results.html", data)

def symbol_preprocess(text):
    text = text.replace('\\n', '')
    text = unicodedata_full2half(text)
    text = ''.join([' ' + ch + ' ' if not ch.isalpha() and not ch.isdigit() else ch for ch in text])
    text = ''.join([' ' if not ch.isalpha() and not ch.isdigit() and not ch in ('+', '-', '\n') else ch for ch in text])
    chinese_pattern = re.compile(r'([\u4e00-\u9fff]+)')
    text = chinese_pattern.sub(r' \1 ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def unicodedata_full2half(text):
    return unicodedata.normalize("NFKC", text)
