//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Imports
//////////////////////////////////////////////////////////////////////////////////////////////////

use std::collections::hash_map::Entry;
use std::collections::{HashMap, HashSet};
use std::path::Path;

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Public Types
//////////////////////////////////////////////////////////////////////////////////////////////////


const DEBUG_RESOLVE: bool = false;


#[derive(Debug)]
pub struct IndexLoader {
    index: Index,
    file_mapping: Vec<String>,
    commit_mapping: Vec<String>,
    rows: Vec<IndexRow>,
    dropped_issues: usize
}

#[derive(Debug)]
struct IndexRow {
    pairing_index: usize,
    sample_count_offset: usize,
    local_sample_count: usize,
    true_sample_count: usize,
    dropped_sample_count: usize,
    temporal_failures: usize
}

#[derive(Debug)]
pub(super) struct Index {
    file_registry: HashMap<String, usize>,
    commit_registry: HashMap<String, usize>,
    delta_by_commit: HashMap<usize, Vec<Delta>>,
    packed_commits: HashMap<usize, HashMap<usize, FileIndex>>,
    restoration_points: HashMap<usize, usize>,
    parents: HashMap<usize, Vec<usize>>,
    pairings: Vec<Pairing>,
    filename_index: Vec<FileIndex>,
    changes_by_commit: Vec<Vec<FileChange>>,
    merge_commit_changes: HashMap<usize, HashMap<usize, Vec<FileChange>>>,
    commit_order: Vec<usize>,
    reversed_order: Vec<usize>
}

pub struct Sample {
    pub issue_key: String,
    pub fixing_commits: Vec<String>,
    pub issue_file_index: FileIndex,
    pub source_file_index: FileIndex,
    pub source_file_name: String,
    pub file_name_index: FileIndex,
    pub label: bool
}

#[derive(Copy, Clone)]
pub struct LightweightSample {
    pub issue_file_index: (u16, u32),
    pub source_file_index: (u16, u32),
    pub file_name_index: (u16, u32),
    pub label: bool
}

pub struct Bucket {
    pub issue_key: String,
    pub commits: Vec<String>,
    pub positive_samples: usize,
    pub total_samples: usize,
    pub sample_offset: usize,
    pub dropped_samples: usize,
    pub temporal_failures: usize
}

pub struct SampleBucket {
    pub issue_key: String,
    pub fixing_commits: Vec<String>,
    pub issue_file_index: FileIndex,
    pub positives: Vec<SampleBucketItem>,
    pub negatives: Vec<SampleBucketItem>
}

#[derive(Clone)]
pub struct SampleBucketItem {
    pub source_file_name: String,
    pub source_file_index: FileIndex,
    pub file_name_index: FileIndex,
}

#[derive(Debug)]
pub struct Pairing {
    issue_key: String,
    resolving_commits: Vec<usize>,
    files_changed_for_commits: Vec<Vec<usize>>,
    issue_file: FileIndex,
}

#[derive(Debug, Copy, Clone)]
#[derive(serde::Deserialize)]
pub struct FileIndex(pub usize, pub usize);

impl TryFrom<FileIndex> for (u16, u32) {
    type Error = anyhow::Error;
    
    fn try_from(value: FileIndex) -> Result<Self, Self::Error> {
        let file_id = value.0.try_into()
            .map_err(|_| anyhow::anyhow!("Invalid file index for lightweight representation (too large)"))?;
        let index = value.1.try_into()
            .map_err(|_| anyhow::anyhow!("Invalid file index for lightweight representation (too large)"))?;
        Ok((file_id, index))
    }
}

#[derive(Debug, Copy, Clone)]
enum Delta {
    Add{file_id: usize, index: FileIndex},
    Remove{file_id: usize}
}

#[derive(Debug, Copy, Clone, serde::Deserialize)]
enum FileChangeType {
    #[serde(rename = "add")] Add,
    #[serde(rename = "mod")] Modify,
    #[serde(rename = "rem")] Remove,
    #[serde(rename = "mod-special")] ModifySpecial
}

#[derive(Debug, Copy, Clone)]
struct FileChange {
    kind: FileChangeType,
    old_name: Option<usize>,
    new_name: Option<usize>
}


//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Bucket Resolving
//////////////////////////////////////////////////////////////////////////////////////////////////


struct ResolvedBucket {
    files: Vec<ResolvedBucketEntry>,
    positive: HashSet<usize>,
    negative: HashSet<usize>
}

