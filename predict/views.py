from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
from .models import PredResults
import unicodedata
import re

def prediction_page(request):
    return render(request, 'predict.html')

def life_style_page(request):
    return render(request, 'life_style.html')

def life_style(request):
    # return render(request, 'life_style.html')

    if request.POST.get('action') == 'post':

        emr_text = str(request.POST.get('emr_text'))
        processed_text = symbol_preprocess(emr_text)

        test_model = pd.read_pickle(r"life_style_en_model_20231221.pkl")
        test_doc = test_model(processed_text)
        predict_cat = max(test_doc.cats, key=test_doc.cats.get)

        return JsonResponse({'result': predict_cat, 'emr_text': processed_text},
                            safe=False)

def iris(request):

    if request.POST.get('action') == 'post':

        # Receive data from client
        sepal_length = float(request.POST.get('sepal_length'))
        sepal_width = float(request.POST.get('sepal_width'))
        petal_length = float(request.POST.get('petal_length'))
        petal_width = float(request.POST.get('petal_width'))

        # Unpickle model
        model = pd.read_pickle(r"/media/shumin/ssd2T/github/codemy_blog/codemy_blog/new_model.pickle")
        # Make prediction
        result = model.predict([[sepal_length, sepal_width, petal_length, petal_width]])

        classification = result[0]

        PredResults.objects.create(sepal_length=sepal_length, sepal_width=sepal_width, petal_length=petal_length,
                                   petal_width=petal_width, classification=classification)

        return JsonResponse({'result': classification, 'sepal_length': sepal_length,
                             'sepal_width': sepal_width, 'petal_length': petal_length, 'petal_width': petal_width},
                            safe=False)
    
def view_results(request):
    # Submit prediction and show all
    data = {"dataset": PredResults.objects.all()}
    return render(request, "results.html", data)

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