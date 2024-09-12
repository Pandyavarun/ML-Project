import os
import sys
from dataclasses import dataclass

from catboost import CatBoostRegressor
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
)
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor

from src.exception import CustomException
from src.logger import logging  
from src.utils import save_object, evaluate_models

@dataclass
class ModelTrainerConfig:
    model_obj_file_path: str=os.path.join('artifacts', 'model.pkl')

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()
    
    def initiate_model_training(self,train_array,test_array):
        try:
            logging.info("Initiating model training")
            X_train, y_train, X_test, y_test = (
                train_array[:,:-1],
                train_array[:,-1],
                test_array[:,:-1],
                test_array[:,-1],
            )

            models = {
                "Linear Regression": LinearRegression(),
                "Random Forest": RandomForestRegressor(),
                "Gradient Boosting": GradientBoostingRegressor(),
                "Ada Boost Classifier": AdaBoostRegressor(),
                "K-Neighbors Classifier": KNeighborsRegressor(),
                "Decision Tree": DecisionTreeRegressor(),
                "XGBRegressor": XGBRegressor(),
                "CatBoosting Classifier": CatBoostRegressor(),
            }

            model_report: dict = evaluate_models(X_train=X_train, y_train=y_train,X_test = X_test, y_test = y_test, models=models)

            best_model_score = max(sorted(model_report.values()))

            best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]

            best_model = models[best_model_name]

            if best_model_score < 0.6:
                raise CustomException("No best model found")
            

            logging.info(f"Best model: {best_model_name}")

            save_object(
                file_path=self.model_trainer_config.model_obj_file_path,
                obj=best_model
            )

            predicted = best_model.predict(X_test)
            r2_square = r2_score(y_test, predicted)
            return r2_square
           

        except Exception as e:
            raise CustomException(e, sys)