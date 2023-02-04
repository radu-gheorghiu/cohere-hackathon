import pinecone

# API key for Pinecone Vector DB
API_KEY = "YOUR_API_KEY"
# GCP environment zone
ENVIRONMENT = "us-east1-gcp"


class PineconeClient:
    def __init__(self, index_name):
        """
        Initializes the Pinecone API service and connects to index_name DB
        """
        pinecone.init(API_KEY, environment=ENVIRONMENT)
        self.index = pinecone.Index(index_name)

    def fetch_by_ids(self, ids, namespace):
        """
        Fetches embeddings vectors in the specified namespace.

        Parameters:
            ids (list[str]): list of vector ids to fetch
            namespace (str): namespace to fetch vectors from

        Returns:
            a list of vectors
        """
        fetch_response = self.index.fetch(ids=ids, namespace=namespace)
        return fetch_response

    def save(self, vectors, namespace):
        """
        Saves embeddings vectors in the specified namespace.

        Parameters:
            vectors: list[str, list, dict]
                id (str): vector identifier
                vector (list) - embedded item
                metadata (dict) - dict with item metadata
            namespace (str): namespace to save vectors, usually corresponding video id

        Returns:
            True or False, depending of the success of the call
        """
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            self.index.upsert(vectors=vectors[i : i + batch_size], namespace=namespace)

    def delete(self, namespace, ids, delete_all=False, filters={}):
        """
        Deletes vectors in the specified namespace.

        Parameters:
            namespace(str): the namespace to query
            ids (list[str] | None): list of vector ids to fetch
            delete_all (bool): True or False, specifiec to delete all ids from namespace or not
            filter (dict | None): dictionary with field-value filters

        Returns:
            True or False, depending of the succes of the call
        """
        if delete_all and filters:
            raise Exception("No filter expected when delete_all=true")
        elif delete_all:
            delete_response = self.index.delete(ids=ids, delete_all=delete_all, namespace=namespace)
        elif filters:
            delete_response = self.index.delete(
                ids=ids, delete_all=delete_all, filter=filters, namespace=namespace
            )
        return delete_response

    def query(
        self,
        namespace,
        vector,
        id=None,
        filter={},
        top_k=10,
        include_values=False,
        include_metadata=False,
    ):
        """
        It retrieves the ids of the most similar items in a namespace, along with their similarity scores.

        Parameters:
            namespace (str): The namespace to query.
            vector (list[int]): query vector. This should be the same length as the dimension of the index being queried
            id (str): the unique ID of the vector to be used as a query vector
            filter (dict): The filter to apply on vector metadata to limit the search.
            top_k (int): The number of results to return for each query.
            include_values (bool): indicates whether vector values are included in the response
            include_metadata (bool): indicates whether metadata is included in the response as well as the ids

        Returns:
            The ids of the most similar items in a namespace, along with their similarity scores.
        """
        if vector and id:
            raise Exception("Vector id and vector not allowed in same query")
        elif vector:
            query_response = self.index.query(
                namespace=namespace,
                vector=vector,
                filter=filter,
                top_k=top_k,
                include_values=include_values,
                include_metadata=include_metadata,
            )
        elif id:
            query_response = self.index.query(
                namespace=namespace,
                id=id,
                filter=filter,
                top_k=top_k,
                include_values=include_values,
                include_metadata=include_metadata,
            )
        else:
            raise Exception("Provide id or vector to query")
        query_answers = [answer['id'] for answer in query_response['matches']]
        return query_answers
