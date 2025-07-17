from __future__ import annotations

import dataclasses
import json
import pathlib
import string
import typing
import cProfile

import alive_progress
import nltk
import numpy
import scipy
import tap
import torch
from sklearn.decomposition import TruncatedSVD

from ..._accelerator import LiveIndexLoader
from ..._accelerator import BM25 as FastBM25, Query as FastBM25Query, Document as FastBM25Document
from ...features.file_utils import FeatureLoader
from ...models.utils.text_retrieval import TfidfVectorizer, RevisedVsmVectorizerBase, Document
from ...models.utils.text_retrieval import BM25Vectorizer
from ...models.utils.text_retrieval import TextVectorizerBase
from ...models.utils.text_retrieval import cosine_similarity as sparse_cosine_similarity
from ..base import BaseCommand, register
from ...utils.args import parse
from ...models.utils.training import Trainer
from ...utils.text_cleaning.identifiers import split_sub_tokens


@dataclasses.dataclass
class TfidfArgs:
    tf: typing.Literal['binary', 'count', 'freq', 'log', 'norm'] = 'freq'
    idf: typing.Literal['unary', 'idf', 'max', 'prob'] = 'idf'
    combine: typing.Literal['in-sum', 'out-sum'] = 'out-sum'
    normalise: bool = False


@dataclasses.dataclass
class BM25Args:
    k1: float = 1.2
    b: float = 0.75
    delta: float = 0.0
    component_weights: list[float] | None = None
    normalise: bool = False


class VSMConfig(tap.Tap):
    data_directory: pathlib.Path
    output_directory: pathlib.Path
    issue_directory: str
    corpus_source: typing.Literal['issue', 'source', 'all']
    kind: typing.Literal['bm25', 'bm25-rank', 'tfidf', 'rvsm']
    mode: typing.Literal['fit', 'global', 'user']
    sep: bool
    split: str | None = None
    run_on: int | None = None
    lsa_components: int | None = None
    extra_options: str = ''
    batch_size: int = 1000
    stemming: bool = False
    lower_case: bool = False
    sub_token_splitting: bool = False
    detailed_performance: bool = False

    def configure(self):
        self.add_argument('--user', action='store_true', default=False)
        self.add_argument('--sep', action='store_true', default=False)
        self.add_argument('--stemming', action='store_true', default=False)
        self.add_argument('--lower-case', action='store_true', default=False)
        self.add_argument('--sub-token-splitting', action='store_true', default=False)
        self.add_argument('--detailed-performance', action='store_true', default=False)


class DocumentFactory:
    __slots__ = ['_fields']

    def __init__(self, *fields: tuple[str, tuple[int, int]]):
        self._fields = fields

    def __hash__(self):
        return hash(self._fields)

    def __eq__(self, other):
        return isinstance(other, DocumentFactory) and self._fields == other._fields

    @property
    def key(self) -> int:
        return self._make_key(self._fields)

    @classmethod
    def make_key(cls, *fields: tuple[str, tuple[int, int]]):
        return cls._make_key(fields)

    @staticmethod
    def _make_key(fields: tuple[tuple[str, tuple[int, int]], ...]):
        return hash(tuple(fields))

    def resolve(self, loader: FeatureLoader, *, pipeline=None, fast=False):
        if pipeline is None:
            pipeline = lambda x: x
        fields = []
        have_issue = False
        have_others = False
        for kind, index in self._fields:
            if kind == 'issue':
                have_issue = True
                fields.append(loader.get_issue(index))
            elif kind == 'filename':
                have_others = True
                fields.append(loader.get_filename(index))
            elif kind == 'source':
                have_others = True
                fields.append(loader.get_source(index))
            else:
                raise ValueError(f'Unknown kind {kind}')
        if have_issue and have_others and fast:
            raise ValueError('Cannot have both issue and other fields in fast mode')
        if have_issue and fast:
            return FastBM25Query(fields[0])
        if fast:
            return FastBM25Document([pipeline(f) for f in fields])
        else:
            return Document(*(pipeline(f) for f in fields))