struct ResolvedBucketEntry {
    filename: usize,
    content: FileIndex
}

struct BaseResolver {
    entries: Vec<ResolvedBucketEntry>,
    negatives: HashSet<usize>,
    positives: HashSet<usize>,
    pending_negatives: HashSet<usize>,
    current_files: HashMap<usize, usize>,
    added: HashSet<usize>
}

impl BaseResolver {
    fn new() -> Self {
        Self {
            entries: Vec::new(),
            negatives: HashSet::new(),
            positives: HashSet::new(),
            pending_negatives: HashSet::new(),
            current_files: HashMap::new(),
            added: HashSet::new()
        }
    }

    fn resolve(mut self, index: &Index, i: usize) -> ResolvedBucket {
        let pairing = &index.pairings[i];

        let first_in_line = *pairing.resolving_commits.iter().min_by_key(
            |x| index.commit_order[**x]
        ).expect("No min");
        let last_in_line = *pairing.resolving_commits.iter().max_by_key(
            |x| index.commit_order[**x]
        ).expect("No max");

        let initial = index.resolve_commit(first_in_line);
        let files = self.register_files(initial).clone();
        self.negatives.extend(files.values().copied());

        let n = pairing.resolving_commits.len();
        let mut next_in_line = 0;
        let mut prev: Option<usize> = None;

        if DEBUG_RESOLVE {
            println!("> {i}");
            println!("{files:?}");
        }


        let path = index.commit_path(
            first_in_line,
            last_in_line
        );
        let path = path.expect("Failed to find commit path");
        let missed_commits = pairing.resolving_commits.iter()
            .copied()
            .all(|x| path.contains(&x));
        if DEBUG_RESOLVE {
            println!("{:?}", pairing.resolving_commits);
            println!("{:?}", path);
        }
        if !missed_commits {
            let stuff = pairing.resolving_commits.iter().copied()
                .map(|x| index.commit_registry.iter().find(|(_, y)| **y == x).unwrap().0.clone()).collect::<Vec<_>>(); 
            
            panic!("Failed to resolve a commit collection: {:?}", stuff);
        }

        for j in path {
            //let j = index.reversed_order[loc];
            let is_related = next_in_line < n && j == pairing.resolving_commits[next_in_line];
            if is_related { next_in_line += 1; }

            let new_contents = self.new_commit_contents(index, j);

            if is_related {
                self.negatives.extend(self.pending_negatives.drain());
            }

            let changes = if index.parents.get(&j).map(|x| x.len()).unwrap_or(0) <= 1 {
                &index.changes_by_commit[j]
            } else {
                let p = prev.expect("Merge commit cannot be first commit");
                if DEBUG_RESOLVE {
                    let p_h = index.commit_registry.iter().find(|(_, v)| **v == p).unwrap().0.clone();
                    println!("Hash Prev = {p_h}");
                    let j_h = index.commit_registry.iter().find(|(_, v)| **v == j).unwrap().0.clone();
                    println!("Hash curr = {j_h}");
                    for (k, _) in index.merge_commit_changes.get(&j).unwrap() {
                        let k_h = index.commit_registry.iter().find(|(_, v)| *v == k).unwrap().0.clone();
                        println!("Merge hash: {k_h}");
                    }
                }
                index.merge_commit_changes.get(&j)
                    .expect("Expected merge commit")
                    .get(&p)
                    .expect("No branch for given parent")
            };
            prev = Some(j);

            if DEBUG_RESOLVE {
                let commit_name = index.commit_registry.iter().find(|(k, v)| **v == j).unwrap().0.clone();
                println!("Current commit: {} (i = {i}; j = {j})", commit_name);
            }

            for change in changes.iter().copied() {
                if DEBUG_RESOLVE {
                    println!("{change:?}");
                }
                match change {
                    FileChange{kind: FileChangeType::Add, old_name: None, new_name: Some(name)} |
                    FileChange{kind: FileChangeType::ModifySpecial, old_name: Some(_), new_name: Some(name)} => {
                        if is_related {
                            self.register_file(name, *new_contents.get(&name).unwrap());
                            self.added.insert(name); 
                        } else { 
                            let uid = self.register_file(name, *new_contents.get(&name).unwrap());
                            self.pending_negatives.insert(uid);
                        }
                    }
                    FileChange{kind: FileChangeType::Remove, old_name: Some(name), new_name: None} => {
                        if is_related {
                            // If related, 1) not a negative, 2) a positive if not added
                            let uid = self.current_files.remove(&name).expect("Deleting non-existent file");
                            self.negatives.remove(&uid);
                            self.pending_negatives.remove(&uid);
                            if !self.added.contains(&name) {
                                self.positives.insert(uid);
                            }
                        } else {
                            self.current_files.remove(&name);                            
                        }
                        self.added.remove(&name);
                    }
                    FileChange{kind: FileChangeType::Modify, old_name: Some(old_name), new_name: Some(new_name)} => {
                        let uid = *self.current_files.get(&old_name).expect("Modifying non-existent file");

                        if is_related {
                            self.negatives.remove(&uid);
                            self.pending_negatives.remove(&uid);
                            if !self.added.contains(&old_name) {
                                self.positives.insert(uid);
                            }
                            self.added.insert(new_name);    // Must track through renames 

                            if old_name != new_name {
                                self.current_files.remove(&old_name);
                                let new_uid = self.register_file(new_name, *new_contents.get(&new_name).unwrap());
                                self.current_files.insert(new_name, new_uid);
                            }

                        } else {
                            if old_name != new_name {
                                self.current_files.remove(&old_name);
                                let new_uid = self.register_file(new_name, *new_contents.get(&new_name).unwrap());
                                self.current_files.insert(new_name, new_uid);
                            }
                        }

                        if self.added.contains(&old_name) {
                            self.added.remove(&old_name);
                            self.added.insert(new_name);
                        }
                    }
                    _ => { panic!("Invalid file change: {change:?}"); }
                }
            }
        }
        
        let res = ResolvedBucket {
            files: self.entries,
            positive: self.positives,
            negative: self.negatives,
        };
        res
    }

