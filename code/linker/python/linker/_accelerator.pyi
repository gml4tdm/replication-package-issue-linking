import typing

# BM25

class Query:
    def __init__(self, words: list[str], /): ...


class Document:
    def __init__(self, fields: list[list[str]], /): ...


class BM25:
    def __init__(self, *,
                 k1: float = 1.2,
                 b: float = 0.75,
                 delta: float = 0.0,
                 component_weights: list[float] | None = None):
        ...

    def rank(self, query: Query, documents: list[Document]) -> list[float]:
        ...


# New API


class LiveIndexLoader:

    @classmethod
    def load(cls,
             plan_path: str, *,
             reuse_old_positives: bool = False,
             transitive_future_positives: bool = True) -> typing.Self:
        ...

    @property
    def number_of_issues(self) -> int:
        ...

    @property
    def dropped_issues(self) -> int:
        ...

    @property
    def dropped_commits(self) -> int:
        ...

    def get_issue(self, idx: int) -> IssueCommitCollection:
        ...


class IssueCommitCollection:

    @property
    def issue_key(self) -> str:
        ...

    @property
    def dropped_commits(self) -> int:
        ...

    @property
    def number_of_commits(self) -> int:
        ...

    def get_commit(self, idx: int) -> Commit:
        ...

    def get_commits(self) -> list[Commit]:
        ...


class Commit:

    @property
    def commit_hash(self) -> str:
        ...

    @property
    def issue_index(self) -> tuple[int, int]:
        ...

    def samples(self) -> list[LiveSample]:
        ...

    def lightweight_samples(self) -> list[LightweightLiveSample]:
        ...


class LiveSample:

    @property
    def file_name(self) -> str:
        ...

    @property
    def file_name_index(self) -> tuple[int, int]:
        ...

    @property
    def source_index(self) -> tuple[int, int]:
        ...

    @property
    def label(self) -> bool:
        ...


class LightweightLiveSample:

    @property
    def file_name_index(self) -> tuple[int, int]:
        ...

    @property
    def source_index(self) -> tuple[int, int]:
        ...

    @property
    def label(self) -> bool:
        ...


# OLD API

class IndexLoader:

    @classmethod
    def from_file(cls, *, plan_path: str) -> typing.Self:
        ...

    def total_samples(self) -> int:
        ...

    def total_positive_samples(self) -> int:
        ...

    def positive_samples_in_range(self, start: int, end: int) -> int:
        ...

    def dropped_issues(self) -> int:
        ...

    def __len__(self) -> int:
        ...

    def __getitem__(self, idx: int) -> Sample:
        ...

    def get_issue_buckets(self) -> list[Bucket]:
        ...

    def get_samples_for_bucket(self, index: int) -> list[Sample]:
        ...
    
    def get_bucket_sample_collection(self, index: int) -> SampleBucket:
        ...

    def lightweight_samples_for_bucket(self, index: int) -> list[LightweightSample]:
        ...

    def lightweight_samples(self) -> SampleContainer:
        ...

    def number_of_buckets(self) -> int:
        ...


class Bucket:
    @property
    def issue_key(self) -> str: ...

    @property
    def commits(self) -> list[str]: ...

    @property
    def positive_samples(self) -> int: ...

    @property
    def total_samples(self) -> int: ...

    @property
    def sample_offset(self) -> int: ...

    @property
    def dropped_samples(self) -> int: ...

    @property
    def temporal_failures(self) -> int: ...


class Sample:

    @property
    def issue_key(self) -> str: ...

    @property
    def commits(self) -> list[str]: ...

    @property
    def issue_file_index(self) -> tuple[int, int]: ...

    @property
    def source_file_index(self) -> tuple[int, int]: ...

    @property
    def source_file_name(self) -> str: ...

    @property
    def file_name_index(self) -> tuple[int, int]: ...

    @property
    def label(self) -> bool: ...


class SampleContainer:

    def __repr__(self) -> str: ...

    def __len__(self) -> int: ...

    def __getitem__(self, index: int) -> LightweightSample: ...


class LightweightSample:
    @property
    def issue_file_index(self) -> tuple[int, int]: ...

    @property
    def source_file_index(self) -> tuple[int, int]: ...

    @property
    def file_name_index(self) -> tuple[int, int]: ...

    @property
    def label(self) -> bool: ...
    
    
class SampleBucket:

    def __repr__(self) -> str: ...
    
    @property 
    def issue_key(self) -> str: ...
    
    @property 
    def commits(self) -> list[str]: ...

    @property
    def issue_file_index(self) -> tuple[int, int]: ...

    @property
    def positives(self) -> list[SampleBucketItem]: ...

    @property
    def negatives(self) -> list[SampleBucketItem]: ...


class SampleBucketItem:

    def __repr__(self) -> str: ...

    @property
    def source_file_index(self) -> tuple[int, int]: ...

    @property
    def source_file_name(self) -> str: ...

    @property
    def file_name_index(self) -> tuple[int, int]: ...


def bulk_clean_text_parallel(documents: list[str],
                             formatting_handling: str,
                             num_threads: int) -> list[str]: ...


def bulk_replace_parallel(documents: list[list[str]],
                          needles: list[list[str]],
                          replacement: list[str],
                          num_threads: int) -> list[list[str]]: ...


def bulk_replace_parallel_string(documents: list[list[str]],
                                 needles: list[str],
                                 replacement: str,
                                 num_threads: int) -> list[list[str]]: ...



class Tagger:
    def __init__(self,
                 weights: dict[str, dict[str, float]],
                 classes: set[str],
                 tagdict: dict[str, str]): ...

    def tag(self, sentence: list[str]) -> list[tuple[str, str]]: ...

    def bulk_tag(self,
                 documents: list[list[list[str]]]) -> list[list[list[tuple[str, str]]]]: ...

    def bulk_tag_parallel(self,
                          documents: list[list[list[str]]],
                          num_threads: int) -> list[list[list[tuple[str, str]]]]: ...