class Tokenizer:

    def __init__(self, *,
                 lower_case: bool = True,
                 stemming: bool = False,
                 sub_token_splitting: bool = False):
        self._lower_case = lower_case
        self._sub_token_splitting = sub_token_splitting
        self._stemmer = None
        if stemming:
            self._stemmer = nltk.stem.PorterStemmer()
        self._stop_words = set(nltk.corpus.stopwords.words('english'))

    def __call__(self, text: str | dict[str, str]):
        if isinstance(text, dict):
            text = text['summary'] + '. ' + text['description']
        for x in string.punctuation:
            text = text.replace(x, ' ')

        if self._sub_token_splitting:
            text = split_sub_tokens(text)

        if self._lower_case:
            text = text.lower()

        tokens = [
            token
            for token in text.split()
            if token not in self._stop_words
        ]

        if self._stemmer is not None:
            tokens = [self._stemmer.stem(t) for t in tokens]

        return tokens



@register('vsm')
class VSMCommand(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tokenize = None

    @staticmethod
    def config_type() -> type[tap.Tap]:
        return VSMConfig

    def execute(self):
        assert isinstance(self.config, VSMConfig)

        self._tokenize = Tokenizer(
            lower_case=self.config.lower_case,
            stemming=self.config.stemming,
            sub_token_splitting=self.config.sub_token_splitting
        )

        if self.config.mode in ('fit', 'global') and self.config.split is None:
            raise ValueError('Must specify --split when using --mode=fit or --mode=global')
        if self.config.kind == 'bm25' and self.config.sep:
            raise ValueError('Cannot use --sep with BM25')
        if self.config.corpus_source in ('issue', 'all') and not self.config.sep:
            raise ValueError('Must use --sep with --corpus-source=issue or --corpus-source=all')
        if self.config.run_on is not None and self.config.mode != 'user':
            raise ValueError('mode must be `user` if --run-on is given')
        if self.config.run_on is not None and self.config.split is None:
            raise ValueError('Must specify --split when --run-on is given')

        with cProfile.Profile() as pr:
            if self.config.mode == 'user':
                self.execute_user(self.config)
            elif self.config.mode == 'fit':
                self.execute_fit(self.config)
            elif self.config.mode == 'global':
                self.execute_global(self.config)
            else:
                raise ValueError(f'Unknown mode: {self.config.mode}')
            pr.dump_stats('prof.bin')

    def fast_execute_user_bm25(self, config: VSMConfig):
        self.logger.info('Generating User-Specific VSM Features')
        feature_loader = FeatureLoader(config.data_directory, config.issue_directory)
        loader = LiveIndexLoader.load(
            str(config.data_directory / 'index.json'),
            transitive_future_positives=False,
            reuse_old_positives=True
        )

        batch = self.split_data(loader, config)
        if isinstance(batch, tuple):
            batch = batch[config.run_on]

        args = parse(config.extra_options, BM25Args)

        aggregated_predictions = []
        aggregated_targets = []
        aggregated_indexes = []

        with alive_progress.alive_bar(len(batch)) as bar:
            i_min = -1
            for i in batch:
                if i_min < 0:
                    i_min = i
                self.logger.info('Fast BM25: %s / %s', i - i_min + 1, len(batch))
                model = FastBM25(k1=args.k1,
                                 b=args.b,
                                 delta=args.delta,
                                 component_weights=args.component_weights)
                collection = loader.get_issue(i)
                # For now, only use the first commit
                commit = collection.get_commit(0)
                query = FastBM25Query(
                    self._tokenize(feature_loader.get_issue(commit.issue_index))
                )
                documents = [
                    FastBM25Document([
                        self._tokenize(feature_loader.get_filename(sample.file_name_index)),
                        self._tokenize(feature_loader.get_source(sample.source_index))
                    ])
                    for sample in commit.lightweight_samples()
                ]
                predictions = model.rank(query, documents)
                targets = [sample.label for sample in commit.lightweight_samples()]
                indexes = [i] * len(predictions)
                aggregated_predictions.extend(predictions)
                aggregated_targets.extend(targets)
                aggregated_indexes.extend(indexes)
                bar()

        performance, details = self.evaluate(
            aggregated_predictions, aggregated_targets, aggregated_indexes
        )
        payload = {'train': None, 'validation': None, 'test': performance, 'details': details}
        config.output_directory.mkdir(parents=True, exist_ok=True)
        with open(config.output_directory / 'performance.json', 'w') as f:
            json.dump(payload, f, indent=2)  # type: ignore

    def execute_user(self, config: VSMConfig):
        if config.kind == 'bm25-rank':
            return self.fast_execute_user_bm25(config)

        self.logger.info('Generating User-Specific VSM Features')
        feature_loader = FeatureLoader(config.data_directory, config.issue_directory)
        loader = LiveIndexLoader.load(
            str(config.data_directory / 'index.json'),
            transitive_future_positives=False,
            reuse_old_positives=True
        )

        batch = self.split_data(loader, config)
        if isinstance(batch, tuple):
            batch = batch[config.run_on]

        predictions = []
        targets = []
        indexes = []
        with alive_progress.alive_bar(len(batch)) as bar:
            for i in batch:
                model, tf = self.fit_over_batch(feature_loader, loader, config, [i], show_bar=False)

                if config.kind == 'bm25-rank' or config.kind == 'rvsm':
                    x, y, z = self.direct_rank_over_batch(
                        feature_loader, loader, config, model, [i], show_bar=False
                    )
                    predictions.extend(x)
                    targets.extend(y)
                    indexes.extend(z)
                    bar()
                    continue

                transformed, indices = tf
                if config.lsa_components is not None:
                    lsa = self.fit_lsa(transformed, config)
                    transformed = lsa.transform(transformed)

                x, y, z = self.rank_over_batch(
                    loader, config, transformed, indices, model, [i], show_bar=False
                )
                predictions.extend(x)
                targets.extend(y)
                indexes.extend(z)
                bar()

        performance, details = self.evaluate(predictions, targets, indexes)
        payload = {'train': None, 'validation': None, 'test': performance, 'details': details}
        config.output_directory.mkdir(parents=True, exist_ok=True)
        with open(config.output_directory / 'performance.json', 'w') as f:
            json.dump(payload, f, indent=2)     # type: ignore

    def execute_fit(self, config: VSMConfig):
        self.logger.info('Generating VSM Features (fit)')
        feature_loader = FeatureLoader(config.data_directory, config.issue_directory)
        loader = LiveIndexLoader.load(
            str(config.data_directory / 'index.json'),
            transitive_future_positives=False,
            reuse_old_positives=True
        )
        train, _val, test = self.split_data(loader, config)
        model, tf = self.fit_over_batch(feature_loader, loader, config, train)
        if config.kind == 'bm25-rank' or config.kind == 'rvsm':
            out = self.direct_rank_over_batch(
                feature_loader, loader, config, model, test
            )
            predictions, targets, indexes = out
        else:
            transformed_train, _indices = tf
            transformed, indices = self.transform_over_batch(
                model, feature_loader, loader, config, test
            )
            if config.lsa_components is not None:
                lsa = self.fit_lsa(transformed_train, config)
                transformed = lsa.transform(transformed)
            out = self.rank_over_batch(
                loader, config, transformed, indices, model, test
            )
            predictions, targets, indexes = out

        performance, details = self.evaluate(predictions, targets, indexes)
        payload = {'train': performance, 'validation': None, 'test': None, 'details': details}
        config.output_directory.mkdir(parents=True, exist_ok=True)
        with open(config.output_directory / 'performance.json', 'w') as f:
            json.dump(payload, f, indent=2)     # type: ignore

    def execute_global(self, config: VSMConfig):
        self.logger.info('Generating VSM Features (global)')
        feature_loader = FeatureLoader(config.data_directory, config.issue_directory)
        loader = LiveIndexLoader.load(
            str(config.data_directory / 'index.json'),
            transitive_future_positives=False,
            reuse_old_positives=True
        )
        train, val, test = self.split_data(loader, config)
        model, _tf = self.fit_over_batch(feature_loader, loader, config, train)
        model, _tf = self.fit_over_batch(feature_loader, loader, config, val, pretrained=model)
        predictions = []
        targets = []
        indexes = []
        with alive_progress.alive_bar(len(test)) as bar:
            for issue_index in test:
                model = model.clone()
                model, transformed = self.fit_over_batch(feature_loader, loader, config, [issue_index], pretrained=model)
                if config.kind == 'bm25-rank' or config.kind == 'rvsm':
                    x, y, z = self.direct_rank_over_batch(
                        feature_loader, loader, config, model, [issue_index], show_bar=False
                    )
                    predictions.extend(x)
                    targets.extend(y)
                    indexes.extend(z)
                    bar()
                else:
                    transformed, indices = transformed
                    if config.lsa_components is not None:
                        lsa = self.fit_lsa(transformed, config)
                        transformed = lsa.transform(transformed)
                    x, y, z = self.rank_over_batch(
                        loader, config, transformed, indices, model, [issue_index], show_bar=False
                    )
                    predictions.extend(x)
                    targets.extend(y)
                    indexes.extend(z)
                    bar()

        performance, details = self.evaluate(predictions, targets, indexes)
        payload = {'train': None, 'validation': None, 'test': performance, 'details': details}
        config.output_directory.mkdir(parents=True, exist_ok=True)
        with open(config.output_directory / 'performance.json', 'w') as f:
            json.dump(payload, f, indent=2)     # type: ignore

    def evaluate(self, predictions, targets, indexes):
        assert isinstance(self.config, VSMConfig)
        base = Trainer.evaluate_std(
            task='ranking',
            predictions=predictions,
            targets=targets,
            indexes=indexes,
        )
        if not self.config.detailed_performance:
            return base, None
        detailed = []
        groups = self._split_predictions(predictions, targets, indexes)
        for group_predictions, group_targets, group_indexes in groups:
            group_scores = Trainer.evaluate(
                task='ranking',
                predictions=group_predictions,
                targets=group_targets,
                indexes=group_indexes,
            )
            detailed.append(group_scores)
        return base, detailed

    @staticmethod
    def _split_predictions(predictions, targets, indexes):
        groups = []
        if not isinstance(predictions, torch.Tensor):
            predictions = torch.tensor(predictions)
        if not isinstance(targets, torch.Tensor):
            targets = torch.tensor(targets)
        if not isinstance(indexes, torch.Tensor):
            indexes = torch.tensor(indexes)
        for g in sorted(torch.unique(indexes)):
            group = (
                predictions[indexes == g],
                targets[indexes == g],
                indexes[indexes == g],
            )
            groups.append(group)
        return groups


    def split_data(self, loader: LiveIndexLoader, config: VSMConfig):
        if config.split is None:
            return list(range(loader.number_of_issues))
        parts = [int(x) for x in config.split.split('/')]
        if len(parts) == 3:
            return split_three(range(loader.number_of_issues), *parts)
        elif len(parts) == 2:
            return split_two(range(loader.number_of_issues), *parts)
        else:
            raise ValueError('Invalid split (expected two or three splits)')

    def fit_lsa(self, documents, config: VSMConfig):
        self.logger.info('Applying LSA')
        if isinstance(documents, list):
            matrix = scipy.sparse.vstack(documents)
        else:
            matrix = documents
        n_components = min(config.lsa_components, matrix.shape[1])
        lsa = TruncatedSVD(n_components=n_components)
        lsa.fit(matrix)

        # config.output_directory.mkdir(parents=True, exist_ok=True)
        # i = 1
        # while True:
        #     p = config.output_directory / f'lsa-{i}.pkl'
        #     if not p.exists():
        #         break
        #     i += 1
        # with open(p, 'wb') as f:
        #     import pickle
        #     pickle.dump(lsa.explained_variance_ratio_.tolist(), f)

        return lsa

    def rank_over_batch(self,
                        loader: LiveIndexLoader,
                        config: VSMConfig,
                        transformed,
                        indices,
                        model,
                        batch: list[int],
                        *,
                        show_bar: bool = True):
        predictions = []
        targets = []
        indexes = []
        if config.sep:
            args = parse(config.extra_options, TfidfArgs)
            outer_sum = args.combine == 'out-sum'
        else:
            outer_sum = False   # To silence the IDE
        manager = alive_progress.alive_bar(len(batch)) if show_bar else DummyBar()
        with manager as bar:
            for issue_index in batch:
                issue = loader.get_issue(issue_index)
                # For now, only use the first commit
                commit = issue.get_commit(0)
                issue_key = DocumentFactory.make_key(('issue', commit.issue_index))
                #issue = transformed[indices[issue_key], :]
                issue = _index_array_row(transformed, indices[issue_key])
                for sample in commit.lightweight_samples():
                    if config.sep:
                        src_key = DocumentFactory.make_key(('source', sample.source_index))
                        fn_key = DocumentFactory.make_key(('filename', sample.file_name_index))
                        #source = transformed[indices[src_key], :]
                        #filename = transformed[indices[fn_key], :]
                        source = _index_array_row(transformed, indices[src_key])
                        filename = _index_array_row(transformed, indices[fn_key])
                        if outer_sum:
                            score_1 = self.cosine_similarity(issue, source)
                            score_2 = self.cosine_similarity(issue, filename)
                            score = score_1 + score_2
                        else:
                            features = source + filename
                            score = self.cosine_similarity(issue, features)
                    else:
                        #key = (sample.file_name_index, sample.source_index)
                        key = DocumentFactory.make_key(
                            ('filename', sample.file_name_index),
                            ('source', sample.source_index)
                        )
                        joint = _index_array_row(transformed, indices[key])
                        score = self.cosine_similarity(issue, joint)
                    predictions.append(score)
                    targets.append(sample.label)
                    indexes.append(issue_index)
                bar()

        return predictions, targets, indexes

    @staticmethod
    def cosine_similarity(x, y):
        return sparse_cosine_similarity(x, y)

    def direct_rank_over_batch(self,
                               feature_loader: FeatureLoader,
                               loader: LiveIndexLoader,
                               _config: VSMConfig,
                               model,
                               batch: list[int],
                               *,
                               show_bar: bool = True):
        predictions = []
        targets = []
        indexes = []
        manager = alive_progress.alive_bar(len(batch)) if show_bar else DummyBar()
        with manager as bar:
            for issue_index in batch:
                issue = loader.get_issue(issue_index)
                # For now, only use the first commit
                commit = issue.get_commit(0)
                query = DocumentFactory(('issue', commit.issue_index)).resolve(feature_loader, pipeline=self._tokenize)
                samples = commit.lightweight_samples()
                documents = [
                    DocumentFactory(('filename', idx.file_name_index), ('source', idx.source_index))\
                        .resolve(feature_loader, pipeline=self._tokenize)
                    for idx in samples
                ]
                predictions.extend(model.rank(query, documents))
                targets.extend([idx.label for idx in samples])
                indexes.extend([issue_index] * len(samples))
                bar()
        return predictions, targets, indexes

    def fit_over_batch(self,
                       feature_loader: FeatureLoader,
                       loader: LiveIndexLoader,
                       config: VSMConfig,
                       batch: list[int], *,
                       show_bar: bool = True,
                       pretrained: TextVectorizerBase | None = None):
        if pretrained is not None:
            model = pretrained
        else:
            model = self.instantiate_model(config)
        training_documents = set()
        all_documents = set()

        # Collect indices
        manager = alive_progress.alive_bar(len(batch)) if show_bar else DummyBar()
        with manager as bar:
            for issue_index in batch:
                issue = loader.get_issue(issue_index)
                # For now, only use the first commit
                commit = issue.get_commit(0)

                fact = DocumentFactory(('issue', commit.issue_index))
                if config.corpus_source in ('issue', 'all'):
                    training_documents.add(fact)
                all_documents.add(fact)

                for sample in commit.samples():
                    if config.sep:
                        src_fact = DocumentFactory(('source', sample.source_index))
                        fn_fact = DocumentFactory(('filename', sample.file_name_index))
                        all_documents.add(src_fact)
                        all_documents.add(fn_fact)
                        if config.corpus_source in ('source', 'all'):
                            training_documents.add(src_fact)
                            training_documents.add(fn_fact)
                    else:
                        fact = DocumentFactory(
                            ('filename', sample.file_name_index),
                            ('source', sample.source_index)
                        )
                        all_documents.add(fact)
                        if config.corpus_source in ('source', 'all'):
                            training_documents.add(fact)
                bar()

        # Train the model
        for fact in training_documents:
            doc = fact.resolve(feature_loader, pipeline=self._tokenize)
            model.update([doc])

        model.finalise()

        if config.kind == 'bm25-rank' or config.kind == 'rvsm':
            return model, None   # No need to transform

        # Transform all features
        transformed = self.transform_over_batch_impl(
            model, list(all_documents), feature_loader, config, show_bar=show_bar
        )

        return model, transformed

    def transform_over_batch(self,
                             model: TextVectorizerBase,
                             feature_loader: FeatureLoader,
                             loader: LiveIndexLoader,
                             config: VSMConfig,
                             batch: list[int], *,
                             show_bar: bool = True):
        all_documents = set()
        manager = alive_progress.alive_bar(len(batch)) if show_bar else DummyBar()
        with manager as bar:
            for issue_index in batch:
                issue = loader.get_issue(issue_index)
                # For now, only use the first commit
                commit = issue.get_commit(0)
                all_documents.add(DocumentFactory(('issue', commit.issue_index)))
                for sample in commit.samples():
                    if config.sep:
                        all_documents.add(DocumentFactory(('filename', sample.file_name_index)))
                        all_documents.add(DocumentFactory(('source', sample.source_index)))
                    else:
                        fact = DocumentFactory(
                            ('filename', sample.file_name_index),
                            ('source', sample.source_index)
                        )
                        all_documents.add(fact)
                bar()
        return self.transform_over_batch_impl(
            model, list(all_documents), feature_loader, config, show_bar=show_bar
        )

    def transform_over_batch_impl(self,
                                  model,
                                  documents: list[DocumentFactory],
                                  feature_loader,
                                  config: VSMConfig,
                                  show_bar: bool = True):
        self.logger.info('Transforming features')

        transformed = []
        indices = {}

        for batch in self.batchify(documents, config.batch_size):
            for fact in batch:
                indices[fact.key] = len(indices)
            transformed.append(model.transform([
                fact.resolve(feature_loader, pipeline=self._tokenize)
                for fact in batch
            ]))

        transformed = scipy.sparse.vstack(transformed).tocoo()
        return transformed, indices

    def instantiate_model(self, config: VSMConfig):
        if config.kind == 'tfidf':
            args = parse(config.extra_options, TfidfArgs)
            return TfidfVectorizer(
                tf=args.tf,
                idf=args.idf,
                vocab=None,
                support_fields=not config.sep,
                outer_field_handling=args.combine == 'out-sum',
                normalise=args.normalise
            )
        elif config.kind == 'bm25' or config.kind == 'bm25-rank':
            args = parse(config.extra_options, BM25Args)
            return BM25Vectorizer(
                k1=args.k1,
                b=args.b,
                delta=args.delta,
                component_weights=args.component_weights,
                vocab=None,
                normalise=args.normalise
            )
        elif config.kind == 'rvsm':
            return RevisedVsmVectorizerBase(
                support_fields=not config.sep,
                vocab=None,
            )
        else:
            raise ValueError(f'Unknown kind: {config.kind}')

    @staticmethod
    def batchify(x, batch_size):
        for i in range(0, len(x), batch_size):
            yield x[i:min(i + batch_size, len(x))]


def split_two(items, x, y):
    assert x > 0
    assert y > 0
    assert x + y == 100
    i = _split_bin(len(items), x, y)
    return items[:i], items[i:]


def split_three(items, x, y, z):
    i1, i2 = _split(len(items), x, y, z)
    return items[:i1], items[i1:i2], items[i2:]


def _split(total, x, y, z):
    assert x > 0
    assert y > 0
    assert z > 0
    assert x + y + z == 100
    i1 = _split_bin(total, x, y + z)
    remaining = total - i1
    i2 = _split_bin(remaining, y, z)
    return i1, i2 + i1


def _split_bin(total, p, q):
    # Find the number x such that
    # abs(x/total - p/q) is minimised
    # Where x is an integer
    y = total*p // (p + q)
    if abs(y/total - p/(p + q)) < abs((y + 1)/total - p/(p + q)):
        return y
    return y + 1


class DummyBar:
    def __enter__(self):
        return self
    def __call__(self):
        pass
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def _index_array_row(a, i):
    if isinstance(a, numpy.ndarray):
        return a[i, :]
    return a.getrow(i).tocoo()
