from __future__ import annotations

import json
import pathlib


class FeatureLoader:

    def __init__(self, base_directory: pathlib.Path, issue_directory: str):
        self._issue_loader = DataLoader(base_directory / issue_directory)
        self._source_loader = DataLoader(base_directory / 'source-code')
        self._filenames_loader = DataLoader(base_directory / 'filenames')

    def get_issue(self, idx):
        return self._issue_loader.fetch(idx)

    def get_source(self, idx):
        return self._source_loader.fetch(idx)

    def get_filename(self, idx):
        return self._filenames_loader.fetch(idx)


class DataLoader:

    def __init__(self, directory: pathlib.Path):
        self._directory = directory
        self._cache = {}
        self._lru = []
        self._max_size = 4

    def fetch(self, idx: tuple[int, int]):
        file_id, index = idx
        if file_id not in self._cache:
            if len(self._cache) > self._max_size:
                del self._cache[self._lru[-1]]
                self._lru.pop()
            self._cache[file_id] = self._load_file(file_id)
            self._lru.insert(0, file_id)
        else:
            self._lru.remove(file_id)
            self._lru.insert(0, file_id)
        return self._cache[file_id][index]

    def _load_file(self, file_id: int):
        with open(self._directory / f'{file_id}.json') as f:
            return json.load(f)
