import abc
import collections
import copy
import math
import typing

import numpy
import scipy
import sklearn

from ...utils import sparse

T = typing.TypeVar('T')


class Document:
    __slots__ = ('_fields',)

    def __init__(self, *x: list[str]):
        self._fields = list(x)

    @property
    def joint_content(self) -> list[str]:
        full = []
        for field in self._fields:
            full.extend(field)
        return full

    @property
    def raw_content(self) -> list[list[str]]:
        return self._fields


class TextVectorizerBase(abc.ABC):

    def __init__(self,
                 vocab: list[str] | None = None,
                 *,
                 support_fields: bool = False,
                 normalise: bool = False):
        self._vocab = None
        self._restrict_to = set(vocab) if vocab is not None else None
        self._o_restrict_to = self._restrict_to
        self._doc_frequencies = collections.defaultdict(int)
        self._n_docs = 0
        self._fitted = False
        self._fields = support_fields
        self._doc_lengths = []
        self._normalise = normalise

    def update(self, documents: list[Document]):
        self._ensure_fitted(False)
        self._n_docs += len(documents)
        for document in documents:
            full_doc = document.joint_content
            self._doc_lengths.append(len(full_doc))
            if self._restrict_to is not None:
                words = set(full_doc) & self._restrict_to
            else:
                words = set(full_doc)
            for word in words:
                self._doc_frequencies[word] += 1
        return self

    def clone(self) -> typing.Self:
        cp = copy.deepcopy(self)
        cp._restrict_to = self._o_restrict_to
        cp._vocab = None
        cp._fitted = False
        return cp

    def finalise(self):
        self._ensure_fitted(False)
        self._fitted = True
        self._vocab = tuple(self._doc_frequencies)
        if self._restrict_to is None:
            self._restrict_to = set(self._vocab)
        return self

    def transform(self, documents: list[Document]):
        self._ensure_fitted(True)
        rows = []
        cols = []
        data = []
        for i, document in enumerate(documents):
            terms = self._transform_with_vocab(document,
                                               self._vocab,
                                               self._restrict_to)
            for j, term in terms:
                if term == 0.0:
                    continue
                rows.append(i)
                cols.append(j)
                data.append(term)
        out = scipy.sparse.coo_matrix(
            (data, (rows, cols)),
            shape=(len(documents), len(self._vocab))
        )
        if self._normalise:
            out = sklearn.preprocessing.normalize(out, norm='l2', axis=1)
            out = out.tocoo()
        return out      # Guaranteed to be in COO format

    def _transform_with_vocab(self, document: Document, vocab, restrict_to):
        # if self._fields:
        #     document = self._check_doc(document, list[list[str]])
        # else:
        #     document = [self._check_doc(document, list[str])]
        counts, lengths = self._count_words(document, restrict_to)
        terms = self._transform_document(counts,
                                         lengths,
                                         vocab)
        return terms

    @staticmethod
    def _count_words(document: Document, restrict_to: set[str]):
        result = []
        lengths = []
        for field in document.raw_content:
            hist = collections.defaultdict(int)
            lengths.append(len(field))
            for word in field:
                if word in restrict_to:
                    hist[word] += 1
            result.append(hist)
        return result, lengths

    @abc.abstractmethod
    def _transform_document(self,
                            document: list[dict[str, int]],
                            lengths: list[int],
                            vocab: tuple[str]):
        pass


    def _ensure_fitted(self, state: bool):
        if self._fitted != state:
            if state:
                raise ValueError('Text vectorizer is not fitted')
            else:
                raise ValueError('Text vectorizer is already fitted')

    # def _check_doc(self, x, t: type[T], /) -> T:
    #     o = typing.get_origin(t)
    #     if o is None:
    #         if not isinstance(x, t):
    #             raise ValueError(
    #                 f'Invalid type (expected {t}, got {type(x)})'
    #             )
    #         return x
    #     else:
    #         if o is not list:
    #             raise ValueError(
    #                 f'Invalid type {t} (expected list, got {type(x)})'
    #             )
    #         inner = typing.get_args(t)
    #         if len(inner) != 1:
    #             raise ValueError(
    #                 f'Invalid type {t} (expected a single inner type)'
    #             )
    #         if not isinstance(x, list):
    #             raise ValueError(
    #                 f'Invalid type {t} (expected list, got {type(x)})'
    #             )
    #         return [self._check_doc(y, inner[0]) for y in x]