    fn new_commit_contents(&self, index: &Index, j: usize) -> HashMap<usize, FileIndex> {
        if index.delta_by_commit.contains_key(&j) { 
            index.delta_by_commit.get(&j)
                .expect(format!("No delta for commit {j}").as_str())
                .iter()
                .filter_map(|d| {
                    match d {
                        Delta::Add { file_id, index } => Some((*file_id, *index)),
                        Delta::Remove { .. } => None
                    }
                })
                .collect::<HashMap<_, _>>()
        } else {
            // Packed commit
            index.packed_commits.get(&j)
                .expect("Packed commit not found").clone()
        }
    }

    fn register_files(&mut self, files: HashMap<usize, FileIndex>) -> &HashMap<usize, usize> {
        for (key, value) in files {
            let _ = self.register_file(key, value);
        }
        &self.current_files
    }

    fn register_file(&mut self, filename: usize, content: FileIndex) -> usize {
        let uid = self.entries.len();
        self.entries.push(ResolvedBucketEntry { filename, content });
        self.current_files.insert(filename, uid);
        uid
    }

}


trait BucketResolver {
    fn resolve(index: &Index, i: usize) -> (ResolvedBucket, usize) {
        let res = BaseResolver::new().resolve(index, i);
        (Self::transform(res), 0)
    }
    
    fn transform(bucket: ResolvedBucket) -> ResolvedBucket;

}

struct UpfrontResolver;

impl BucketResolver for UpfrontResolver {
    fn transform(bucket: ResolvedBucket) -> ResolvedBucket {
        bucket
    }
}


//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Index Implementation
//////////////////////////////////////////////////////////////////////////////////////////////////

impl IndexLoader {
    pub fn load_from_file(path: impl AsRef<Path>) -> anyhow::Result<Self> {
        let file = std::fs::File::open(path)?;
        let reader = std::io::BufReader::new(file);
        let index: RawIndex = serde_json::from_reader(reader)?;
        let index: Index = index.into();
        let file_mapping = Self::convert_registry(&index.file_registry);
        let commit_mapping = Self::convert_registry(&index.commit_registry);
        let mut rows = Vec::new();
        let mut offset = 0;
        let mut dropped_issues = 0;
        for i in 0..index.pairings.len() {
            let (resolved, failures) = UpfrontResolver::resolve(&index, i);
            if resolved.positive.is_empty() {
                dropped_issues += 1; 
                continue;
            }
            let all_pos = index.pairings[i].files_changed_for_commits
                .iter().flat_map(|x| x.iter())
                .copied()
                .collect::<HashSet<_>>();
            // if resolved.positive.len() > all_pos.len(),
            // then we have a serious problem
            let dropped = all_pos.len() - resolved.positive.len();
            if DEBUG_RESOLVE {
                if dropped > 0 {
                    println!("Issue: {}", index.pairings[i].issue_key);
                    for x in all_pos.difference(&resolved.positive) {
                        println!("{x} -- {}", file_mapping[*x]);
                    }
                }
            }
            let row = IndexRow {
                pairing_index: i,
                sample_count_offset: offset,
                local_sample_count: resolved.positive.len() + resolved.negative.len(),
                true_sample_count: resolved.positive.len(),
                dropped_sample_count: dropped,
                temporal_failures: failures
            };
            offset += row.local_sample_count;
            rows.push(row);
        }
        Ok(
            Self {
                index,
                file_mapping,
                commit_mapping,
                rows,
                dropped_issues,
            }
        )
    }

