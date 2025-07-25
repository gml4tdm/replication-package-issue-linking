use pyo3::prelude::*;
use std::collections::HashMap;
use std::collections::HashSet;
use std::error::Error;
use pyo3::exceptions::PyValueError;
use rayon::prelude::*;



use super::pos::PerceptronTagger;
use super::replacement::{CharTrie, WordTrie};


#[pyclass]
pub struct Tagger {
    p: PerceptronTagger
}

pub fn create_pool(num_threads: usize) -> PyResult<rayon::ThreadPool> {
   match rayon::ThreadPoolBuilder::new()
      .num_threads(num_threads)
      .build()
   {
      Err(e) => Err(PyValueError::new_err(e.to_string())),
      Ok(pool) => Ok(pool),
   }
}

#[pymethods]
impl Tagger {
    #[new]
    pub fn __new__(weights: HashMap<String, HashMap<String, f64>>,
                   classes: HashSet<String>,
                   tagdict: HashMap<String, String>) -> Self {
        Tagger{p: PerceptronTagger::from_weights_and_classes(weights, classes, tagdict)}
    }

    pub fn tag(&self, sentence: Vec<String>) -> Vec<(String, String)> {
        self.p.tag(sentence)
    }

    pub fn bulk_tag(&self, documents: Vec<Vec<Vec<String>>>) -> Vec<Vec<Vec<(String, String)>>> {
        documents
            .into_iter()
            .map(
                |document|
                    document
                        .into_iter()
                        .map(|sentence| self.p.tag(sentence))
                        .collect())
            .collect()
    }

    pub fn bulk_tag_parallel(&self, documents: Vec<Vec<Vec<String>>>, num_threads: usize) -> PyResult<Vec<Vec<Vec<(String, String)>>>> {
        Ok(
            create_pool(num_threads)?.install(|| {
                documents.into_par_iter().map(
                |document|
                    document
                        .into_iter()
                        .map(|sentence| self.p.tag(sentence))
                        .collect())
                .collect()
            })
        )
    }
}

#[pyfunction]
pub fn bulk_replace_parallel(documents: Vec<Vec<String>>,
                         needles: Vec<Vec<String>>,
                         replacement: Vec<String>,
                         num_threads: usize) -> PyResult<Vec<Vec<String>>> {
    let x = create_pool(num_threads)?.install(|| {
        let trie = WordTrie::new(needles);
        documents.into_par_iter().map(
            move |document| trie.replace_substrings_with(document, &replacement)
        )
    }).collect();
    Ok(x)
}

#[pyfunction]
pub fn bulk_replace_parallel_string(documents: Vec<Vec<String>>,
                                needles: Vec<String>,
                                replacement: String,
                                num_threads: usize) -> PyResult<Vec<Vec<String>>> {
    let x = create_pool(num_threads)?.install(|| {
        let trie = CharTrie::new(needles);
        documents.into_par_iter().map(
            move |document| document
                .into_iter()
                .map(|body| trie.replace_substrings_with(body, &replacement))
                .collect()
        )
    }).collect();
    Ok(x)
}

