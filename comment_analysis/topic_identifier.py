import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim import corpora


class TopicIdentifier:
    """
    This class is used to identify topics in a set of texts. It uses the LDA (Latent Dirichlet Allocation) model.

    Attributes:
        _texts: list of texts
        _processed_texts: list of texts after processing
        _dictionary: dictionary of words
        _doc_term_matrix: list of tuples (word_id, word_count)
        _num_topics: number of topics to identify
        _lda_model: LDA (Latent Dirichlet Allocation) model used to identify topics
    """

    def __init__(self, texts=None):
        if texts is not None:
            self._texts = texts
            self._processed_texts = self._process_clean_texts()
            self._create_dictionary()
            self._create_lda_model()

    def __call__(self, texts):
        self._texts = texts
        self._processed_texts = self._process_clean_texts()
        self._create_dictionary()
        self._create_lda_model()

    def _process_clean_texts(self):
        """
        Process and cleans the texts by removing stopwords and punctuation
        :returns list of processed texts
        """
        processed_texts = []
        for text in self._texts:
            words = simple_preprocess(text)
            processed_texts.append([word for word in words if word not in STOPWORDS])
        return processed_texts

    def _create_dictionary(self):
        """
        Creates a dictionary of words from the processed texts
        :return: None
        """
        self._dictionary = corpora.Dictionary(self._processed_texts)
        self._doc_term_matrix = [self._dictionary.doc2bow(text) for text in self._processed_texts]

    def _create_lda_model(self, num_topics=5):
        """
        Creates the LDA model with the specified number of topics
        :param num_topics: number of topics to identify in the texts
        :return: None
        """
        self._num_topics = num_topics
        self._lda_model = gensim.models.LdaMulticore(self._doc_term_matrix
                                                         , num_topics=num_topics
                                                         , id2word=self._dictionary
                                                         , passes=50
                                                         , workers=2
                                                     )

    def set_texts(self, texts):
        self._texts = texts
        self._processed_texts = self._process_clean_texts()
        self._create_dictionary()
        self._create_lda_model()

    def identify_topics(self, num_topics=5):
        """
        Re-creates the LDA model with the specified number of topics
        :param num_topics: number of topics to identify in the texts
        :return: None
        """
        self._create_lda_model(num_topics)

    def extract_topics(self, num_words=5):
        """
        Extracts a number of topics which is specified by the num_topics parameter
        :param num_words: number of words to extract for each topic
        :return: dictionary of topics
        """
        topics = {}
        for topic_id, topic in self._lda_model.print_topics(num_topics=self._num_topics, num_words=num_words):
            topics[topic_id] = topic
        return topics