    pub fn num_features(&self) -> usize {
        self.rows.last()
            .map(|row| row.sample_count_offset + row.local_sample_count)
            .unwrap_or(0)
    }
    
    pub fn total_positive_samples(&self) -> usize {
        self.rows.iter()
            .map(|row| row.true_sample_count)
            .sum()
    }
    
    pub fn dropped_issues(&self) -> usize {
        self.dropped_issues
    }
    
    pub fn num_buckets(&self) -> usize {
        self.rows.len()
    }
    
    pub fn positive_samples_in_range(&self, start: usize, end: usize) -> usize {
        let (start_row_index, start_local_index) = self.resolve_index(start);
        let (end_row_index, end_local_index) = self.resolve_index(end);
        let mut total = 0;
        for index in start_row_index..=end_row_index {
            let row = &self.rows[index];
            if index == start_row_index && start_row_index == end_row_index {
                total += if start_local_index < row.true_sample_count {
                    if end_local_index < row.true_sample_count {
                        end_local_index - start_local_index + 1
                    } else {
                        row.true_sample_count - start_local_index
                    }
                } else {
                    0
                };
            } else if index == start_row_index {
                total += if start_local_index < row.true_sample_count {
                    row.true_sample_count - start_local_index
                } else {
                    0
                };
            } else if index == end_row_index {
                total += if end_local_index < row.true_sample_count {
                    end_local_index + 1
                } else {
                    row.true_sample_count
                };
            } else {
                total += row.true_sample_count;
            }
        }
        total
    }
    
    pub fn get_sample(&self, index: usize) -> anyhow::Result<Sample> {
        let (row_index, local_index) = self.resolve_index(index);
        let row = &self.rows[row_index];
        let pairing = &self.index.pairings[row.pairing_index];
        
        // Get the issue information 
        let issue_key = pairing.issue_key.clone();
        let issue_file_index = pairing.issue_file;
        
        // Get file information 
        let (resolved, _) = UpfrontResolver::resolve(&self.index, row.pairing_index);
        let mut file_ids = resolved.positive.iter()
            .copied()
            .chain(resolved.negative.iter().copied())
            .collect::<Vec<_>>();
        file_ids.sort();
        let file_id = file_ids[local_index];
        let file_info = &resolved.files[file_id];
        let source_file_index = file_info.content;
        let file_name_index = self.index.filename_index[file_info.filename];
        
        // Get label 
        let label = resolved.positive.contains(&file_id);
        
        // Get fixing commits
        let fixing_commits = pairing.resolving_commits
            .iter()
            .copied()
            .map(|i| self.commit_mapping[i].clone())
            .collect();
        
        let sample = Sample {
            issue_key,
            fixing_commits,
            issue_file_index,
            source_file_index,
            source_file_name: self.file_mapping[file_id].clone(),
            file_name_index,
            label,
        };
        Ok(sample)
    }
    
