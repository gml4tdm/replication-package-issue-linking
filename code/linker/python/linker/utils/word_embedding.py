import pathlib

import gensim
import gensim.scripts.glove2word2vec


def load_word_embedding(path: str, file_format) -> gensim.models.KeyedVectors:
    match file_format:
        case 'word2vec-gensim':
            return gensim.models.KeyedVectors.load(path)    # type: ignore
        case 'word2vec-c':
            return gensim.models.KeyedVectors.load_word2vec_format(path, binary=False)
        case 'word2vec-c-binary':
            return gensim.models.KeyedVectors.load_word2vec_format(path, binary=True)
        case 'fasttext-gensim':
            return gensim.models.FastText.load(path).wv
        case 'fasttext-native':
            return gensim.models.fasttext.load_facebook_vectors(path)
        case 'fasttext-native-model':
            return gensim.models.fasttext.load_facebook_model(path).wv
        case 'glove':
            return gensim.models.KeyedVectors.load_word2vec_format(
                path, binary=False, no_header=True
            )
        case _:
            raise ValueError(f'Unknown file format: {file_format}')
