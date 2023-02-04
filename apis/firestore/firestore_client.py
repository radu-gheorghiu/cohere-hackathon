import random
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


CREDENTIALS_FILE = "credentials/firestore-credentials.json"


class FirestoreClient:
    def __init__(self):
        """
        Initializes the Firestore client.
        """
        cred = credentials.Certificate(CREDENTIALS_FILE)
        self.app = firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def get_document_by_id(self, collection, document_id):
        """
        Retrieves a document from a collection by its ID.

        Parameters:
            collection (str): the name of the collection to retrieve from
            document_id (str): a document ID to retrieve

        Returns:
            a list of dictionaries representing the retrieved documents
        """
        doc_ref = self.db.collection(collection).document(document_id)
        doc = doc_ref.get()
        return doc.to_dict()

    def get_documents_by_ids(self, collection, document_ids):
        """
        Retrieves a batch of documents from a collection by document ID.

        Parameters:
            collection (str): the name of the collection to retrieve from
            document_ids (list[str]): a list of document IDs to retrieve

        Returns:
            a list of dictionaries representing the retrieved documents
        """
        collection_ref = self.db.collection(collection)
        docs = [collection_ref.document(document_id).get() for document_id in document_ids]
        return [doc.to_dict() for doc in docs if doc.exists]

    def get_documents_by_filters(self, collection, filters):
        """
        Retrieves documents from a collection that match the specified filters.

        Parameters:
            collection (str): the name of the collection to retrieve from
            filters (list[tuple]): a list of tuples with field name, operator, values to filter by

        Returns:
            a list of dictionaries representing the retrieved documents
        """
        collection_ref = self.db.collection(collection)
        query = collection_ref
        for field, operation, value in filters:
            query = query.where(field, operation, value)
        result = query.get()
        return [doc.to_dict() for doc in result if doc.exists]

    def save_document(self, collection, document):
        """
        Saves a document in a collection.

        Parameters:
            collectionn (str): the name of the collection to save to
            document (dict): a dictionary with key = document id and value a dictionary of data to save to the document
        """
        document_id, document_details = list(document.items())[0]
        doc_ref = self.db.collection(collection).document(document_id)
        doc_ref.set(document_details)

    def save_documents(self, collection, documents):
        """
        Saves documents in a collection.

        Parameters:
            collection (str): the name of the collection to save to
            documents (list[dict]): a list of dictionaries with key = document id and value a dictionary of data to save to the document
        """
        batch_size = 500
        for i in range(0, len(documents), batch_size):
            batch = self.db.batch()
            for document in documents[i : i + batch_size]:
                document_id, document_details = list(document.items())[0]
                doc_ref = self.db.collection(collection).document(document_id)
                batch.set(doc_ref, document_details)
            batch.commit()
