import tornado.escape
import tornado.web
from nltk.tokenize import word_tokenize
from webapp.application import database
from webapp.classification import SentiClassifier
import pickle


class GetEndpoint(tornado.web.RequestHandler):
    def send(self, data):
        self.set_header('Content-Type', 'application/json')
        self.write(tornado.escape.json_encode(data))

    def post(self):
        data_json = tornado.escape.json_decode(self.request.body)
        noticias_individuo = database.items['noticias'].find(
            {'individuo': data_json['individuo'],
             'sentimento': {'$exists': True}})
        self.send({
            'result': noticias_individuo
        })


class IndividuoEndpoint(tornado.web.RequestHandler):

    def send(self, data):
        self.set_header('Content-Type', 'application/json')
        self.write(tornado.escape.json_encode(data))

    def post(self):
        data_json = tornado.escape.json_decode(self.request.body)
        pickle_data = database.traindata['dumps'].find_one({'train_id': 1})
        word_features = pickle.loads(pickle_data['word_features'])
        BAYES = pickle.loads(pickle_data['naive_bayes'])
        LINEAR_SVC = pickle.loads(pickle_data['linear_svc'])
        RBF_SVC = pickle.loads(pickle_data['rbf_svc'])

        senti_classifier = SentiClassifier(BAYES, LINEAR_SVC, RBF_SVC)

        def find_features(document):
            words = word_tokenize(document.lower())
            features = {}
            for w in word_features:
                features[w] = (w in words)

            return features

        noticias_individuo = database.items['noticias'].find(
            {'individuo': 'Renan Calheiros',
             '$or': [
                 {'positiva': {'$exists': False}},
                 {'negativa': {'$exists': False}},
                 {'neutro': {'$exists': False}}]})

        for noticia in list(noticias_individuo):
            if noticia.get('conteudo', ''):
                feat = find_features(noticia['conteudo'])
                senti = senti_classifier.classify(feat)
                database.items.noticias.update_one(
                    {'titulo': noticia['titulo']},
                    {'$set': {'sentiment': senti}})

        self.send({
            'total': noticias_individuo.count()
        })
