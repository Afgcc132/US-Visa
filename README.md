-Proyecto de Programación para practicar MLOPS

#git commands
'''
git add. 

git commit -m "Initial commit"

git push origin main
'''

mongodb+srv://afgcc132_db_user:EBmg5X3VKtwEhB7c@cluster0.zv2f9bv.mongodb.net/?appName=Cluster0


#workflow
1. constants
2. Entity   
3. component
4. pipeline
5. main_file 



### Data Ingestion
- Data Ingestion: it is a class that is used to ingest data from the mongodb database to the feature store.
- Steps:
    1. Connect to the mongodb database
    2. Extract the data from the mongodb database
    3. Store the data in the feature store
    4. Split the data into train and test
    5. Save the train and test data
    6. Return the train and test data


### Data Validation
- Data Validation: it is a class that is used to validate the data from the feature store.
- Steps:
    1. Connect to the feature store
    2. Extract the data from the feature store
    3. Validate the data
    4. Store the validated data
    5. Return the validated Data


### Data Transformation
- Data Transformation: it is a class that is used to transform the data from the feature store.
- Steps:
    1. Connect to the feature store
    2. Extract the data from the feature store
    3. Transform the data
    4. Store the transformed data
    5. Return the transformed data


### Model Trainer
- Model Trainer: it is a class that is used to train the model from the feature store.
- Steps:
    1. Connect to the feature store
    2. Extract the data from the feature store
    3. Train the model
    4. Store the trained model
    5. Return the trained model


798644228622.dkr.ecr.us-east-2.amazonaws.com/usvisa-app