    pub fn get_bucket_sample_collection(&self, 
                                        bucket_index: usize) -> anyhow::Result<SampleBucket> 
    {
        let bucket = &self.rows[bucket_index];
        let pairing = &self.index.pairings[bucket.pairing_index];
        let mut positives = Vec::with_capacity(bucket.true_sample_count);
        let mut negatives = Vec::with_capacity(bucket.local_sample_count - bucket.true_sample_count);

        let (resolved, _) = UpfrontResolver::resolve(&self.index, bucket.pairing_index);
        let mut file_ids = resolved.positive.iter()
            .copied()
            .chain(resolved.negative.iter().copied())
            .collect::<Vec<_>>();
        file_ids.sort();

        let fixing_commits = pairing.resolving_commits
            .iter()
            .copied()
            .map(|i| self.commit_mapping[i].clone())
            .collect::<Vec<_>>();

        for file_id in file_ids {
            let file_info = &resolved.files[file_id];
            let source_file_index = file_info.content;
            let file_name_index = self.index.filename_index[file_info.filename];
            let entry = SampleBucketItem {
                source_file_index,
                file_name_index,
                source_file_name: self.file_mapping[file_id].clone(),
            };
            if resolved.positive.contains(&file_id) {
                positives.push(entry);
            } else {
                negatives.push(entry);
            }
        }
        
        Ok(SampleBucket{
            issue_key: pairing.issue_key.clone(),
            fixing_commits,
            issue_file_index: pairing.issue_file,
            positives,
            negatives,
        })
    }
    
    pub fn get_samples_for_bucket(&self, bucket_index: usize) -> anyhow::Result<Vec<Sample>> {
        let collection = self.get_bucket_sample_collection(bucket_index)?;
        let mut samples = Vec::new();
        let stream = collection.positives
            .into_iter()
            .map(|x| (x, true))
            .chain(
                collection.negatives
                    .into_iter()
                    .map(|x| (x, false))
            );
        for (item, label) in stream {
            let sample = Sample {
                source_file_index: item.source_file_index,
                source_file_name: item.source_file_name,
                file_name_index: item.file_name_index,
                issue_key: collection.issue_key.clone(),
                issue_file_index: collection.issue_file_index,
                fixing_commits: collection.fixing_commits.clone(),
                label
            };
            samples.push(sample);
        }
        Ok(samples)
    }
    
    pub fn get_lightweight_samples_for_bucket(
        &self,
        bucket_index: usize) -> anyhow::Result<Vec<LightweightSample>> 
    {
        let samples = self.get_samples_for_bucket(bucket_index)?;
        let lw = samples.into_iter()
            .map(|sample| {
                let lws = LightweightSample {
                    issue_file_index: sample.issue_file_index.try_into()?,
                    source_file_index: sample.source_file_index.try_into()?,
                    file_name_index: sample.file_name_index.try_into()?,
                    label: sample.label
                };
                Ok(lws)
            })
            .collect::<anyhow::Result<Vec<_>>>()?;
        Ok(lw)
    }

    pub fn get_issue_buckets(&self) -> Vec<Bucket> {
        self.rows.iter()
            .enumerate()
            .map(|(_index, row)| {
                let pairing = &self.index.pairings[row.pairing_index];
                //let commit_id = get_anchor_commit(pairing);
                let commits = pairing.resolving_commits.iter()
                    .copied()
                    .map(|x| self.commit_mapping[x].clone())
                    .collect();
                Bucket {
                    issue_key: pairing.issue_key.clone(),
                    commits,
                    positive_samples: row.true_sample_count,
                    total_samples: row.local_sample_count,
                    sample_offset: row.sample_count_offset,
                    dropped_samples: row.dropped_sample_count,
                    temporal_failures: row.temporal_failures
                }
            })
            .collect()
    }

    fn resolve_index(&self, index: usize) -> (usize,  usize) {
        let row_index = self.rows.partition_point(|r| r.sample_count_offset <= index) - 1;
        let row = &self.rows[row_index];
        (row_index, index - row.sample_count_offset)
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
}


impl Index {
    fn commit_path(&self, start: usize, stop: usize) -> Option<Vec<usize>> {
        if start == stop {
            return Some(vec![start]);
        }
        let empty = Vec::new();
        let mut stack: Vec<(usize, Vec<usize>)> = vec![(stop, Vec::new())];
        while let Some((current, path)) = stack.pop() {
            if current == start {
                return Some(self.make_path(start, stop, path));
            }

            let parents = self.parents.get(&current).unwrap_or(&empty);
            if parents.len() == 0 {
                continue;                           // end of search path 
            } else if parents.len() == 1 {
                stack.push((parents[0], path));     // Next in line 
            } else {
                // Reverse iteration to guarantee branch-DFS
                for (index, parent) in parents.iter().copied().enumerate().rev() {
                    let mut new_path = path.clone();
                    new_path.push(index);
                    stack.push((parent, new_path));
                }
            }
        }        
        None
    }

