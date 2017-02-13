
from nltk.classify import ClassifierI
from statistics import mode


class SentiClassifier(ClassifierI):

    def __init__(self, *classifiers):
        self._classifiers = classifiers

    def classify(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)
        try:
            return mode(votes)
        except:
            return votes[-1]

    def confidence(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)

        choice_votes = votes.count(mode(votes))
        conf = choice_votes / len(votes)
        return conf


    # def classify(self, features):
    #     votes = []
    #     for c in self._classifiers:
    #         v = c.classify(features)
    #         votes.append(v)
    #     return max(set(votes), key=votes.count)
    #
    # def confidence(self, features):
    #     votes = []
    #     for c in self._classifiers:
    #         v = c.classify(features)
    #         votes.append(v)
    #
    #     mode = max(set(votes), key=votes.count)
    #     choice_votes = votes.count(mode)
    #     conf = choice_votes / len(votes)
    #     return conf
