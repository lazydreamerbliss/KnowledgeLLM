import math
import os
import pickle

import numpy as np
from faiss import IndexFlatL2, IndexIDMap2, IndexIVFFlat
from redis.commands.search.document import Document
from tqdm import tqdm


class InMemoryVectorDb:
    """It maintains a vector database (FLAT) in-memory for given image library
    - It needs to persist the index to disk for reuse
    """
    IDX_FILENAME: str = 'mem_db.idx'
    DEFAULT_NEIGHBOR_COUNT: int = 5  # Default number of nearest neighbors to be queried for IVF

    def __init__(self, db_path, index_filename: str | None = None):
        if not db_path:
            raise ValueError('A path is mandatory for using in-memory vector DB')

        tqdm.write(f'Loading index from disk...', end=' ')
        db_path = os.path.expanduser(db_path)
        if not os.path.isdir(db_path):
            raise ValueError('Path does not exist')

        index_filename = index_filename or InMemoryVectorDb.IDX_FILENAME
        index_file_path: str = os.path.join(db_path, index_filename)
        self.mem_index_path: str = index_file_path
        self.id_mapping: dict[int, str] | None = None  # Maintain the mapping of ID to UUID
        self.mem_index_flat: IndexIDMap2 | None = None
        self.mem_index_ivf: IndexIVFFlat | None = None
        self.index_size_since_last_training: int = 0  # TODO: add a timer to retrain the index

        # self.mem_index: IndexIVFFlat | None = None
        if os.path.isfile(index_file_path):
            try:
                obj = pickle.load(open(index_file_path, 'rb'))
                self.id_mapping = obj['id_mapping']  # dict
                self.mem_index_flat = obj['index_flat']  # IndexIDMap2
                self.mem_index_ivf = obj['index_ivf']  # IndexIVFFlat

                if not self.mem_index_flat and not self.mem_index_ivf:
                    raise Exception()
                index_size: int = self.mem_index_flat.ntotal if self.mem_index_flat else self.mem_index_ivf.ntotal
                if self.id_mapping and len(self.id_mapping) != index_size:
                    raise Exception()

                tqdm.write(f'Loaded index from {index_file_path}')
            except:
                raise ValueError('Corrupted index file')
        else:
            tqdm.write(f'Index file {index_file_path} not found, this is a new database')

    def initialize_index(self,
                         vector_dimension: int,
                         training_set: list[np.ndarray] | None = None,
                         training_set_uuid: list[str] | None = None,
                         expected_dataset_size: int = 0):
        """Initialize in-memory index
        - If no training set is given, use a flat index
        - If training set is given, use IVF index
        - If training set is given with UUIDs, track the ID mapping for IVF index

        Args:
            vector_dimension (int): _description_
            training_set (list[np.ndarray] | None, optional): _description_. Defaults to None.
            training_set_uuid (list[str] | None, optional): _description_. Defaults to None.
            expected_dataset_size (int, optional): _description_. Defaults to 0.

        Raises:
            ValueError: _description_
        """
        # If no training set is given, use a flat index
        if not training_set:
            index: IndexFlatL2 = IndexFlatL2(vector_dimension)
            self.mem_index_flat = IndexIDMap2(index)
            return

        # IVF index case
        if training_set_uuid and len(training_set) != len(training_set_uuid):
            raise ValueError('Training set and UUID list have different lengths')

        if expected_dataset_size <= 100000:
            tqdm.write(f'Dataset size {expected_dataset_size} is too small for IVF, suggest using flat index instead')

        # Calculation of a fair number of clusters and training set size for IVF
        # - https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index#how-big-is-the-dataset
        cluster_count = 4 * int(math.sqrt(expected_dataset_size))
        expected_training_set_size = 30 * cluster_count
        if len(training_set) < expected_training_set_size:
            tqdm.write(
                f'Training set {len(training_set)} is too small for the expected dataset size: {expected_dataset_size}, this will lower the accuracy of the index. Expected size: {expected_training_set_size}')

        quantizer: IndexFlatL2 = IndexFlatL2(vector_dimension)
        training_set_np: np.ndarray = np.asarray(training_set)
        self.mem_index_ivf = IndexIVFFlat(quantizer, vector_dimension, cluster_count)
        self.mem_index_ivf.nprobe = InMemoryVectorDb.DEFAULT_NEIGHBOR_COUNT
        self.mem_index_ivf.train(training_set_np)  # type: ignore
        self.index_size_since_last_training = len(training_set)

        # Track vector ID only when the embedding is added with a UUID
        if training_set_uuid:
            self.id_mapping = dict(zip(range(len(training_set_uuid)), training_set_uuid))
            self.mem_index_ivf.add_with_ids(training_set_np, np.asarray(range(len(training_set))))  # type: ignore
        else:
            self.mem_index_ivf.add(training_set_np)  # type: ignore

    def add(self, embeddings: np.ndarray, uuid: str | None = None):
        """Save given embedding to vector DB
        - If no UUID is given, no ID track
        - If UUID is given, track the ID mapping for both flat and IVF index

        Args:
            embeddings (np.ndarray): _description_
            uuid (str | None, optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
            ValueError: _description_
        """
        if not self.mem_index_flat or not self.mem_index_ivf or not self.mem_index_ivf.is_trained:
            raise ValueError('Index not initialized')

        if not self.id_mapping:
            self.id_mapping = dict()

        target_index: IndexIDMap2 | IndexIVFFlat = self.mem_index_flat if self.mem_index_flat else self.mem_index_ivf

        # Track vector ID only when the embedding is added with a UUID
        if uuid:
            id: int = target_index.ntotal
            if id in self.id_mapping:
                # A conflict means some of the embeddings with smaller IDs are deleted
                # - Add a random number to the ID until it is not in the mapping
                while id in self.id_mapping:
                    id += np.random.randint(1, 10)
            self.id_mapping[id] = uuid
            target_index.add_with_ids(np.asarray([embeddings]), np.asarray([id]))  # type: ignore
        else:
            target_index.add(np.asarray([embeddings]))  # type: ignore

    def remove(self, ids: list[int]):
        """Remove given embeddings from vector DB by ID
        - Caller should provide and ensure the ID on their own
        """
        if not self.mem_index_flat or not self.mem_index_ivf or not self.mem_index_ivf.is_trained:
            raise ValueError('Index not initialized')

        if not ids:
            return

        if self.id_mapping:
            for id in ids:
                if id in self.id_mapping:
                    del self.id_mapping[id]
        target_index: IndexIDMap2 | IndexIVFFlat = self.mem_index_flat if self.mem_index_flat else self.mem_index_ivf
        target_index.remove_ids(np.asarray(ids))  # type: ignore

    def clean_all_data(self):
        """Fully clean the library data for reset
        - Remove all keys in vector DB
        """
        if not self.mem_index_flat or not self.mem_index_ivf or not self.mem_index_ivf.is_trained:
            raise ValueError('Index not initialized')

        if self.mem_index_flat:
            self.mem_index_flat.reset()
        if self.mem_index_ivf:
            self.mem_index_ivf.reset()
        if self.id_mapping:
            self.id_mapping.clear()

    def delete_db(self):
        """Fully drop and delete the library data
        1. Remove all keys in vector DB
        2. Delete the index
        """
        self.clean_all_data()
        if os.path.isfile(self.mem_index_path):
            os.remove(self.mem_index_path)

    def persist(self):
        """Persist index to disk
        """
        pickle.dump({
            'id_mapping': self.id_mapping,
            'index_flat': self.mem_index_flat,
            'index_ivf': self.mem_index_ivf,
        }, open(self.mem_index_path, 'wb'))

    def query(self,
              embeddings: np.ndarray,
              top_k: int = 10,
              additional_neighbors: int = 5) -> list[str | int]:
        """Query the given embeddings against the index for similar
        - Return a list of UUIDs or IDs, depending on whether the ID is tracked

        Args:
            embeddings (np.ndarray): _description_
            top_k (int, optional): _description_. Defaults to 10.
            additional_neighbors (int, optional): The additional closest neighbors to be queried for IVF. Defaults to 2.

        Raises:
            ValueError: _description_

        Returns:
            list[str | int]: _description_
        """
        if not self.mem_index_flat or not self.mem_index_ivf or not self.mem_index_ivf.is_trained:
            raise ValueError('Index not initialized')

        if self.mem_index_ivf and additional_neighbors != InMemoryVectorDb.DEFAULT_NEIGHBOR_COUNT and additional_neighbors > 0:
            self.mem_index_ivf.nprobe = additional_neighbors

        target_index: IndexIDMap2 | IndexIVFFlat = self.mem_index_flat if self.mem_index_flat else self.mem_index_ivf
        D, I = target_index.search(np.asarray([embeddings]), top_k)  # type: ignore

        # Reset the number of neighbors to be queried for IVF
        self.mem_index_ivf.nprobe = InMemoryVectorDb.DEFAULT_NEIGHBOR_COUNT

        if not self.id_mapping:
            return list(I[0])
        return [self.id_mapping[id] for id in I[0]]
