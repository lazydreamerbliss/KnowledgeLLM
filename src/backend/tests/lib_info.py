from pathlib import Path

from constants.lib_constants import LibTypes
from utils.lib_manager import LibInfo

doc_lib1: LibInfo = LibInfo()
doc_lib1.uuid = '17aad22d-db89-441d-bb8f-5a178bd0b041'
doc_lib1.name = 'doc_lib1'
doc_lib1.path = f'{Path(__file__).parent}/doc_lib1'
doc_lib1.type = LibTypes.DOCUMENT.value

doc_lib2: LibInfo = LibInfo()
doc_lib2.uuid = '4677ba79-dcc8-4886-92b6-69ceb4483aa6'
doc_lib2.name = 'doc_lib2'
doc_lib2.path = f'{Path(__file__).parent}/doc_lib2'
doc_lib2.type = LibTypes.DOCUMENT.value

img_lib1: LibInfo = LibInfo()
img_lib1.uuid = 'e6c9a6a3-5c3d-4b8d-9d8e-7f0e4b3b1d6f'
img_lib1.name = 'img_lib1'
img_lib1.path = f'{Path(__file__).parent}/img_lib1'
img_lib1.type = LibTypes.IMAGE.value

img_lib2: LibInfo = LibInfo()
img_lib2.uuid = 'd5b3f8e7-8a9d-4a0c-9d4e-9c8e4b3b1d6f'
img_lib2.name = 'img_lib2'
img_lib2.path = f'{Path(__file__).parent}/img_lib2'
img_lib2.type = LibTypes.IMAGE.value