class _TfidfVectorizerBase(TextVectorizerBase, abc.ABC):

    def __init__(self,
                 vocab: list[str] | None = None, *,
                 support_fields: bool = False,
                 outer_field_handling: bool = False,
                 normalise: bool = False):
        super().__init__(vocab, support_fields=support_fields, normalise=normalise)
        self._idf_cache = None
        self._idx_cache = None
        self._outer_field_handling = outer_field_handling

    def _transform_document(self,
                            document: list[dict[str, int]],
                            lengths: list[int],
                            vocab: tuple[str]):
        if self._idf_cache is None:
            self._idf_cache = self._idf(self._doc_frequencies, vocab)
        if self._idx_cache is None:
            self._idx_cache = self._idx(vocab)
        all_words = set()
        for field in document:
            all_words |= set(field)

        if self._outer_field_handling:
            fields = []
            for field, length in zip(document, lengths):
                fields.append(
                    self._apply_idf(
                        self._tf(field, length, vocab),
                        self._idf_cache
                    )
                )
            out = {
                w: math.fsum(field.get(w, 0) for field in fields)
                for w in all_words
            }
        else:

            combined = {
                k: sum(field.get(k, 0) for field in document)
                for k in all_words
            }
            length = sum(lengths)
            out = self._apply_idf(self._tf(combined, length, vocab), self._idf_cache)

        return sorted((self._idx_cache[w], f) for w, f in out.items())

    def _idx(self, vocab: tuple[str]):
        return {
            w: i
            for i, w in enumerate(vocab)
        }

    def _apply_idf(self, tf: dict[str, float], idf: dict[str, float]):
        return {w: f * idf[w] for w, f in tf.items()}

    @abc.abstractmethod
    def _tf(self, counts: dict[str, int], length: int, vocab: tuple[str]):
        pass

    @abc.abstractmethod
    def _idf(self, doc_frequencies: dict[str, int], vocab: tuple[str]):
        pass


class _BinaryTf_TfidfVectorizerBase(_TfidfVectorizerBase, abc.ABC):

    def _tf(self, counts: dict[str, int], length: int, vocab: tuple[str]):
        #return [word in counts for word in vocab]
        return {w: 1 if f > 0 else 0 for w, f in counts.items()}

class _Count_TfidfVectorizerBase(_TfidfVectorizerBase, abc.ABC):

    def _tf(self, counts: dict[str, int], length: int, vocab: tuple[str]):
        #return [counts.get(word, 0) for word in vocab]
        return counts

class _TermFrequency_TfidfVectorizerBase(_TfidfVectorizerBase, abc.ABC):

    def _tf(self, counts: dict[str, int], length: int, vocab: tuple[str]):
        total = length
        #return [counts.get(word, 0) / total if total > 0 else 0 for word in vocab]
        return {w: f / total for w, f in counts.items()}

class _LogSmoothedTermFrequency_TfidfVectorizerBase(_TfidfVectorizerBase, abc.ABC):

    def _tf(self, counts: dict[str, int], length: int, vocab: tuple[str]):
        #return [math.log(counts.get(word, 0) + 1) for word in vocab]
        return {w: math.log(f + 1) for w, f in counts.items()}

class _NormalisedTermFrequency_TfidfVectorizerBase(_TfidfVectorizerBase, abc.ABC):

    def _tf(self, counts: dict[str, int], length: int, vocab: tuple[str]):
        maximum = max(counts.values())
        # return [
        #     0.5 + 0.5*counts.get(word, 0) / maximum
        #     for word in vocab
        # ]
        return {
            w: 0.5 + 0.5*f / maximum
            for w, f in map(lambda x: counts.get(x[0], 0), vocab)
        }


class _UnaryIdf_TfidfVectorizerBase(_TfidfVectorizerBase, abc.ABC):

    def _idf(self, doc_frequencies: dict[str, int], vocab: tuple[str]):
        # return [
        #     1.0 if word in doc_frequencies else 0.0
        #     for word in vocab
        # ]
        return {
            w: 1 if doc_frequencies.get(w, 0) > 0 else 0
            for w in vocab
        }


class _DefaultIdf_TfidfVectorizerBase(_TfidfVectorizerBase, abc.ABC):

    def _idf(self, doc_frequencies: dict[str, int], vocab: tuple[str]):
        # n_docs = self._n_docs + 1
        # return [
        #     math.log(n_docs / (doc_frequencies.get(word, 0) + 1)) + 1
        #     for word in vocab
        # ]
        n_docs = self._n_docs + 1
        return {
            # w: math.log(n_docs / (f + 1)) + 1
            # for w, f in doc_frequencies.items()
            # if f > 0
            w: math.log(n_docs / (f + 1)) + 1
            for w, f in map(lambda x: (x, doc_frequencies.get(x, 0)), vocab)
        }