    fn make_path(&self, start: usize, stop: usize, path: Vec<usize>) -> Vec<usize> {
        let mut result = vec![stop];
        let mut path_index = 0;
        let mut current = stop;
        let empty = Vec::new();
        while current != start {
            let parents = self.parents.get(&current).unwrap_or(&empty);
            if parents.len() == 0 {
                panic!("Failed to find start commit");
            } else if parents.len() == 1 {
                current = parents[0];
            } else {
                current = parents[path[path_index]];
                path_index += 1;
            }
            result.push(current);
        }
        result.reverse();
        result 
    }

    fn resolve_commit(&self, commit_id: usize) -> HashMap<usize, FileIndex> {
        let target = self.parents.get(&commit_id)
            .map(|parents| parents.first().expect("Expected at least one parent"));
        match target {
            None => HashMap::new(),
            Some(parent_id) => self.resolve_code_for_commit(*parent_id)
        }
    }
    
    fn resolve_code_for_commit(&self, commit_id: usize) -> HashMap<usize, FileIndex> {
        let base = self.get_restoration_point(commit_id);
        let mut situation = self.packed_commits.get(&base)
            .unwrap_or_else(|| panic!("Missing packed commit {base}"))
            .clone();

        if DEBUG_RESOLVE {
            println!("Restore base: {situation:?}");
            println!("Restoring {commit_id} from {base}");
        }

        let mut stack = Vec::new();
        let mut current = commit_id;
        while current != base {
            if DEBUG_RESOLVE {
                println!("In path: {current}");
            }
            stack.push(current);
            let parents = self.parents.get(&current)
                .unwrap_or_else(
                    || panic!("Missing parent for commit {current} (start commit should be its own restore point")
                );
            let parent = parents.first().expect("Expected at least one parent");
            current = *parent;
        }
        
        while let Some(commit_id) = stack.pop() {
            let deltas = self.delta_by_commit.get(&commit_id)
                .unwrap_or_else(|| panic!("Missing delta for commit {commit_id}"));
            for delta in deltas {
                if DEBUG_RESOLVE {
                    println!("Apply delta: {delta:?}");
                }
                match delta {
                    Delta::Add{file_id, index} => {
                        situation.insert(*file_id, *index);
                    }
                    Delta::Remove{file_id} => {
                        situation.remove(file_id);
                    }
                }
            }
        }
        situation
    }
    
