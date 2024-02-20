from knowledge_base.document.doc_embedder import DocEmbedder
from knowledge_base.image.image_embedder import ImageEmbedder
from knowledge_base.image.image_tagger import ImageTagger
from lib_manager import LibraryManager
from utils.task_runner import TaskRunner

from python.server.grpc_server import GrpcServer

# img_embedder = ImageEmbedder()
# doc_embedder = DocEmbedder()
# tagger = ImageTagger()
task_runner: TaskRunner = TaskRunner()
lib_manager: LibraryManager = LibraryManager(task_runner)
grpc_server: GrpcServer = GrpcServer(task_runner, lib_manager)