class _MaxIdf_TfidfVectorizerBase(_TfidfVectorizerBase, abc.ABC):

    def _idf(self, doc_frequencies: dict[str, int], vocab: tuple[str]):
        maximum = max(doc_frequencies.values()) + 1
        # return [
        #     math.log(maximum / (1 + doc_frequencies.get(word, 0))) + 1
        #     for word in vocab
        # ]
        return {
            # w: math.log(maximum / (1 + f)) + 1
            # for w, f in doc_frequencies.items()
            # if f > 0
            w: math.log(maximum / (1 + f)) + 1
            for w, f in map(lambda x: (x, doc_frequencies.get(x, 0)), vocab)
        }


class _ProbabilisticIdf_TfidfVectorizerBase(_TfidfVectorizerBase, abc.ABC):

    def _idf(self, doc_frequencies: dict[str, int], vocab: tuple[str]):
        n_docs = self._n_docs + 1
        # return [
        #     math.log((n_docs - (1 + doc_frequencies.get(word, 0))) / (doc_frequencies.get(word, 0) + 1))
        #     for word in vocab
        # ]
        return {
            # w: math.log((n_docs - (1 + f)) / (f + 1))
            # for w, f in doc_frequencies.items()
            # if f > 0
            w: math.log((n_docs - (1 + f)) / (f + 1))
            for w, f in map(lambda x: (x, doc_frequencies.get(x, 0)), vocab)
        }


class TfidfVectorizer:

    _tf_bases = {
        'binary': _BinaryTf_TfidfVectorizerBase,
        'count': _Count_TfidfVectorizerBase,
        'freq': _TermFrequency_TfidfVectorizerBase,
        'log': _LogSmoothedTermFrequency_TfidfVectorizerBase,
        'norm': _NormalisedTermFrequency_TfidfVectorizerBase,
    }

    _idf_bases = {
        'unary': _UnaryIdf_TfidfVectorizerBase,
        'idf': _DefaultIdf_TfidfVectorizerBase,
        'max': _MaxIdf_TfidfVectorizerBase,
        'prob': _ProbabilisticIdf_TfidfVectorizerBase,
    }

    def __new__(cls,
                tf: typing.Literal['binary', 'count', 'freq', 'log', 'norm'],
                idf: typing.Literal['unary', 'idf', 'max', 'prob'], *,
                vocab: list[str] | None = None,
                support_fields: bool = False,
                outer_field_handling: bool = False,
                normalise: bool = False) -> _TfidfVectorizerBase:
        bases = (
            cls._tf_bases[tf],
            cls._idf_bases[idf],
        )
        new_cls = type(
            f'{tf}_{idf}_TfidfVectorizer',
            bases,
            {}
        )
        self = new_cls(vocab,
                       support_fields=support_fields,
                       outer_field_handling=outer_field_handling,
                       normalise=normalise)
        return self


class RevisedVsmVectorizerBase(_LogSmoothedTermFrequency_TfidfVectorizerBase,
                               _DefaultIdf_TfidfVectorizerBase):

    def rank(self, query: Document, documents: list[Document]):
        v_query = self.transform([query])
        v_documents = self.transform(documents)
        v_cos = [
            cosine_similarity(
                v_query,
                v_documents.getrow(i).tocoo()
            )
            for i in range(v_documents.shape[0])
        ]
        n_min = min(self._doc_lengths)
        n_max = max(self._doc_lengths)
        lengths = [len(doc.joint_content) for doc in documents]
        n = [(x - n_min) / (n_max - n_min) for x in lengths]
        return [g * score for g, score in zip(map(self._g, n), v_cos, strict=True)]

    @staticmethod
    def _g(x):
        return 1 / (1 + math.exp(-x))