    fn get_restoration_point(&self, commit_id: usize) -> usize {
        match self.restoration_points.get(&commit_id) {
            Some(&inner) => inner,
            None => panic!("Missing commit {commit_id}")
        }
    }
}

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Deserialization Types and Functions
//////////////////////////////////////////////////////////////////////////////////////////////////


#[derive(Debug)]
#[derive(serde::Deserialize)]
struct RawIndex {
    file_registry: HashMap<String, String>,
    commit_registry: HashMap<String, String>,
    delta_by_commit: HashMap<String, Vec<(String, String, Option<FileIndex>)>>,
    packed_commits: HashMap<String, HashMap<String, FileIndex>>,
    restoration_points: HashMap<String, String>,
    filename_index: Vec<FileIndex>,
    parents: HashMap<String, Vec<String>>,
    pairings: Vec<RawPairing>,
    changes_by_commit: HashMap<String, Vec<(FileChangeType, Option<String>, Option<String>)>>,
    merge_commit_changes: HashMap<String, HashMap<String, Vec<(FileChangeType, Option<String>, Option<String>)>>>,
    commit_order: HashMap<String, usize>,
}

#[derive(Debug, serde::Deserialize)]
struct RawPairing {
    issue_key: String,
    resolving_commits: Vec<String>,
    files_changed_for_commits: Vec<Vec<String>>,
    #[serde(rename = "issue-data")] issue_file: FileIndex,
}


impl From<RawIndex> for Index {
    fn from(mut value: RawIndex) -> Self {
        let file_registry = convert_mapping(value.file_registry);
        let commit_registry = convert_mapping(value.commit_registry);
        
        let delta_by_commit = value.delta_by_commit.into_iter()
            .map(|(commit_id, deltas)| {
                let converted_id = str2num(commit_id, "commit");
                let converted_deltas = deltas.into_iter()
                    .map(|(action, file_id, file_index  )| {
                        match action.as_str() {
                            "add" => Delta::Add {
                                file_id: str2num(file_id, "file"),
                                index: file_index.expect("Empty file index in add action")
                            },
                            "rem" => Delta::Remove {
                                file_id: str2num(file_id, "file")
                            },
                            _ => panic!("Invalid plan file (unknown delta action {})", action)
                        }
                    })
                    .collect();
                (converted_id, converted_deltas)
            })
            .collect();
        
        let packed_commits = value.packed_commits.into_iter()
            .map(|(commit_id, files)| {
                let converted_id = str2num(commit_id, "commit");
                let converted_files = files.into_iter()
                    .map(|(file_id, file_index)| {
                        let converted_file_id = str2num(file_id, "file");
                        (converted_file_id, file_index)
                    })
                    .collect();
                (converted_id, converted_files)
            })
            .collect();

        let restoration_points = value.restoration_points.into_iter()
            .map(|(commit_id, parent_id)| {
                let converted_id = str2num(commit_id, "commit");
                let parent_id = str2num(parent_id, "parent");
                (converted_id, parent_id)
            })
            .collect();
        
        let parents = value.parents.into_iter()
            .map(|(commit_id, parent_ids)| {
                let converted_id = str2num(commit_id, "commit");
                let parent_ids = parent_ids.into_iter()
                    .map(|p| str2num(p, "parent"))
                    .collect();
                (converted_id, parent_ids)
            })
            .collect();

        let pairings = value.pairings.into_iter()
            .map(|p| Pairing {
                issue_key: p.issue_key,
                resolving_commits: p.resolving_commits.into_iter()
                    .map(|x| str2num(x, "resolving commit"))
                    .collect(),
                files_changed_for_commits: p.files_changed_for_commits.into_iter()
                    .map(|files| files.into_iter()
                        .map(|f| str2num(f, "file"))
                        .collect()
                    )
                    .collect(), 
                issue_file: p.issue_file
            })
            .collect();
        
        let filename_index = value.filename_index;

        let mut changes = value.changes_by_commit.into_iter()
            .map(|(k, v)| {
                let converted_key = str2num(k, "commit");
                let converted_value = v.into_iter()
                    .map(|(kind, old, new)| {
                        let old_converted = old.map(|x| str2num(x, "file"));
                        let new_converted = new.map(|x| str2num(x, "file"));
                        FileChange{kind, old_name: old_converted, new_name: new_converted}
                    })
                    .collect();
                (converted_key, converted_value)
            })
            .collect::<HashMap<_, Vec<_>>>();
        let mut changes_by_commit = Vec::new();
        for i in 0..changes.len() {
            changes_by_commit.push(
                changes.remove(&i)
                    .expect("Missing commit sequence number in changes")
            )
        }
        if !changes.is_empty() {
            panic!("There were un-consumed changes");
        }
        
        let merge_commit_changes = value.merge_commit_changes
            .into_iter()
            .map(|(k, v)| {
                let converted_key = str2num(k, "commit");
                let converted_value = v.into_iter()
                    .map(|(x, y)| {
                        let converted_x = str2num(x, "commit");
                        let converted_y = y.into_iter()
                            .map(|(kind, old, new)| {
                                let old_converted = old.map(|x| str2num(x, "file"));
                                let new_converted = new.map(|x| str2num(x, "file"));
                                FileChange{kind, old_name: old_converted, new_name: new_converted}
                            })
                            .collect();
                        (converted_x, converted_y)
                    })
                    .collect();
                (converted_key, converted_value)
            })
            .collect();

        let mut commit_order = Vec::new();
        let mut reversed_order = vec![0; value.commit_order.len()];
        for i in 0..value.commit_order.len() {
            let loc = value.commit_order.remove(&format!("{i}")).expect("Missing sequential commit ID");
            commit_order.push(loc);
            reversed_order[loc] = i; 
        }

        Self {
            commit_registry,
            file_registry,
            delta_by_commit,
            packed_commits,
            restoration_points,
            pairings,
            parents,
            filename_index,
            changes_by_commit,
            merge_commit_changes,
            commit_order,
            reversed_order
        }
    }
}

fn convert_mapping(m: HashMap<String, String>) -> HashMap<String, usize> {
    m.into_iter()
        .map(|(k, v)| (k, v.parse().expect("Invalid plan file")))
        .collect()
}

fn str2num(x: String, kind: &'static str) -> usize {
    x.parse()
        .unwrap_or_else(|_| panic!("Invalid plan file (invalid {kind} ID: {x})"))
}