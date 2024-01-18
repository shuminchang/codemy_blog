from django.db import models


class IrisPredResults(models.Model):

    sepal_length = models.FloatField()
    sepal_width = models.FloatField()
    petal_length = models.FloatField()
    petal_width = models.FloatField()
    classification = models.CharField(max_length=30)

    def __str__(self):
        return self.classification
    
class LifeStylePredResults(models.Model):

    emr_text = models.TextField()
    processed_text = models.TextField()
    classification = models.CharField(max_length=30)

    def __str__(self):
        return self.classification