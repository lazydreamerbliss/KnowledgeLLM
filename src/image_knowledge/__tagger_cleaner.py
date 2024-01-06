import re
from pathlib import Path

import nltk
import regex
from deep_translator import GoogleTranslator
from nltk.corpus import wordnet as wn

nltk.download('wordnet')
translator = GoogleTranslator(source='en', target='zh-CN')
words = ['amazing', 'interesting', 'love', 'great', 'nice']


translated_list: list[str] = list()
tag_list: list[str] = list()
with open(Path(f'{Path(__file__).parent.parent.parent}/local_models/fancyfeast--joytag')/'top_tags.txt', 'r') as f:
    batch_size: int = 200
    pending_for_trans: str = ''
    saved_taggers: str = ''
    batch_count: int = 0
    for line in f.readlines():
        pending_for_trans += ' '.join(line.lower().strip().split('_')) + ';;;'
        saved_taggers += line.lower().strip() + ';;'
        batch_count += 1
        if batch_count <= batch_size:
            continue
        else:
            translated: str = translator.translate(pending_for_trans).replace('\u200b', '').replace('；', ';').replace('; ;;', ';;;').replace(';; ;', ';;;').replace('; ; ;', ';;;').replace(';;;', ';;')
            tag_list += [tag for tag in saved_taggers.split(';;')]
            translated_list += [word for word in translated.split(';;')]
            print(saved_taggers)
            print(translated)
            print(len(tag_list), len(translated_list))
            saved_taggers = ''
            batch_count = 0
            pending_for_trans = ''


    if len(pending_for_trans) > 0:
        translated: str = translator.translate(pending_for_trans).replace('\u200b', '').replace('；', ';').replace('; ;;', ';;;').replace(';; ;', ';;;').replace('; ; ;', ';;;').replace(';;;', ';;')
        print(saved_taggers)
        print(translated)
        print(len(tag_list), len(translated_list))
        tag_list += [tag.strip() for tag in saved_taggers.split(';;')]
        translated_list += [word.strip() for word in translated.split(';;')]


if __name__ == '__main__':
    with open(f'{Path(__file__).parent}/tmp.txt', 'w') as F:
        for i, tag in enumerate(tag_list):
            translate = translated_list[i]
            F.write(f'{tag_list[i]}:{translated_list[i]}\n')
