import os
import numpy as np
import pandas as pd
import math
from sklearn import cross_validation as cv
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.metrics import mean_squared_error
from math import sqrt
from .DAO import restart_csv

def predict(ratings, similarity, type='event'):
    if type == 'event':
        mean_user_rating = ratings.mean(axis=1)
        #You use np.newaxis so that mean_user_rating has same format as ratings
        ratings_diff = (ratings - mean_user_rating[:, np.newaxis])
        pred = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array([np.abs(similarity).sum(axis=1)]).T
    elif type == 'item':
        pred = ratings.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])
    return pred

def rmse(prediction, ground_truth):
    prediction = prediction[ground_truth.nonzero()].flatten()
    ground_truth = ground_truth[ground_truth.nonzero()].flatten()
    return sqrt(mean_squared_error(prediction, ground_truth))

def matrix_pos_assign(col):
    pos = 0
    result = {}
    for i in range(len(col)):
        tmp = col[i]
        if tmp not in result and not math.isnan(tmp):
            result[int(tmp)] = pos
            pos = pos + 1
    return result

class Recomender:
    """
    Inicialización de la clase recomendador
    """
    def __init__(self, **kwargs):
        restart_csv()
        if "csv" not in kwargs:
            self.csv_path = os.path.abspath("events/csv/event_recommender.csv")
        else:
            self.csv_path = os.path.abspath(kwargs["csv"])
        
        header = ['event_id', 'user_signedUp_id', 'views']
        self.df = pd.read_csv(self.csv_path, sep=',', names=header)
        self.n_events = self.df["event_id"].nunique()
        """
        if(self.df["event_id"].values.any()):
            self.n_events =  self.n_events-1
        """
        self.n_items = self.df["user_signedUp_id"].nunique()
        """
        if(self.df["user_signedUp"].values.any()):
            self.n_items =  self.n_items-1
        """
    def toString(self):
        return str('Numero de eventos:' + str(self.n_events) + '\n\n Numero de usuarios que asisten al menos a algun evento:' + str(self.n_items))

    def train(self):
        train_data, test_data = cv.train_test_split(self.df, test_size=0.25)
        #Create two user-item matrices, one for training and another for testing
        train_data_matrix = np.zeros((self.n_events, self.n_items))

        user_signedUp_id_pos = matrix_pos_assign(self.df["user_signedUp_id"])
        event_id_pos = matrix_pos_assign(self.df["event_id"])

        print(train_data)
        for line in train_data.itertuples():
            if not math.isnan(line[2]):
                train_data_matrix[event_id_pos[int(line[1])],user_signedUp_id_pos[int(line[2])]] = int(line[3])

        print(train_data_matrix)
        test_data_matrix = np.zeros((self.n_events, self.n_items))
        for line in test_data.itertuples():
            if not math.isnan(line[2]):
                test_data_matrix[event_id_pos[int(line[1])],user_signedUp_id_pos[int(line[2])]] = int(line[3])
        
        event_similarity = pairwise_distances(train_data_matrix, metric='cosine')
        item_similarity = pairwise_distances(train_data_matrix.T, metric='cosine')

        item_prediction = predict(train_data_matrix, item_similarity, type='item')
        event_prediction = predict(train_data_matrix, event_similarity, type='event')
        
        print("posicion de evento",event_id_pos[6])
        print("info de la matrix para el evento 6",train_data_matrix[event_id_pos[6]])

        print('Event-based CF RMSE: ' + str(rmse(event_prediction, test_data_matrix)))
        print('Item-based CF RMSE: ' + str(rmse(item_prediction, test_data_matrix)))