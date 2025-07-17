mod ml;
mod nlp;
mod bm25;

use std::sync::{Arc, RwLock};
use pyo3::exceptions::{PyException, PyIndexError};
use pyo3::types::PyType;
use pyo3::prelude::*;

use ml::index_loader::IndexLoader;
use crate::bm25::{Document, Query, BM25};
use crate::ml::index_loader::{Bucket, LightweightSample, SampleBucket, SampleBucketItem};
use crate::ml::{Commit, IssueCommitCollection, LightweightLiveSample, LiveIndexLoader, LiveSample};

#[pyclass(name = "IndexLoader")]
struct PyFeatureLoader {
    loader: IndexLoader
}

#[pymethods]
impl PyFeatureLoader {
    #[classmethod]
    #[pyo3(signature = (*, plan_path))]
    fn from_file(_cls: &Bound<'_, PyType>, plan_path: String) -> PyResult<Self> {
        let loader = IndexLoader::load_from_file(plan_path)
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))?;
        Ok(Self { loader })
    }

    fn total_samples(&self) -> usize {
        self.loader.num_features()
    }

    fn total_positive_samples(&self) -> usize {
        self.loader.total_positive_samples()
    }

    fn positive_samples_in_range(&self, start: usize, end: usize) -> usize {
        self.loader.positive_samples_in_range(start, end)
    }

    fn dropped_issues(&self) -> usize {
        self.loader.dropped_issues()
    }

    fn get_issue_buckets(&self) -> Vec<PyBucket> {
        self.loader.get_issue_buckets().into_iter()
            .map(|b| PyBucket { inner: b })
            .collect()
    }

    fn __len__(&self) -> usize {
        self.loader.num_features()
    }

    fn __getitem__(&self, index: usize) -> PyResult<PySample> {
        self.loader.get_sample(index)
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))
            .map(|s| PySample{inner: s})
    }
    
    fn get_samples_for_bucket(&self, index: usize) -> PyResult<Vec<PySample>> {
        self.loader.get_samples_for_bucket(index)
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))
            .map(|ss| ss.into_iter().map(|s| PySample{inner: s}).collect())
    }
    
    fn get_bucket_sample_collection(&self, index: usize) -> PyResult<PySampleBucket> {
        self.loader.get_bucket_sample_collection(index)
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))
            .map(|sb| PySampleBucket{inner: sb})
    }

    fn get_lightweight_samples_for_bucket(&self, index: usize) -> PyResult<Vec<PyLightweightSample>> {
        let samples = self.loader.get_lightweight_samples_for_bucket(index)
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))
            .map(|ss| ss.into_iter().map(|s| PyLightweightSample{inner: s}).collect())?;
        Ok(samples)
    }
    
    fn lightweight_samples(&self) -> PyResult<PySampleContainer> {
        let mut samples = Vec::with_capacity(self.loader.num_features());
        for b in 0..self.loader.num_buckets() {
            let lws = self.loader.get_lightweight_samples_for_bucket(b)
                .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))?;
            samples.extend(lws);
        }
        Ok(PySampleContainer{samples})
    }
    
    fn number_of_buckets(&self) -> PyResult<usize> {
        Ok(self.loader.num_buckets())
    }
}


#[pyclass(name = "Sample")]
struct PySample {
    inner: ml::index_loader::Sample
}

#[pymethods]
impl PySample {
    fn __repr__(&self) -> String {
        format!(
            "Sample(issue={:?}, commits={:?}, issue_file_index={:?}, source_file_index={:?}, source_file_name={:?}, file_name_index={:?}, label={})",
            self.inner.issue_key,
            self.inner.fixing_commits,
            (self.inner.issue_file_index.0, self.inner.issue_file_index.1),
            (self.inner.source_file_index.0, self.inner.source_file_index.1),
            self.inner.source_file_name,
            (self.inner.file_name_index.0, self.inner.file_name_index.1),
            self.inner.label
        )
    }
    
    #[getter]
    fn issue_key(&self) -> PyResult<String> { Ok(self.inner.issue_key.clone()) }
    #[getter]
    fn commits(&self) -> PyResult<Vec<String>> { Ok(self.inner.fixing_commits.clone()) }
    #[getter]
    fn issue_file_index(&self) -> PyResult<(usize, usize)> {
        let index = self.inner.issue_file_index;
        Ok((index.0, index.1))
    }
    #[getter]
    fn source_file_index(&self) -> PyResult<(usize, usize)> {
        let index = self.inner.source_file_index;
        Ok((index.0, index.1))
    }
    #[getter]
    fn source_file_name(&self) -> PyResult<String> { Ok(self.inner.source_file_name.clone()) }
    #[getter]
    fn file_name_index(&self) -> PyResult<(usize, usize)> {
        let index = self.inner.file_name_index;
        Ok((index.0, index.1))
    }
    #[getter]
    fn label(&self) -> PyResult<bool> { Ok(self.inner.label) }
}