class BM25Vectorizer(TextVectorizerBase):

    def __init__(self, *,
                 k1: float = 1.2,
                 b: float = 0.75,
                 delta: float = 0.0,
                 component_weights: list[float] | None = None,
                 vocab: list[str] | None = None,
                 normalise: bool = False):
        super().__init__(
            vocab,
            support_fields=True,
            normalise=normalise
        )
        self._k1 = k1
        self._b = b
        self._delta = delta
        self._w = component_weights
        self._idf_cache = None

    def rank_no_fit(self, query: Document, documents: list[Document]):
        # Determine vocab
        restrict_to = set(query.joint_content)
        vocab = tuple(restrict_to)

        # Calculate IDF
        doc_freq = collections.defaultdict(int)
        lengths = []
        for document in documents:
            joint = document.joint_content
            lengths.append(len(joint))
            for word in set(joint) & restrict_to:
                doc_freq[word] += 1
        n_docs = len(documents)
        idf = [
            math.log(
                (n_docs - n + 0.5) / (n + 0.5) + 1.0
            )
            for n in map(lambda v: doc_freq[v], vocab)
        ]
        avg_length = sum(lengths) / len(documents)

        # Calculate term frequencies
        term_frequencies = []
        for document in documents:
            term_frequencies.append(
                [
                    collections.Counter(field)
                    for field in document.raw_content
                ]
            )

        # Rank documents
        result = []
        w = self._w if self._w is not None else [1] * len(term_frequencies[0])
        for document, length in zip(term_frequencies, lengths, strict=True):
            terms = []
            l = length / avg_length
            for word, idf_coef in zip(vocab, idf, strict=True):
                f_d = math.fsum(
                    w * field.get(word, 0.0)
                    for w, field in zip(w, document, strict=True)
                )
                numerator = f_d * (self._k1 + 1)
                denominator = f_d + self._k1 * (1 - self._b + self._b * l)
                term = numerator / denominator + self._delta
                score_for_term = term * idf_coef
                terms.append(score_for_term)
            result.append(math.fsum(terms))

        return result

    def rank(self, query: Document, documents: list[Document]):
        restrict_to = set(query.joint_content)
        vocab = tuple(restrict_to)
        result = []
        for document in documents:
            terms = self._transform_with_vocab(document,
                                               vocab,
                                               restrict_to)
            result.append(math.fsum(x[1] for x in terms))
        return result

    def _transform_document(self,
                            document: list[dict[str, int]],
                            lengths: list[int],
                            vocab: tuple[str]):
        if self._idf_cache is None:
            self._idf_cache = {
                k: math.log(
                    (self._n_docs - n + 0.5) / (n + 0.5) + 1.0
                )
                for k, n in self._doc_frequencies.items()
            }
        terms = []
        length = sum(lengths)
        avg_length = sum(self._doc_lengths) / self._n_docs
        l = length / avg_length
        if self._w is None:
            w = [1] * len(document)
        else:
            w = self._w
        for i, word in enumerate(vocab):
            f_d = math.fsum(
                w * field.get(word, 0.0)
                for w, field in zip(w, document, strict=True)
            )
            numerator = f_d * (self._k1 + 1)
            denominator = f_d + self._k1 * (1 - self._b + self._b * l)
            term = numerator / denominator + self._delta
            score = term * self._idf_cache.get(word, 0.0)
            if score != 0:
                terms.append((i, score))
        return terms


def cosine_similarity(x, y):
    if isinstance(x, numpy.ndarray):
        dot = numpy.dot(x, y)
        if dot == 0:
            return 0
        return dot / (numpy.linalg.norm(x) * numpy.linalg.norm(y))
    if hasattr(x, 'tocoo'):
        x = x.tocoo()
    if hasattr(y, 'tocoo'):
        y = y.tocoo()
    out = sparse.cosine_similarity(
        sparse.scipy_to_torch_coo(x),
        sparse.scipy_to_torch_coo(y)
    )
    return out.item()


# if __name__ == '__main__':
# #     t = TfidfVectorizer('freq', 'idf', normalise=True)
#     documents = [
#         ['this', 'is', 'a', 'test', 'document', 'hey'],
#         ['this', 'is', 'another', 'test', 'document'],
#         ['this', 'is', 'yet', 'another', 'test', 'document'],
#         ['this', 'is', 'a', 'regular', 'document'],
#         ['this', 'is', 'a', 'query', 'document'],
#     ]
#     q = ['this', 'is', 'a', 'query', 'document']
#     t.update(documents)
#     t.finalise()
#     print(t.transform(documents))
#     print('----')
#     print(t.transform([q]))
#
#     print('======')
#     from sklearn.feature_extraction.text import TfidfVectorizer as SkTfidfVectorizer
#     sk = SkTfidfVectorizer(stop_words=None, token_pattern=r'\b\w+\b')
#     sk.fit([' '.join(x) for x in documents])
#     print(sk.transform([' '.join(x) for x in documents]))
#     print('----')
#     print(sk.transform([' '.join(x) for x in [q]]))
#
    # t = BM25Vectorizer()
    # t.update([Document(x) for x in documents])
    # t.finalise()
    # print(t.rank(
    #     Document(q),
    #     [Document(x) for x in documents]
    # ))
#
#     from bm25 import BM25
#     bm25 = BM25()
#     bm25.update([[x] for x in documents])
#     bm25.finalise()
#     print(bm25.rank(
#         q,
#         [[x] for x in documents]
#     ))
#
#     print(t.transform([[x] for x in documents]))
#     print()
#     print(bm25.vectorise([[x] for x in documents]))
#     print()
#     print(t.transform([[q]]))
#     print()
#     print(bm25.vectorise([[q]]))
#