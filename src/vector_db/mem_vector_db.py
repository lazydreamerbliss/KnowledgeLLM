import math
import os
import pickle
from functools import wraps

import numpy as np
from faiss import IndexFlatL2, IndexIDMap2, IndexIVFFlat
from tqdm import tqdm


def ensure_index(func):
    """Decorator to ensure the index is initialized
    """
    @wraps(func)
    def wrapper(self: 'InMemoryVectorDb', *args, **kwargs):
        if not self.mem_index_flat and not self.mem_index_ivf:
            raise ValueError('Index not initialized')
        return func(self, *args, **kwargs)
    return wrapper


class InMemoryVectorDb:
    """It maintains a vector database (FLAT) in-memory for given image library
    - It needs to persist the index to disk for reuse
    """
    IDX_FILENAME: str = 'mem_db.idx'
    DEFAULT_NEIGHBOR_COUNT: int = 5  # Default number of nearest neighbors to be queried for IVF

    def __init__(self, folder_path, index_filename: str | None = None):
        if not folder_path:
            raise ValueError(
                'A folder path is mandatory for using in-memory vector DB, index file will be created in the folder')

        tqdm.write(f'Loading vector index from disk...', end=' ')
        folder_path = os.path.expanduser(folder_path)
        if not os.path.isdir(folder_path):
            raise ValueError('Path does not exist')

        index_filename = index_filename or InMemoryVectorDb.IDX_FILENAME
        index_file_path: str = os.path.join(folder_path, index_filename)
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

    def __get_index(self) -> IndexIDMap2 | IndexIVFFlat:
        if self.mem_index_flat:
            return self.mem_index_flat
        if self.mem_index_ivf:
            return self.mem_index_ivf
        raise ValueError('Index not initialized')

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

    @ensure_index
    def add(self, uuid: str | None, embeddings: list[float]):
        """Save given embedding to vector DB
        - If UUID is not given or empty, no ID track
        - If UUID is given, track the ID mapping for both flat and IVF index

        Args:
            embeddings (list[float]): _description_
            uuid (str | None, optional): _description_. Defaults to None.

        Raises:
            ValueError: _description_
            ValueError: _description_
        """
        if not self.id_mapping:
            self.id_mapping = dict()

        target_index: IndexIDMap2 | IndexIVFFlat = self.__get_index()

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

    @ensure_index
    def remove(self, uuids: list[str] | None, ids: list[int] | None):
        """Remove given embeddings from vector DB by UUID or ID
        - If remove by UUID then ID tracking is required
        - If both UUID and ID are given, remove by ID
        """
        if not uuids and not ids:
            return
        if uuids and not ids and not self.id_mapping:
            raise ValueError('ID mapping is required for removing by UUID')

        to_be_removed_ids: list[int] | None = None
        if ids:
            to_be_removed_ids = ids
        elif uuids and self.id_mapping:
            to_be_removed_ids = [id for id, uuid in self.id_mapping.items() if uuid in uuids]
        if not to_be_removed_ids:
            return

        if self.id_mapping:
            for id in to_be_removed_ids:
                if id in self.id_mapping:
                    del self.id_mapping[id]

        target_index: IndexIDMap2 | IndexIVFFlat = self.__get_index()
        target_index.remove_ids(np.asarray(to_be_removed_ids))  # type: ignore

    def clean_all_data(self):
        """Fully clean the library data for reset
        - Remove all keys in vector DB
        - Does not need to ensure index, since it could be called before index is initialized
        """
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

    @ensure_index
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

        Returns:a
            list[str | int]: _description_
        """
        prob_changed: bool = False
        if self.mem_index_ivf and additional_neighbors != InMemoryVectorDb.DEFAULT_NEIGHBOR_COUNT and additional_neighbors > 0:
            self.mem_index_ivf.nprobe = additional_neighbors
            prob_changed = True

        target_index: IndexIDMap2 | IndexIVFFlat = self.__get_index()
        D, I = target_index.search(np.asarray([embeddings]), top_k)  # type: ignore

        # Reset the number of neighbors to be queried for IVF
        if prob_changed and self.mem_index_ivf:
            self.mem_index_ivf.nprobe = InMemoryVectorDb.DEFAULT_NEIGHBOR_COUNT

        if not self.id_mapping:
            return list(I[0])
        return [self.id_mapping[id] for id in I[0]]
