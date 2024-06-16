from django.apps import AppConfig
import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class PredictConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predict'

    def ready(self):
        global iris_model, life_style_model
        iris_model_path = os.path.join(self.path, 'iris_model.pickle')
        life_style_model_path = os.path.join(self.path, 'life_style_en_model_20231221.pkl')

        try:
            iris_model = pd.read_pickle(iris_model_path)
            life_style_model = pd.read_pickle(life_style_model_path)
            logger.info("Models loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
