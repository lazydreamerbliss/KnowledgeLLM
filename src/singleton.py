from knowledge_base.document.doc_embedder import DocEmbedder
from knowledge_base.image.image_embedder import ImageEmbedder
from knowledge_base.image.image_tagger import ImageTagger
from lib_manager import LibraryManager
from utils.task_runner import TaskRunner

# img_embedder = ImageEmbedder()
# doc_embedder = DocEmbedder()
# tagger = ImageTagger()
lib_manager: LibraryManager = LibraryManager()
task_runner: TaskRunner = TaskRunner()
