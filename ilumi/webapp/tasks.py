from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.metrics import classification_report
from sklearn import svm
from webapp.application import database
from webapp.constants import STOPWORDS
from nltk.tokenize import word_tokenize
from bson.binary import Binary
import time
import nltk
import random
import pickle


def pre_processing_tfidf(stemmer, train_labels, documents, category):
    all_ = []
    for document in documents:
        words = word_tokenize(document.get('conteudo', ''))
        if not words:
            continue
        train_labels.append(category)
        procd_words = [w for w in words if w not in STOPWORDS]
        all_.append([procd_words])
    return train_labels, all_


def pre_processing(stemmer, documents, noticias, category):
    all_ = []
    for document in noticias:
        words = word_tokenize(document.get('conteudo', '').lower())
        if not words:
            continue
        documents.append((document.get('conteudo', '').lower(), category))
        [all_.append(w) for w in words if w not in STOPWORDS]
    return documents, all_


def nlp_train_data():
    stemmer = nltk.stem.RSLPStemmer()

    def find_features(document):
        words = word_tokenize(document)
        features = {}
        for w in word_features:
            features[w] = (w in words)

        return features
    _pos = database.items['noticias'].find({'positiva':  True})
    _neg = database.items['noticias'].find({'positiva':  False})
    _neutral = database.items['noticias'].find({'neutro':  True})

    all_words = []
    documents = []

    documents, all_pos = pre_processing(stemmer, documents, _pos, 'pos')
    documents, all_neg = pre_processing(stemmer, documents, _neg, 'neg')
    documents, all_neutral = pre_processing(
        stemmer, documents, _neutral, 'neutral')

    doc_pickle = pickle.dumps(documents)
    database.traindata['dumps'].insert_one({
        'train_id': 1,
        'documents': Binary(doc_pickle)})

    all_words = all_pos + all_neg + all_neutral
    all_words = nltk.FreqDist(all_words)

    words_count = all_words.most_common(1000)[100:]
    word_features = [word for (word, count) in words_count]
    # word_features = list(all_words.keys())[:3000]
    word_pickle = pickle.dumps(word_features)
    database.traindata['dumps'].update_one(
        {'train_id': 1},
        {'$set': {'word_features': Binary(word_pickle)}})

    featuresets = [(find_features(rev), category) for (rev, category) in documents]  # noqa
    random.shuffle(featuresets)

    testing_perc = int(0.4 * len(featuresets))

    testing_set = featuresets[:testing_perc]
    training_set = featuresets[testing_perc:]

    classifier = nltk.NaiveBayesClassifier.train(training_set)
    bayes_acc = nltk.classify.accuracy(classifier, testing_set)
    print('Bayes acc: ' + str(bayes_acc))

    LinearSVC_classifier = SklearnClassifier(svm.SVC(kernel='linear'))
    LinearSVC_classifier.train(training_set)
    linear_acc = nltk.classify.accuracy(LinearSVC_classifier, testing_set)
    print('SVM Linear acc: ' + str(linear_acc))

    RBFSVC_classifier = SklearnClassifier(svm.SVC(kernel='rbf'))
    RBFSVC_classifier.train(training_set)
    rbf_acc = nltk.classify.accuracy(RBFSVC_classifier, testing_set)
    print('RBF SVC acc: ' + str(rbf_acc))

    bayes_pickle = pickle.dumps(classifier)
    database.traindata['dumps'].update_one(
        {'train_id': 1},
        {'$set': {'naive_bayes': Binary(bayes_pickle)}}, upsert=True)

    linear_svc_pickle = pickle.dumps(LinearSVC_classifier)
    database.traindata['dumps'].update_one(
        {'train_id': 1},
        {'$set': {'linear_svc': Binary(linear_svc_pickle)}}, upsert=True)

    rbf_pickle = pickle.dumps(RBFSVC_classifier)
    database.traindata['dumps'].update_one(
        {'train_id': 1},
        {'$set': {'rbf_svc': Binary(rbf_pickle)}}, upsert=True)


def train_data_tfidf(database):
    stemmer = nltk.stem.RSLPStemmer()

    _pos_train = database.items['noticias'].find(
        {'positiva':  True, 'testing': {'$exists': False}})
    _neg_train = database.items['noticias'].find(
        {'positiva':  False, 'testing': {'$exists': False}})
    _neutral_train = database.items['noticias'].find(
        {'neutro':  True, 'testing': {'$exists': False}})

    _pos_test = database.items['noticias'].find(
        {'positiva':  True, 'testing': True})
    _neg_test = database.items['noticias'].find(
        {'positiva':  False, 'testing': True})
    _neutral_test = database.items['noticias'].find(
        {'neutro':  True, 'testing': True})

    train_labels = []
    train_labels, all_pos_train = pre_processing_tfidf(
        stemmer, train_labels, _pos_train, 'pos')
    train_labels, all_neg_train = pre_processing_tfidf(
        stemmer, train_labels, _neg_train, 'neg')
    train_labels, all_neutral_train = pre_processing_tfidf(
        stemmer, train_labels, _neutral_train, 'neutral')

    test_labels = []
    test_labels, all_pos_test = pre_processing_tfidf(
        stemmer, test_labels, _pos_test, 'pos')
    test_labels, all_neg_test = pre_processing_tfidf(
        stemmer, test_labels, _neg_test, 'neg')
    test_labels, all_neutral_test = pre_processing_tfidf(
        stemmer, test_labels, _neutral_test, 'neutral')

    vectorizer = TfidfVectorizer(
        min_df=5, max_df=0.8, sublinear_tf=True,
        use_idf=True, decode_error='ignore')

    train_data = all_pos_train + all_neg_train + all_neutral_train
    test_data = all_pos_test + all_neg_test + all_neutral_test

    train_vectors = vectorizer.fit_transform(train_data)
    test_vectors = vectorizer.transform(test_data)

    # Perform classification with SVM, kernel=linear
    classifier_linear = svm.SVC(kernel='linear')
    t0 = time.time()
    classifier_linear.fit(train_vectors, train_labels)
    t1 = time.time()
    prediction_linear = classifier_linear.predict(test_vectors)
    t2 = time.time()
    time_linear_train = t1-t0
    time_linear_predict = t2-t1

    # Perform classification with SVM, kernel=linear
    classifier_rbf = svm.SVC(kernel='rbf')
    t0 = time.time()
    classifier_rbf.fit(train_vectors, train_labels)
    t1 = time.time()
    prediction_rbf = classifier_rbf.predict(test_vectors)
    t2 = time.time()
    time_rbf_train = t1-t0
    time_rbf_predict = t2-t1

    print("Training time RBF: %fs;" % (time_rbf_train))
    print("Training time Linear: %fs;" % (time_linear_train))

    # Print results in a nice table
    print("Results for SVC(kernel=rbf)")
    print("Training time: %fs; Prediction time: %fs" % (
        time_rbf_train, time_rbf_predict))
    print(classification_report(test_labels, prediction_rbf))
    print("Results for SVC(kernel=linear)")
    print("Training time: %fs; Prediction time: %fs" % (
        time_linear_train, time_linear_predict))
    print(classification_report(test_labels, prediction_linear))
