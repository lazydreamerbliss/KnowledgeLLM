import math
import os
import pickle
from functools import wraps

import numpy as np
from faiss import IndexFlatL2, IndexIDMap2, IndexIVFFlat
from loggers import vector_db_logger as LOGGER
from utils.exceptions.db_errors import VectorDbCoreError


def ensure_index(func):
    """Decorator to ensure the index is initialized
    """
    @wraps(func)
    def wrapper(self: 'InMemoryVectorDb', *args, **kwargs):
        if not self._mem_index_flat and not self._mem_index_ivf:
            raise VectorDbCoreError('Index not initialized')
        return func(self, *args, **kwargs)
    return wrapper


class InMemoryVectorDb:
    """It maintains a vector database (FLAT) in-memory for given image library
    - It needs to persist the index to disk for reuse
    """
    IDX_FILENAME: str = 'mem_db.idx'  # Default index file name, if file name is not given
    DEFAULT_NEIGHBOR_COUNT: int = 5  # Default number of nearest neighbors to be queried for IVF

    def __init__(self, data_folder, index_filename: str | None = None, ignore_index_error: bool = False):
        if not data_folder:
            raise VectorDbCoreError(
                'A folder path is mandatory for using in-memory vector DB, index file will be created in the folder')

        data_folder = os.path.expanduser(data_folder)
        if not os.path.isdir(data_folder):
            os.makedirs(data_folder)

        LOGGER.info(f'Loading vector index from disk, path: {data_folder}, index file: {index_filename}')
        index_filename = index_filename or InMemoryVectorDb.IDX_FILENAME
        index_file_path: str = os.path.join(data_folder, index_filename)
        self.mem_index_path: str = index_file_path
        self.__id_mapping: dict[int, str] = dict()  # Maintain the mapping of ID to UUID
        self.__id_mapping_reverse: dict[str, int] = dict()  # Maintain the reverse mapping of UUID to ID
        self._mem_index_flat: IndexFlatL2 | IndexIDMap2 | None = None
        self._mem_index_ivf: IndexIVFFlat | None = None
        self.index_size_since_last_training: int = 0  # TODO: add a timer to retrain the index

        # self.mem_index: IndexIVFFlat | None = None
        if os.path.isfile(index_file_path):
            try:
                obj: dict = pickle.load(open(index_file_path, 'rb'))
                self.__id_mapping = obj.get('id_mapping', dict())  # dict, can be empty
                self.__id_mapping_reverse = obj.get('id_mapping_reverse', dict())  # dict, can be empty
                self._mem_index_flat = obj['index_flat']  # IndexIDMap2
                self._mem_index_ivf = obj['index_ivf']  # IndexIVFFlat

                if not self._mem_index_flat and not self._mem_index_ivf:
                    msg: str = 'Corrupted index file: index not loaded'
                    LOGGER.error(msg)
                    raise VectorDbCoreError(msg)
                if self.__id_mapping:
                    index_size: int = self._mem_index_flat.ntotal if self._mem_index_flat else self._mem_index_ivf.ntotal
                    # If we are not ignoring index error, raise exception on length mismatch
                    if not ignore_index_error \
                            and (len(self.__id_mapping) != index_size or len(self.__id_mapping_reverse) != index_size):
                        msg: str = f'Corrupted index file: ID mapping size {len(self.__id_mapping)} does not match index size {index_size}'
                        LOGGER.error(msg)
                        raise VectorDbCoreError(msg)

                LOGGER.info(f'Index file {index_file_path} loaded successfully')
            except VectorDbCoreError:
                raise
            except Exception as e:
                LOGGER.error(f'Failed to load index file: {e}')
                raise VectorDbCoreError(f'Failed to load index file: {e}')
        else:
            LOGGER.info(f'Index file {index_file_path} not found, this is a new vector database')

    def __get_index(self) -> IndexFlatL2 | IndexIDMap2 | IndexIVFFlat:
        if self._mem_index_flat:
            return self._mem_index_flat
        if self._mem_index_ivf:
            return self._mem_index_ivf
        raise VectorDbCoreError('Index not initialized')

    def initialize_index(self,
                         vector_dimension: int,
                         track_id: bool = False,
                         training_set: np.ndarray | None = None,
                         training_set_uuid_list: list[str] | None = None,
                         expected_dataset_size: int = 0):
        """Initialize in-memory index
        - If no training set is given, use a flat index
        - If training set is given, use IVF index
        - If training set is given with UUIDs, track the ID mapping for IVF index

        Args:
            vector_dimension (int): _description_
            track_id (int): Flat index param, whether to track ID. Defaults to False.
            training_set (list[np.ndarray] | None, optional): IVF index param. Defaults to None.
            training_set_uuid_list (list[str] | None, optional): IVF index param, whether to track ID. Defaults to None.
            expected_dataset_size (int, optional): IVF index param. Defaults to 0.
        """
        LOGGER.info(f'Initializing index for in-memory vector DB, vector dimension: {vector_dimension}, track ID: {track_id}')

        # FLAT index case
        # - If no training set is given using flat index, and return directly
        if training_set is None:
            index: IndexFlatL2 = IndexFlatL2(vector_dimension)
            if track_id:
                self._mem_index_flat = IndexIDMap2(index)
                LOGGER.info('Using flat index for in-memory vector DB with ID tracking, no training data provided')
            else:
                self._mem_index_flat = index
                LOGGER.info('Using flat index for in-memory vector DB, no training data and no ID tracking')
            return

        # IVF index case
        LOGGER.info('Using IVF index for in-memory vector DB, training data provided')
        if training_set_uuid_list and len(training_set) != len(training_set_uuid_list):
            msg: str = 'Training set and UUID list have different lengths'
            LOGGER.error(msg)
            raise VectorDbCoreError(msg)

        # The threshold "7020" is from IVF's warning message "WARNING clustering
        # 2081 points to 180 centroids: please provide at least 7020 training
        # points"
        if expected_dataset_size <= 7020:
            LOGGER.warning(
                f'Dataset size {expected_dataset_size} is too small for IVF, suggest using flat index instead')

        # Calculation of a fair number of clusters and training set size for IVF
        # - https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index#how-big-is-the-dataset
        # - Give warning if the training set size is too small
        cluster_count = 4 * int(math.sqrt(expected_dataset_size))
        expected_training_set_size = 30 * cluster_count
        if len(training_set) < expected_training_set_size:
            LOGGER.warning(
                f'Training set {len(training_set)} is too small for the expected dataset size: {expected_dataset_size}, this will lower the accuracy of the index. Expected size: {expected_training_set_size}')

        quantizer: IndexFlatL2 = IndexFlatL2(vector_dimension)
        self._mem_index_ivf = IndexIVFFlat(quantizer, vector_dimension, cluster_count)
        self._mem_index_ivf.nprobe = InMemoryVectorDb.DEFAULT_NEIGHBOR_COUNT

        self._mem_index_ivf.train(training_set)  # type: ignore
        self.index_size_since_last_training = len(training_set)
        LOGGER.info(f'IVF index trained')

        # Track vector ID only when the embedding is added with a UUID
        if training_set_uuid_list:
            self.__id_mapping = dict(zip(range(len(training_set_uuid_list)), training_set_uuid_list))
            self._mem_index_ivf.add_with_ids(training_set, np.asarray(range(len(training_set))))  # type: ignore
        else:
            self._mem_index_ivf.add(training_set)  # type: ignore
        LOGGER.info(f'IVF index trained data added')

    @ensure_index
    def add(self, uuid: str | None, embedding: list[float]):
        """Save given embedding to vector DB
        - If UUID is not given or empty, no ID track
        - If UUID is given, track the ID mapping for both flat and IVF index

        Args:
            embedding (list[float]): _description_
            uuid (str | None, optional): _description_. Defaults to None.
        """
        target_index: IndexFlatL2 | IndexIDMap2 | IndexIVFFlat = self.__get_index()

        # Track vector ID only when the embedding is added with a UUID
        if uuid:
            id: int = target_index.ntotal

            # A conflict means some of the embeddings with smaller IDs are deleted
            # - Add a random number to the ID until it is not in the mapping
            if id in self.__id_mapping:
                while id in self.__id_mapping:
                    id += np.random.randint(1, 10)

            self.__id_mapping[id] = uuid
            self.__id_mapping_reverse[uuid] = id
            target_index.add_with_ids(np.asarray([embedding]), np.asarray([id]))  # type: ignore
        else:
            target_index.add(np.asarray([embedding]))  # type: ignore

    @ensure_index
    def remove(self, uuids: list[str] | None, ids: list[int] | None):
        """Remove embeddings from vector DB by UUIDs or IDs
        - If remove by UUID then ID tracking is mandatory
        - If both UUID and ID list are given, remove by ID only
        """
        if not uuids and not ids:
            return
        if uuids and not ids and not self.__id_mapping:
            raise VectorDbCoreError('ID mapping is required for removing by UUID')

        LOGGER.info(f'Removing vector entries from in-memory vector DB, UUIDs: {uuids}, IDs: {ids}')
        to_be_removed_ids: list[int] | None = None
        if ids:
            to_be_removed_ids = ids
        elif uuids and self.__id_mapping_reverse:
            to_be_removed_ids = [self.__id_mapping_reverse[uuid] for uuid in uuids if uuid in self.__id_mapping_reverse]
        if not to_be_removed_ids:
            return

        target_index: IndexFlatL2 | IndexIDMap2 | IndexIVFFlat = self.__get_index()
        target_index.remove_ids(np.asarray(to_be_removed_ids))  # type: ignore

        # Clean up deleted IDs from ID mapping
        if self.__id_mapping:
            for id in to_be_removed_ids:
                self.__id_mapping_reverse.pop(self.__id_mapping.pop(id))

    def clean_all_data(self):
        """Fully clean the library data for reset
        - Remove all keys in vector DB
        - Does not need to ensure index, since it could be called before index is initialized
        """
        LOGGER.warning(f'Cleaning in-memory vector DB, path: {self.mem_index_path}')
        if self._mem_index_flat:
            self._mem_index_flat.reset()
        if self._mem_index_ivf:
            self._mem_index_ivf.reset()
        if self.__id_mapping:
            self.__id_mapping.clear()
        if self.__id_mapping_reverse:
            self.__id_mapping_reverse.clear()

    def delete_db(self):
        """Fully drop and delete the library data
        1. Remove all keys in vector DB
        2. Delete the index file
        """
        LOGGER.warning(f'Deleting vector DB and index file, path: {self.mem_index_path}')
        self.clean_all_data()
        if os.path.isfile(self.mem_index_path):
            os.remove(self.mem_index_path)

    def persist(self):
        """Persist index to disk
        """
        LOGGER.info(f'Persisting vector index to disk, path: {self.mem_index_path}')
        pickle.dump({
            'id_mapping': self.__id_mapping,
            'id_mapping_reverse': self.__id_mapping_reverse,
            'index_flat': self._mem_index_flat,
            'index_ivf': self._mem_index_ivf,
        }, open(self.mem_index_path, 'wb'))

    def index_exists(self) -> bool:
        """Check if the index exists
        """
        return os.path.isfile(self.mem_index_path)

    @ensure_index
    def query(self,
              embedding: np.ndarray,
              top_k: int = 10,
              additional_neighbors: int = 5) -> list[str | int]:
        """Query the given embedding against the index for similar
        - Return a list of UUIDs or IDs, depending on whether ID mapping is enabled

        Args:
            embedding (np.ndarray): _description_
            top_k (int, optional): _description_. Defaults to 10.
            additional_neighbors (int, optional): The additional closest neighbors to be queried for IVF. Defaults to 2.
        """
        prob_changed: bool = False
        if self._mem_index_ivf and additional_neighbors != InMemoryVectorDb.DEFAULT_NEIGHBOR_COUNT and additional_neighbors > 0:
            self._mem_index_ivf.nprobe = additional_neighbors
            prob_changed = True

        # Index search returns a tuple of two arrays: distances and IDs
        target_index: IndexFlatL2 | IndexIDMap2 | IndexIVFFlat = self.__get_index()
        D, I = target_index.search(embedding, top_k)  # type: ignore

        # Reset the number of neighbors to be queried for IVF
        if prob_changed and self._mem_index_ivf:
            self._mem_index_ivf.nprobe = InMemoryVectorDb.DEFAULT_NEIGHBOR_COUNT

        if not self.__id_mapping:
            return list(I[0])

        # faiss returns `-1` if not enough neighbors are found, so filter out ID=-1 results
        return [self.__id_mapping[id] for id in I[0] if id > -1]
