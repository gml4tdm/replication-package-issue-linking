import collections
import math

import scipy


class BM25:

    def __init__(self,
                 k1: float = 1.2,
                 b: float = 0.75,
                 delta: float = 0.0,
                 component_weights: list[float] | None = None,
                 vocab: list[str] | None = None):
        self._k1 = k1
        self._b = b
        self._delta = delta
        self._w = component_weights or [1]
        self._doc_freq = collections.defaultdict(int)
        self._n_docs = 0
        self._total_doc_length = 0
        self._fit = False
        self._vocab = None
        self._restrict_to = set(vocab) if vocab is not None else None
        self._idf_cache = None

    def update(self, documents: list[list[list[str]]]):
        if self._fit:
            raise ValueError('Already finalised')
        self._n_docs += len(documents)
        for fields in documents:
            doc = []
            for field in fields:
                doc.extend(field)
            self._total_doc_length += len(doc)
            if self._restrict_to is not None:
                words = set(doc) & self._restrict_to
            else:
                words = set(doc)
            for word in words:
                self._doc_freq[word] += 1
        return self

    def finalise(self):
        if self._fit:
            raise ValueError('Already finalised')
        self._fit = True
        self._vocab = tuple(self._doc_freq.keys())
        return self

    def vectorise(self, documents: list[list[list[str]]]):
        assert self._fit, 'Fit the model first'
        rows = []
        cols = []
        data = []
        for i, doc_fields in enumerate(documents):
            terms = self._term_coefficients(self._vocab, doc_fields)
            for j, term in enumerate(terms):
                if term == 0.0:
                    continue
                rows.append(i)
                cols.append(j)
                data.append(term)
        return scipy.sparse.coo_matrix(
            (data, (rows, cols)),
            shape=(len(documents), len(self._vocab))
        )

    def rank(self, query: list[str], documents: list[list[list[str]]]):
        assert self._fit, 'Fit the model first'
        words_in_query = list(set(query))
        scores = []
        for doc_fields in documents:
            terms = self._term_coefficients(words_in_query, doc_fields)
            scores.append(math.fsum(terms))
        return scores

    @property
    def _avg_length(self):
        return self._total_doc_length / self._n_docs

    @property
    def _idf(self):
        if self._idf_cache is None:
            self._idf_cache =  {
                k: math.log(
                    (self._n_docs - n + 0.5)/(n + 0.5) + 1.0
                )
                for k, n in self._doc_freq.items()
            }
        return self._idf_cache

    def _term_coefficients(self, vocab: list[str], doc_fields: list[list[str]]):
        terms = []
        doc = []
        for field in doc_fields:
            doc.extend(field)
        doc_frequencies = [collections.Counter(f) for f in doc_fields]
        for word in vocab:
            f_d = self._frequency(word, doc_frequencies)
            l = len(doc) / self._avg_length
            numerator = f_d * (self._k1 + 1)
            denominator = f_d + self._k1 * (1 - self._b + self._b * l)
            term = numerator / denominator + self._delta
            terms.append(self._idf.get(word, 0.0) * term)
        return terms

    def _frequency(self, word: str, doc: list[collections.Counter]):
        return math.fsum(
            w * field.get(word, 0.0)
            for w, field in zip(self._w, doc)
        )


if __name__ == '__main__':
    bm25 = BM25()
    documents = [
        [['this', 'is', 'a', 'test', 'document']],
        [['this', 'is', 'another', 'test', 'document']],
        [['this', 'is', 'yet', 'another', 'test', 'document']],
        [['this', 'is', 'a', 'regular', 'document']],
    ]
    bm25.update(documents)
    bm25.finalise()
    print(bm25.vectorise(documents))
    for x in bm25.vectorise(documents).toarray().tolist():
        print(x)
    print(bm25.rank(['test', 'document'], documents))
    import torch

    z = bm25.vectorise(documents)
    print(torch.from_numpy(z.row))

    y = torch.sparse_coo_tensor(
        torch.vstack([
            torch.from_numpy(z.row),
            torch.from_numpy(z.col),
        ]),
        torch.from_numpy(z.data),
        z.shape
    )