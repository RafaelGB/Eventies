import os
import numpy as np
import pandas as pd
import math
from sklearn import cross_validation as cv
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.metrics import mean_squared_error
from math import sqrt
from .DAO import restart_csv
from .models import MyRecommender

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
    colList = []
    for i in range(len(col)):
        tmp = col[i]
        if tmp not in result and not math.isnan(tmp):
            colList.append(int(tmp))
            result[int(tmp)] = pos
            pos = pos + 1
    return result,colList

class Recomender:
    """
    Inicialización de la clase recomendador
    """
    def __init__(self, **kwargs):
        """
                ZONA DE CHEQUEO DE ARGUMENTOS DE ENTRADA
                ........................................
            csv : para pasar por parametro la path de destino
                  POR DEFECTO: events/csv/event_recommender.csv
            
            verbose : para indicar si se quiere información por consola
                      POR DEFECTO: verbose=False
        """

        if "csv" not in kwargs:
            self.csv_path = os.path.abspath("events/csv/event_recommender.csv")
        else:
            self.csv_path = os.path.abspath(kwargs["csv"])
        if "verbose" in kwargs and isinstance(kwargs["verbose"], bool):
            self.verbose=kwargs["verbose"]
        else:
            self.verbose=False
        """
                FIN DE ZONA DE CHEQUEO DE ARGUMENTOS DE ENTRADA
        """
        #creamos o modificamos csv
        restart_csv(self.csv_path)
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
    def info(self):
        return str('Numero de eventos:' + str(self.n_events) + '\n\n Numero de usuarios que asisten al menos a algun evento:' + str(self.n_items))

    def train(self):
        #------------------------matrices------------------------

        train_data_matrix = np.zeros((self.n_events, self.n_items))
        test_data_matrix = np.zeros((self.n_events, self.n_items))

        #------------------------datos de usuario------------------------

        user_signedUp_id_pos, unique_user_ids= matrix_pos_assign(self.df["user_signedUp_id"])

        dictRecommenders = {}
        for x in unique_user_ids:
            dictRecommenders[x]=[]
        #------------------------datos de evento------------------------

        event_id_pos, unique_event_ids= matrix_pos_assign(self.df["event_id"])

        #------------------------creación de datasets con crossvalidation------------------------
        train_data, test_data = cv.train_test_split(self.df, test_size=0.25)

        if self.verbose:
            print("para la lista de ids de eventos:"+str(unique_event_ids))
            print("para la lista de ids de users:"+str(unique_user_ids))
            print(train_data)

        for line in train_data.itertuples():
            if not math.isnan(line[2]):
                train_data_matrix[event_id_pos[int(line[1])],user_signedUp_id_pos[int(line[2])]] = int(line[1])

        if self.verbose:
            print(train_data_matrix)


        for line in test_data.itertuples():
            if not math.isnan(line[2]):
                test_data_matrix[event_id_pos[int(line[1])],user_signedUp_id_pos[int(line[2])]] = int(line[1])
        
        event_similarity = pairwise_distances(train_data_matrix, metric='cosine')
        item_similarity = pairwise_distances(train_data_matrix.T, metric='cosine')

        item_prediction = predict(train_data_matrix, item_similarity, type='item')
        event_prediction = predict(train_data_matrix, event_similarity, type='event')

        #ejemplos
        """
        if self.verbose:
            print('Event-based CF RMSE: ' + str(rmse(event_prediction, test_data_matrix)))
            print('Item-based CF RMSE: ' + str(rmse(item_prediction, test_data_matrix)))
        """
        
        for event_id in unique_event_ids:
            event_pos = event_id_pos[event_id]
            row = train_data_matrix[event_id_pos[event_id],:]
            tmpArray = []
            recommended_events=[]
            for index,elem in enumerate(row):
                if int(elem)>0:
                    tmpArray.append(index)
                    recommended_events.append(int(elem))
            if len(tmpArray)>1:
                for index,(posUser,idEvent) in enumerate(zip(tmpArray,recommended_events)):
                    tmpArrayReduce = tmpArray
                    tmpArrayReduce.remove(posUser)
                    for j in tmpArrayReduce:
                        col = train_data_matrix[:,posUser]
                        for y in col:
                            if y>0 and y and y != idEvent not in dictRecommenders[unique_user_ids[posUser]]:
                                dictRecommenders[unique_user_ids[posUser]].append(int(y))
        if self.verbose:
            print(dictRecommenders)

        for key, value in dictRecommenders.items():
            print(value)
            tmpRecommender = MyRecommender(user=int(key),id_events=value)
            tmpRecommender.save()

    def getRecommendedEvents(self,myId):
        myObject = MyRecommender.objects.get(user=myId)
        print(str(myObject.id_events))

        
                