#[pyclass(name = "SampleContainer")]
struct PySampleContainer {
    samples: Vec<LightweightSample>
}

#[pymethods]
impl PySampleContainer {
    fn __repr__(&self) -> String {
        format!(
            "SampleContainer(n_items={})",
            self.samples.len()
        )
    }
    
    fn __len__(&self) -> usize {
        self.samples.len()
    }
    
    fn __getitem__(&self, index: usize) -> PyResult<PyLightweightSample> {
        self.samples.get(index)
            .map(|s| PyLightweightSample{inner: *s})
            .ok_or_else(|| PyErr::new::<PyIndexError, _>(format!("Index out of range: {}", index)))
    }
}


#[pyclass(name = "LightweightSample")]
struct PyLightweightSample {
    inner: LightweightSample 
}

#[pymethods]
impl PyLightweightSample {
    fn __repr__(&self) -> String {
        format!(
            "LightweightSample(issue_file_index={:?}, source_file_index={:?}, file_name_index={:?}, label={})",
            self.inner.issue_file_index,
            self.inner.source_file_index,
            self.inner.file_name_index,
            self.inner.label
        )
    }
    
    #[getter]
    fn issue_file_index(&self) -> PyResult<(u16, u32)> {
        Ok(self.inner.issue_file_index)
    }
    #[getter]
    fn source_file_index(&self) -> PyResult<(u16, u32)> {
        Ok(self.inner.source_file_index)
    }
    #[getter]
    fn file_name_index(&self) -> PyResult<(u16, u32)> {
        Ok(self.inner.file_name_index)
    }
    #[getter]
    fn label(&self) -> PyResult<bool> { Ok(self.inner.label) }
}


#[pyclass(name = "Bucket")]
struct PyBucket {
    inner: Bucket 
}

#[pymethods]
impl PyBucket {
    fn __repr__(&self) -> String {
        format!(
            "Bucket(issue_key={:?}, commits={:?}, positive_samples={}, total_samples={}, sample_offset={}, dropped_samples={})",
            self.inner.issue_key,
            self.inner.commits,
            self.inner.positive_samples,
            self.inner.total_samples,
            self.inner.sample_offset,
            self.inner.dropped_samples
        )
    }
    
    #[getter]
    fn issue_key(&self) -> String { self.inner.issue_key.clone() }
    #[getter]
    fn commits(&self) -> Vec<String> { self.inner.commits.clone() }
    #[getter]
    fn positive_samples(&self) -> usize { self.inner.positive_samples }
    #[getter]
    fn total_samples(&self) -> usize { self.inner.total_samples }
    #[getter]
    fn sample_offset(&self) -> usize { self.inner.sample_offset }
    #[getter]
    fn dropped_samples(&self) -> usize { self.inner.dropped_samples }
    #[getter]
    fn temporal_failures(&self) -> usize { self.inner.temporal_failures }
}

#[pyclass(name = "SampleBucket")]
struct PySampleBucket {
    inner: SampleBucket
}

#[pymethods]
impl PySampleBucket {
    fn __repr__(&self) -> String {
        format!(
            "SampleBucket(issue_key={:?}, commits={:?}, issue_file_index={:?}, positives=<{} files>, negatives=<{} files>)",
            self.inner.issue_key,
            self.inner.fixing_commits,
            (self.inner.issue_file_index.0, self.inner.issue_file_index.1),
            self.positives().len(),
            self.negatives().len()
        )
    }

    #[getter]
    fn issue_key(&self) -> String { self.inner.issue_key.clone() }
    #[getter]
    fn commits(&self) -> Vec<String> { self.inner.fixing_commits.clone() }
    #[getter]
    fn issue_file_index(&self) -> (usize, usize) {
        let index = self.inner.issue_file_index;
        (index.0, index.1)
    }
    #[getter]
    fn positives(&self) -> Vec<PySampleBucketItem> {
        self.inner.positives
            .iter()
            .cloned()
            .map(|i| PySampleBucketItem{inner: i})
            .collect()
    }
    #[getter]
    fn negatives(&self) -> Vec<PySampleBucketItem> {
        self.inner.negatives
            .iter()
            .cloned()
            .map(|i| PySampleBucketItem{inner: i})
            .collect()
    }
}

#[pyclass(name = "SampleBucketItem")]
struct PySampleBucketItem {
    inner: SampleBucketItem
}

