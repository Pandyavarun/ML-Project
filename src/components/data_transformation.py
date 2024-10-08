import sys
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline  

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path =os.path.join('artifacts', 'preprocessor.pkl')

class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()
    
    def get_data_transformer_object(self):
        '''
        This method is used to get the data transformation object
        '''
        logging.info("Initiating data transformation")
        try:
            df = pd.read_csv('notebook\data\stud.csv')
            logging.info("Read dataset as DataFrame")
            
            # Preprocessing pipeline
            num_features = ["writing_score", "reading_score"]
            cat_features = ["gender", "race_ethnicity", "parental_level_of_education", "lunch", "test_preparation_course"]

            num_pipeline = Pipeline(
                steps=[
                    ('imputer', SimpleImputer(strategy='median')),
                    ('scaler', StandardScaler(with_mean=False))
                ]
            )
            cat_pipeline = Pipeline(
                steps=[
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('one_hot_encoder', OneHotEncoder()),
                    ('scaler', StandardScaler(with_mean=False))
                ]
            )
            logging.info("Numerical columns standard scaled")
            logging.info("Categorical columns encoded")

            logging.info(f"Categorical columns: {cat_features}")
            logging.info(f"Numerical columns: {num_features}") 
            
            preprocessor = ColumnTransformer(
                transformers=[
                    ('num_pipeline', num_pipeline, num_features),
                    ('cat_pipeline', cat_pipeline, cat_features)
                ]
            )

            return preprocessor
        except Exception as e:
            raise CustomException(e, sys)
    
    
    def initiate_data_transformation(self, train_path, test_path):
        '''
        This method is used to initiate data transformation
        '''
        try:
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)

            logging.info("Read train and test dataset as DataFrame")
            logging.info("Obtaining preprocessor object")

            preprocessing_obj = self.get_data_transformer_object()

            target_column_name = "math_score"
            num_features = ["writing_score", "reading_score"]

            input_feature_train_df = train_df.drop(columns=[target_column_name], axis=1)
            target_feature_train_df = train_df[target_column_name]

            input_feature_test_df = test_df.drop(columns=[target_column_name], axis=1)
            target_feature_test_df = test_df[target_column_name]

            logging.info(f"applying preprocessor object on train and test dataset")

            input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)

            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]
            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            logging.info(f"Saved preprocessing object at {self.data_transformation_config.preprocessor_obj_file_path}")

            save_object(
                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessing_obj
            )

            return(
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path,
            )
            
        
        
        except Exception as e:
            raise CustomException(e, sys)