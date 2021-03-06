import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import pandas as pd
import fire
import numpy as np
from utility.singleton_logger import SingletonLogger
import mlflow
from google.cloud import storage

client = storage.Client()
logger = SingletonLogger.get_logger()
metrics_info = {'metrics': []}


def train_model(dataset_path, original_dataset_path, n_estimators, criterion, min_samples_leaf, random_state):
    """
    Trains a Random Forest Regressor model and save it on the MLFlow Model Registry.
    :param dataset_path: The path of the dataset to be used for the training.
    :param original_dataset_path: The path of the dataset before the data preparation phase.
    :param n_estimators: the number of estimators for the regression model.
    :param criterion: The function to measure the quality of a split.
    :param min_samples_leaf: The minimum number of samples required to be at a leaf node.
    :param random_state: Controls both the randomness of the bootstrapping of the samples used when building trees
    """
    model_name = "random_forest_regressor"
    dataset = pd.read_csv(dataset_path).set_index('time')
    x_training_set, y_training_set = __split_into_x_y(dataset)
    x_test_set, y_test_set = __split_into_x_y(dataset)
    experiment = __get_mlflow_experiment(model_name)

    with mlflow.start_run(experiment_id=experiment.experiment_id):
        mlflow.set_experiment(model_name)
        __log_parameter("Original Dataset", original_dataset_path)

        model = __get_model(n_estimators, criterion, min_samples_leaf, random_state)
        logger.info("Training started")
        model.fit(x_training_set, y_training_set)
        logger.info("Training finished")

        y_test_pred = model.predict(x_test_set)
        rmse = np.sqrt(mean_squared_error(y_test_pred, y_test_set))
        __log_metric("rmse", rmse)
        __save(model, model_name)


def __save(model, name):
    """
    Logs a model in the MLFlow Model Registry
    :param model: The model to be saved
    :param name: The name that will be uset to save the model
    """
    mlflow.sklearn.log_model(model, artifact_path=name, registered_model_name=name)
    logger.info("Model saved")


def __log_parameter(name, value):
    """
    Logs a parmeter in the MLFlow server
    :param name - The name of the parameter
    :param value - The value of the parameter
    """
    logger.info(name + ": " + str(value))
    mlflow.log_param(name, value)


def __log_metric(name, value):
    """
    Logs a metric in the MLFlow server
    :param name - The name of the metric
    :param value - The value of the metric
    """
    logger.info(name + ": " + str(value))
    mlflow.log_metric(name, value)
    __save_metric_to_file(name, value)


def __save_metric_to_file(name, value):
    global metrics_info
    metrics_info['metrics'].append({
            'name': name,
            'value': float(value)
        })
    with open('/tmp/metrics.json', 'w') as metrics_file:
        json.dump(metrics_info, metrics_file)

    metric_file_path = '/tmp/' + name
    with open(metric_file_path, 'w') as value_file:
        value_file.write(str(value))


def __get_mlflow_experiment(name):
    """
    Get an experiment from the MLFlow server
    :param name - The name of the experiment
    """
    if not mlflow.get_experiment_by_name(name):
        mlflow.create_experiment(name=name)
    return mlflow.get_experiment_by_name(name)


def __get_model(n_estimators, criterion, min_samples_leaf, random_state):
    return RandomForestRegressor(
        n_estimators=n_estimators,
        criterion=criterion,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
        verbose=True,
        n_jobs=4
    )


def __split_into_x_y(data):
    target_col = "load"
    x = data.drop(columns=target_col)
    y = data.loc[:, target_col]
    logger.info("Data splitted into x and y")
    return x, y


if __name__ == "__main__":
    fire.Fire(train_model)