#[pymethods]
impl PySampleBucketItem {
    fn __repr__(&self) -> String {
        format!(
            "SampleBucketItem(source_file_name={:?}, source_file_index={:?}, file_name_index={:?})",
            self.inner.source_file_name,
            (self.inner.source_file_index.0, self.inner.source_file_index.1),
            (self.inner.file_name_index.0, self.inner.file_name_index.1)
        )
    }
    
    #[getter]
    fn source_file_name(&self) -> String {
        self.inner.source_file_name.clone()
    }
    #[getter]
    fn source_file_index(&self) -> (usize, usize) {
        let index = self.inner.source_file_index;
        (index.0, index.1)
    }
    #[getter]
    fn file_name_index(&self) -> (usize, usize) {
        let index = self.inner.file_name_index;
        (index.0, index.1)
    }
}

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Live API
//////////////////////////////////////////////////////////////////////////////////////////////////


#[pyclass(name = "LiveIndexLoader")]
struct PyLiveIndexLoader {
    inner: Arc<RwLock<LiveIndexLoader>>
}

#[pyclass(name = "IssueCommitCollection")]
struct PyIssueCommitCollection {
    inner: IssueCommitCollection
}

#[pyclass(name = "Commit")]
struct PyCommit {
    inner: Commit
}

#[pyclass(name = "LiveSample")]
struct PyLiveSample {
    inner: LiveSample
}

#[pyclass(name = "LightweightLiveSample")]
struct PyLightweightLiveSample {
    inner: LightweightLiveSample
}

#[pymethods]
impl PyLiveIndexLoader {
    #[classmethod]
    #[pyo3(signature = (path, *, reuse_old_positives=true, transitive_future_positives=false))]
    fn load(_cls: &Bound<'_, PyType>,
            path: String,
            reuse_old_positives: bool,
            transitive_future_positives: bool) -> PyResult<Self>
    {
        let result = LiveIndexLoader::load_from_file(
            path, reuse_old_positives, transitive_future_positives
        );
        let inner = result
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))?;
        Ok(Self { inner })
    }

    #[getter]
    fn number_of_issues(&self) -> PyResult<usize> {
        Ok(self.inner.read()
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))?
            .number_of_issues())
    }

    #[getter]
    fn dropped_issues(&self) -> PyResult<usize> {
        Ok(self.inner.read()
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))?
            .dropped_issues())
    }

    #[getter]
    fn dropped_commits(&self) -> PyResult<usize> {
        Ok(self.inner.read()
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))?
            .dropped_commits())
    }

    fn get_issue(&self, index: usize) -> PyResult<PyIssueCommitCollection> {
        let out = PyIssueCommitCollection {
            inner: self.inner.read()
                .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))?
                .get_issue(index)
        };
        Ok(out)
    }
}

#[pymethods]
impl PyIssueCommitCollection {
    fn __repr__(&self) -> PyResult<String> {
        let out = format!(
            "IssueCommitCollection(issue_key={:?}, number_of_commits={})",
            self.issue_key()?,
            self.number_of_commits()
        );
        Ok(out)
    }

    #[getter]
    fn issue_key(&self) -> PyResult<String> {
        self.inner.issue_key()
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))
    }

    #[getter]
    fn dropped_commits(&self) -> usize {
        self.inner.dropped_commits()
    }

    #[getter]
    fn number_of_commits(&self) -> usize {
        self.inner.number_of_commits()
    }

    fn get_commits(&self) -> PyResult<Vec<PyCommit>> {
        let out = self.inner.get_commits()
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))?
            .into_iter()
            .map(|c| PyCommit{inner: c})
            .collect();
        Ok(out)
    }

    fn get_commit(&self, index: usize) -> PyResult<PyCommit> {
        let commit = self.inner.get_commit(index)
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))?;
        Ok(PyCommit{inner: commit})
    }

    fn debug(&self) -> PyResult<String> {
        self.inner.debug()
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))
    }
}

#[pymethods]
impl PyCommit {
    fn __repr__(&self) -> PyResult<String> {
        let out = format!(
            "Commit(commit_hash={:?}, issue_index={:?})",
            self.commit_hash()?,
            self.issue_index()?
        );
        Ok(out)
    }

