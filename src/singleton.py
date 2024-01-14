from pathlib import Path
from doc_knowledge.doc_embedder import DocEmbedder

from image_knowledge.image_embedder import ImageEmbedder
from image_knowledge.image_tagger import ImageTagger


SAMPLE_FOLDER: str = f'{Path(__file__).parent.parent}/samples'

img_embedder = ImageEmbedder()
#doc_embedder = DocEmbedder()
tagger = ImageTagger()
