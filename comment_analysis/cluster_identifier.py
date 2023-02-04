import pandas as pd
from pandas import json_normalize
import json
import numpy as np
import time
import cohere
from math import ceil
from sklearn.cluster import DBSCAN


class ClusterIdentifier:

    _api_key = 'f1DZIoFirHG7l5CcbCyvF0J3ADU5pdlVBLZ7I1va'

    def __init__(self):
        self._cohere = cohere.Client(self._api_key)
        self._data = None
        self._data_frame = None
        self._all_comments = None
        self._top_level_comments = None
        self._replies = None
        self._embedded_comments = None
        self._clustered_comments = {}

    def _identify_clusters(self):
        """
        Identify clusters of comments using DBSCAN
        :return:
        """
        variable_eps = len(self._embedded_comments) / 500
        variable_samples = round(len(self._embedded_comments) / 80)

        self._clusters = DBSCAN(eps=variable_eps, min_samples=variable_samples, metric='cosine').fit(self._embedded_comments)
        self._num_clusters = max(self._clusters.labels_.tolist())

    def _determine_cluster_comments(self):
        """
        Determine which comments belong to which cluster
        :return:
        """
        for cluster_id in set(self._clusters.labels_):
            self._clustered_comments[str(cluster_id)] = []

        for comment_cluster, comment_id in zip(self._clusters.labels_, self._all_comment_ids):
            self._clustered_comments[str(comment_cluster)].append(comment_id)

    def analyze_comments(self, comments):
        self._process_comments(comments=comments)
        self._generate_comments_embeddings()
        self._identify_clusters()
        self._determine_cluster_comments()
        return self._clustered_comments

    def _process_comments(self, comments):
        df = pd.DataFrame(columns=['author', 'text', 'comment_id', 'parent_comment_id', 'like_count'])

        for comment in comments:
            for k, v in comment.items():
                row = {
                    'author': v['author'],
                    'text': v['text'],
                    'comment_id': k
                }
                tdf = pd.DataFrame([row])
                df = pd.concat([df, tdf], ignore_index=True, axis=0)

                if 'replies' in v.keys():
                    for kk, vv in v['replies'].items():
                        comment_id = kk.replace(k, '').replace('.', '')
                        row = {
                            'author': vv['author'],
                            'text': vv['text'],
                            'comment_id': comment_id,
                            'parent_comment_id': k,
                            'like_count': vv['like_count']
                        }
                        tdf = pd.DataFrame([row])
                        df = pd.concat([df, tdf], ignore_index=True, axis=0)

        # truncate very large texts to the max length of 4096
        df['text'] = df['text'].apply(lambda x: x[:4096])

        # save attributes to object
        self._data_frame = df
        self._all_comments = self._data_frame['text'].tolist()
        self._all_comment_ids = self._data_frame['comment_id'].tolist()
        self._top_level_comments = df[~df['comment_id'].isna()]
        self._replies = df[~df['parent_comment_id'].isna()]

    def _generate_comments_embeddings(self):
        """
        Embed comments using the cohere API
        :return:
        """
        self._embedded_comments = self._cohere.embed(self._data_frame['text'].values.tolist()).embeddings

    def get_number_of_clusters(self):
        return self._num_clusters

    def get_cluster_comments(self, cluster_id):
        return self._clustered_comments[cluster_id]
