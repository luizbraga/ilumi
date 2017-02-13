
import os
import asyncio
import tornado
import tornado.web
import tornado.options
import logging
import nltk
from pymongo import MongoClient


logger = logging.getLogger(__name__)

__all__ = ['database', 'app']


SETTINGS = dict(
    debug=os.environ.get('DEBUG', True),
    compress_response=True,
)

database = MongoClient(
    os.environ.get('DATABASE_URL'),
    connect=False)


from webapp import endpoints  # noqa
from webapp.tasks import nlp_train_data  # noqa
from webapp.classification import SentiClassifier  # noqa
app = tornado.web.Application([
    (r'/obter-noticias', endpoints.GetEndpoint),
    (r'/test-individuo', endpoints.IndividuoEndpoint)
], **SETTINGS)


def runserver():
    tornado.options.parse_command_line()
    logger.info('Installing NLTK Packages')
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('rslp')

    pickle_data = database.traindata['dumps'].find_one({'train_id': 1})
    if not pickle_data:
        nlp_train_data()

    logger.info('NLTK Successfully installed')
    if app.settings.get('debug', False):
        app.listen(address='0.0.0.0', port=5000)
        logger.info('Listening on port 5000')
        tornado.ioloop.IOLoop.instance().start()
    else:
        tornado.platform.asyncio.AsyncIOMainLoop().install()
        app.listen(address='0.0.0.0', port=5000)
        logger.info('Listening on port 5000')
        asyncio.get_event_loop().run_forever()