    #[getter]
    fn commit_hash(&self) -> PyResult<String> {
        self.inner.commit_hash()
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))
    }

    #[getter]
    fn issue_index(&self) -> PyResult<(usize, usize)> {
        let idx = self.inner.issue_file_index()
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))?;
        Ok((idx.0, idx.1))
    }

    fn samples(&self) -> PyResult<Vec<PyLiveSample>> {
        let raw = self.inner.samples()
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))?;
        let out = raw.into_iter()
            .map(|s| PyLiveSample{inner: s})
            .collect();
        Ok(out)
    }

    fn lightweight_samples(&self) -> PyResult<Vec<PyLightweightLiveSample>> {
        let raw = self.inner.lightweight_samples()
            .map_err(|e| PyErr::new::<PyException, _>(e.to_string()))?;
        let out = raw.into_iter()
            .map(|s| PyLightweightLiveSample{inner: s})
            .collect();
        Ok(out)
    }
}

#[pymethods]
impl PyLiveSample {
    fn __repr__(&self) -> String {
        format!(
            "LiveSample(file_name={:?}, file_name_index={:?}, source_index={:?}, label={})",
            self.inner.source_file_name,
            self.file_name_index(),
            self.source_index(),
            if self.inner.label { "True" } else { "False" }
        )
    }

    #[getter]
    fn file_name(&self) -> String {
        self.inner.source_file_name.clone()
    }

    #[getter]
    fn file_name_index(&self) -> (usize, usize) {
        let idx = self.inner.file_name_index;
        (idx.0, idx.1)
    }

    #[getter]
    fn source_index(&self) -> (usize, usize) {
        let idx = self.inner.source_file_index;
        (idx.0, idx.1)
    }

    #[getter]
    fn label(&self) -> bool {
        self.inner.label
    }
}

#[pymethods]
impl PyLightweightLiveSample {
    fn __repr__(&self) -> String {
        format!(
            "LightweightLiveSample(file_name_index={:?}, source_index={:?}, label={})",
            self.file_name_index(),
            self.source_index(),
            if self.inner.label { "True" } else { "False" }
        )
    }

    #[getter]
    fn file_name_index(&self) -> (usize, usize) {
        let idx = self.inner.file_name_index;
        (idx.0 as usize, idx.1 as usize)
    }

    #[getter]
    fn source_index(&self) -> (usize, usize) {
        let idx = self.inner.source_file_index;
        (idx.0 as usize, idx.1 as usize)
    }

    #[getter]
    fn label(&self) -> bool {
        self.inner.label
    }
}

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// BM25 API
//////////////////////////////////////////////////////////////////////////////////////////////////


#[pyclass(name = "Query")]
#[derive(Clone)]
struct PyQuery(Query);

#[pymethods]
impl PyQuery {
    #[new]
    #[pyo3(signature = (words, /))]
    fn new(words: Vec<String>) -> Self {
        Self(Query::new(words))
    }
}


#[pyclass(name = "Document")]
#[derive(Clone)]
struct PyDocument(Document);

#[pymethods]
impl PyDocument {
    #[new]
    #[pyo3(signature = (fields, /))]
    fn new(fields: Vec<Vec<String>>) -> Self {
        Self(Document::new(fields))
    }
}

#[pyclass(name = "BM25")]
struct PyBM25(BM25);

#[pymethods]
impl PyBM25 {
    #[new]
    #[pyo3(signature = (*, k1 = 1.2, b = 0.75, delta = 0.0, component_weights = None))]
    fn new(k1: f64, b: f64, delta: f64, component_weights: Option<Vec<f64>>) -> Self {
        Self(BM25::new(k1, b, delta, component_weights))
    }
    
    fn rank(&self, query: PyQuery, documents: Vec<PyDocument>) -> Vec<f64> {
        self.0.rank(
            query.0,
            documents.into_iter().map(|d| d.0).collect()
        )
    }
}


/// A Python module implemented in Rust.
#[pymodule]
fn _accelerator(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Old API
    m.add_class::<PyFeatureLoader>()?;
    m.add_class::<PySample>()?;
    m.add_class::<PyBucket>()?;
    m.add_class::<PySampleBucket>()?;
    m.add_class::<PySampleBucketItem>()?;
    // New API
    m.add_class::<PyLiveIndexLoader>()?;
    m.add_class::<PyIssueCommitCollection>()?;
    m.add_class::<PyCommit>()?;
    m.add_class::<PyLiveSample>()?;
    m.add_class::<PyLightweightLiveSample>()?;
    // BM25
    m.add_class::<PyDocument>()?;
    m.add_class::<PyQuery>()?;
    m.add_class::<PyBM25>()?;
    // Preprocessing
    m.add_class::<nlp::py_lib::Tagger>()?;
    m.add_function(wrap_pyfunction!(nlp::py_lib::bulk_replace_parallel, m)?)?;
    m.add_function(wrap_pyfunction!(nlp::py_lib::bulk_replace_parallel_string, m)?)?;
    Ok(())
}
