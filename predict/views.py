from django.shortcuts import render
from django.http import JsonResponse
import pandas as pd
from .models import PredResults

def prediction_page(request):
    return render(request, 'predict.html')

def predict_chances(request):

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

        print("RESULT")
        print(result)
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