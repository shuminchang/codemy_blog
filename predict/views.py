from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
from .models import IrisPredResults, LifeStylePredResults
import unicodedata
import re
import os
from django.conf import settings

current_directory_path = os.getcwd()

def prediction_page(request):
    return render(request, 'predict.html')

def iris_prediction_page(request):
    return render(request, 'iris_predict.html')

def life_style_prediction_page(request):
    return render(request, 'life_style_predict.html')

def load_model(model_type):
    model_path = os.path.join(settings.BASE_DIR, model_type)
    model = pd.read_pickle(model_path)
    return model

def life_style_process(request):
    # return render(request, 'life_style.html')

    if request.POST.get('action') == 'post':

        emr_text = str(request.POST.get('emr_text'))
        processed_text = symbol_preprocess(emr_text)

        # Unpickle model
        life_style_model = load_model('life_style_en_model_20231221.pkl')

        # Make prediction
        test_doc = life_style_model(processed_text)
        # Get the max probability as results
        classification = max(test_doc.cats, key=test_doc.cats.get)

        LifeStylePredResults.objects.create(emr_text=emr_text, 
                                            processed_text=processed_text, 
                                            classification=classification)

        return JsonResponse({'result': classification, 'emr_text': emr_text, 'processed_text': processed_text},
                            safe=False)

def iris_process(request):

    if request.POST.get('action') == 'post':

        # Receive data from client
        sepal_length = float(request.POST.get('sepal_length'))
        sepal_width = float(request.POST.get('sepal_width'))
        petal_length = float(request.POST.get('petal_length'))
        petal_width = float(request.POST.get('petal_width'))

        # Unpickle model
        iris_model = load_model('iris_model.pickle')
        
        # Make prediction
        result = iris_model.predict([[sepal_length, sepal_width, petal_length, petal_width]])

        classification = result[0]

        IrisPredResults.objects.create(sepal_length=sepal_length, sepal_width=sepal_width, petal_length=petal_length,
                                   petal_width=petal_width, classification=classification)

        return JsonResponse({'result': classification, 'sepal_length': sepal_length,
                             'sepal_width': sepal_width, 'petal_length': petal_length, 'petal_width': petal_width},
                            safe=False)

def view_results(request):
    return render(request, 'results.html')

def view_iris_results(request):
    # Submit prediction and show all
    data = {"dataset": IrisPredResults.objects.all()}
    return render(request, "iris_results.html", data)

def view_life_style_results(request):
    data = {"dataset": LifeStylePredResults.objects.all()}
    return render(request, "life_style_results.html", data)

def symbol_preprocess(text):
    text = text.replace('\\n', '')
    text = unicodedata_full2half(text)           # 全形轉半形
    # text = re.sub(r'([^\w\n\\])', r' \1 ', text) # add symbol space
    # text = re.sub(r'([^\w\\n\-\+])', r' ', text) # remove symbol
    # text = text.replace('\\n', ' ')  # accuracy 會降低
    text = ''.join([' ' + ch + ' ' if not ch.isalpha() and not ch.isdigit() else ch for ch in text])
    # text = ''.join([' ' if not ch.isalpha() and not ch.isdigit() and not ch in ('+', '-') else ch for ch in text])
    text = ''.join([' ' if not ch.isalpha() and not ch.isdigit() and not ch in ('+', '-', '\n') else ch for ch in text])
    
    # 定義中文字的正則表達式
    chinese_pattern = re.compile(r'([\u4e00-\u9fff]+)')

    # 將中文字前後增加空格
    text = chinese_pattern.sub(r' \1 ', text)
    
    text = re.sub(r'\s{2,}', ' ', text)
    
#     doc = nlp(text)
#     text = [token.lemma_.lower() for token in doc]
#     text = [token for token in text if token not in STOPLIST]
    
    return text.strip()

def unicodedata_full2half(text):
    return unicodedata.normalize("NFKC", text)
