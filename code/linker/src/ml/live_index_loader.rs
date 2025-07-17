//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Imports
//////////////////////////////////////////////////////////////////////////////////////////////////

use std::collections::hash_map::Entry;
use std::collections::HashMap;
use std::fs::File;
use std::path::Path;
use std::sync::{Arc, RwLock};
use serde::Deserialize;
use super::resolver::{ResolvedEntry, Resolver};
use super::errors::{IndexDecodingError, IndexLoadingError};
use super::raw_index::RawIndex;
use super::shared_types::{FileIndex, Index};

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Types
//////////////////////////////////////////////////////////////////////////////////////////////////

pub struct LiveIndexLoader {
    index: Index,
    resolver: Resolver,
    file_mapping: Vec<String>,
    commit_mapping: Vec<String>,
    rows: Vec<IssueCommitCollection>,
    dropped_commits: usize,
    dropped_issues: usize
}

#[derive(Clone)]
pub struct IssueCommitCollection {
    index_loader: Arc<RwLock<LiveIndexLoader>>,
    pairing_index: usize,
    dropped_commits: usize,
    number_of_commits: usize,
}

pub struct Commit {
    index_loader: Arc<RwLock<LiveIndexLoader>>,
    entries: Arc<Vec<ResolvedEntry>>,
    pairing_index: usize,
    commit_index: usize,
    files: Vec<(usize, bool)>
}

pub struct LightweightSample {
    pub source_file_index: (u16, u32),
    pub file_name_index: (u16, u32),
    pub label: bool
}

pub struct Sample {
    pub source_file_index: FileIndex,
    pub source_file_name: String,
    pub file_name_index: FileIndex,
    pub label: bool
}

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Implementation
//////////////////////////////////////////////////////////////////////////////////////////////////

impl LiveIndexLoader {
    pub fn load_from_file(path: impl AsRef<Path>,
                          reuse_old_positives: bool, 
                          transitive_future_positives: bool) -> Result<Arc<RwLock<Self>>, IndexLoadingError> {
        let file = File::open(path)
            .map_err(IndexDecodingError::IOError)?;
        let reader = std::io::BufReader::new(file);
        let raw_index: RawIndex = serde_json::from_reader(reader)
            .map_err(|e| IndexDecodingError::InternalLibraryError(e.into()))?;
        let index: Index = raw_index.try_into()?;
        let file_mapping = Self::convert_registry(&index.file_registry);
        let commit_mapping = Self::convert_registry(&index.commit_registry);
        let resolver = Resolver::new(reuse_old_positives, transitive_future_positives);
        let instance = Arc::new(
            RwLock::new(
                Self {
                    index,
                    file_mapping,
                    commit_mapping,
                    resolver,
                    rows: Vec::new(),
                    dropped_issues: 0,
                    dropped_commits: 0
                }   
            )
        );
        {
            // We need to enter a separate scope so that 'obj' is released.
            // Luckily, this is the only write access we will ever need.
            let mut obj = instance.write()?;
            for i in 0..obj.index.pairings.len() {
                //println!("{} {i}", obj.index.pairings[i].issue_key);
                let result = obj.resolver.resolve(&obj.index, i)?;
                let dropped = result.samples_by_commit.values()
                    .map(|x| if !x.iter().any(|y| y.1) { 1 } else { 0 } )
                    .sum::<usize>();
                obj.dropped_commits += dropped;
                if dropped == result.samples_by_commit.len() {
                    obj.dropped_issues += 1;
                    continue;
                }
                obj.rows.push(IssueCommitCollection {
                    index_loader: instance.clone(),
                    pairing_index: i,
                    dropped_commits: dropped,
                    number_of_commits: result.samples_by_commit.len() - dropped
                });
            }
        }
        Ok(instance)
    }

    fn convert_registry(registry: &HashMap<String, usize>) -> Vec<String> {
        let mut reverse_mapping = registry
            .into_iter()
            .map(|(k, v)| (*v, k.clone()))
            .collect::<HashMap<_, _>>();
        let mut new_registry = Vec::new();
        for i in 0..reverse_mapping.len() {
            match reverse_mapping.entry(i) {
                Entry::Occupied(e) => {
                    new_registry.push(e.remove());
                }
                Entry::Vacant(_) => {
                    panic!("Registry missing commit {i}");
                }
            }
        }
        new_registry
    }
    
    pub fn number_of_issues(&self) -> usize {
        self.rows.len()
    }
    
    pub fn dropped_issues(&self) -> usize {
        self.dropped_issues
    }
    
    pub fn dropped_commits(&self) -> usize {
        self.dropped_commits
    }
    
    pub fn get_issue(&self, index: usize) -> IssueCommitCollection {
        self.rows[index].clone()
    }
}

impl IssueCommitCollection {
    pub fn issue_key(&self) -> Result<String, IndexLoadingError> {
        let loader = self.index_loader.read()?;
        let pairing = &loader.index.pairings[self.pairing_index];
        Ok(pairing.issue_key.clone())
    }
    
    pub fn dropped_commits(&self) -> usize {
        self.dropped_commits
    }
    
    pub fn number_of_commits(&self) -> usize {
        self.number_of_commits
    }
    
    pub fn get_commits(&self) -> Result<Vec<Commit>, IndexLoadingError> {
        let loader = self.index_loader.read()?;
        let resolved = loader.resolver.resolve(
            &loader.index, self.pairing_index
        )?;
        let commit_ids = resolved.commits.into_iter()
            .filter(|i| resolved.samples_by_commit.get(i)
                .expect("Missing samples for commit")
                .iter()
                .any(|x| x.1)
            )
            .collect::<Vec<_>>();
        let entries = Arc::new(resolved.data);
        let commits = commit_ids.into_iter()
            .map(|i| {
                Commit {
                    index_loader: self.index_loader.clone(),
                    entries: entries.clone(),
                    pairing_index: self.pairing_index,
                    commit_index: i,
                    files: resolved.samples_by_commit.get(&i).unwrap().clone()
                }
            })
            .collect::<Vec<_>>();
        Ok(commits)
    }
    
    pub fn get_commit(&self, index: usize) -> Result<Commit, IndexLoadingError> {
        let commit = self.get_commits()?
            .into_iter()
            .nth(index)
            .expect("Index out of bounds");
        Ok(commit)
    }
    
    pub fn debug(&self) -> Result<String, IndexLoadingError> {
        let loader = self.index_loader.read()?;
        let resolved = loader.resolver.resolve(
            &loader.index, self.pairing_index
        )?;
        Ok(format!("{resolved:?}"))
    }
}

impl Commit {
    pub fn commit_hash(&self) -> Result<String, IndexLoadingError> {
        let loader = self.index_loader.read()?;
        let registry = &loader.commit_mapping;
        Ok(registry[self.commit_index].clone())
    }
    
    pub fn issue_file_index(&self) -> Result<FileIndex, IndexLoadingError> {
        let loader = self.index_loader.read()?;
        let pairing = &loader.index.pairings[self.pairing_index];
        Ok(pairing.issue_file)
    }
    
    pub fn samples(&self) -> Result<Vec<Sample>, IndexLoadingError> {
        let loader= self.index_loader.read()?;
        let registry = &loader.file_mapping;
        self.samples_helper(
            |(uid, label)| {
                let entry = &self.entries[uid];
                let filename = registry[entry.filename].clone();
                let filename_index = loader.index.filename_index[entry.filename];
                let source_index = entry.content;
                Sample {
                    file_name_index: filename_index,
                    source_file_name: filename,
                    source_file_index: source_index,
                    label
                }
            }
        )
    }
    
    pub fn lightweight_samples(&self) -> Result<Vec<LightweightSample>, IndexLoadingError> {
        let loader= self.index_loader.read()?;
        self.samples_helper(
            |(uid, label)| {
                let entry = &self.entries[uid];
                let filename_index = loader.index.filename_index[entry.filename];
                let source_index = entry.content;
                LightweightSample {
                    file_name_index: filename_index
                        .try_into()
                        .expect("Failed to convert file index to compact representation"),
                    source_file_index: source_index
                        .try_into()
                        .expect("Failed to convert file index to compact representation"),
                    label
                }
            }
        )
    }
    
    fn samples_helper<F, T>(&self, f: F) -> Result<Vec<T>, IndexLoadingError>
    where
        F: Fn((usize, bool)) -> T
    {
        let files = self.files.iter()
            .copied()
            .map(f)
            .collect::<Vec<_>>();
        Ok(files)
    }
}
