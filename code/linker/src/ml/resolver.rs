//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Imports
//////////////////////////////////////////////////////////////////////////////////////////////////

use std::collections::{HashMap, HashSet};

use super::errors::ResolverError;
use super::shared_types::{Delta, FileChange, FileChangeType, FileIndex, Index, Pairing};

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Types
//////////////////////////////////////////////////////////////////////////////////////////////////

type ResolverResult<T> = Result<T, ResolverError>;

#[derive(Debug)]
pub(super) struct Resolver {
    // Settings
    transitive_future: bool,
    reuse_old: bool
}

#[derive(Debug)]
pub(super) struct ResolutionResult {
    pub(super) commits: Vec<usize>,
    pub(super) samples_by_commit: HashMap<usize, Vec<(usize, bool)>>,
    pub(super) data: Vec<ResolvedEntry>
}

#[derive(Debug)]
pub(super) struct ResolvedEntry {
    pub(super) filename: usize,
    pub(super) content: FileIndex
}

#[derive(Debug)]
struct ResolverState {
    current_files: HashMap<usize, usize>,
    entries: Vec<ResolvedEntry>,
}

impl ResolverState {
    fn new() -> Self {
        Self { current_files: HashMap::new(), entries: Vec::new() }
    }
    
    fn register_file(&mut self, filename: usize, content: FileIndex) -> usize {
        let current = self.current_files.get(&filename).copied();
        if let Some(uid) = current {
            if self.entries[uid].content == content {
                return uid;
            }
        }
        let uid = self.entries.len();
        self.entries.push(ResolvedEntry { filename, content });
        self.current_files.insert(filename, uid);
        uid
    }
}

#[derive(Debug)]
struct BackwardChange {
    original_change: FileChange,
    uid_old: Option<usize>
}

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Implementation
//////////////////////////////////////////////////////////////////////////////////////////////////

impl Resolver {
    pub fn new(reuse_old: bool, transitive_future: bool) -> Self {
        Self {reuse_old, transitive_future}
    }
    
    pub fn resolve(&self,
                   index: &Index, 
                   pairing_index: usize)  -> ResolverResult<ResolutionResult>
    {
        let pairing = self.preflight_checks(
            index, pairing_index
        )?;
        let path = self.get_path(index, pairing);
        
        let mut entries = ResolverState::new();
        
        let (samples_by_commit, files_after_last, backward_changes) = self.forward_pass(
            index, 
            pairing,
            path.clone(), 
            &mut entries
        );

        let samples_by_commit = self.backward_pass(
            path.clone(),
            samples_by_commit,
            files_after_last,
            backward_changes
        );
        
        let commits = path.into_iter()
            .filter(|i| pairing.resolving_commits.contains(i))
            .collect();
        
        let data = entries.entries;
        
        let res = ResolutionResult {
            commits,
            samples_by_commit,
            data
        };
        
        Ok(res)
    }
    
    fn preflight_checks<'a, 'b: 'a>(&'a self,
                                    index: &'b Index, 
                                    pairing_index: usize) -> ResolverResult<&'b Pairing>
    {
        let pairing = index.pairings.get(pairing_index)
            .ok_or_else(|| ResolverError::IndexOutOfBounds {
                field: "pairings".to_string(), index: pairing_index
            })?;
        Ok(pairing)
    }
    
    fn get_path(&self, index: &Index, pairing: &Pairing) -> Vec<usize> {
        // All checks in this function should be enforced by the index generator;
        // Errors point to in invalid index.
        
        let mut target_commits = pairing.resolving_commits.to_vec();
        target_commits.sort_by_key(|c| index.commit_order[*c]);
        let path = index.commit_path(target_commits);
        // let path = path.expect("Failed to find commit path");
        
        if let Some(p) = path {
            p
        } else {
            let hashes = pairing.resolving_commits.iter().copied()
                .map(|x| index.commit_registry.iter()
                    .find(|(_, y)| **y == x)
                    .unwrap()
                    .0
                    .clone()
                )
                .collect::<Vec<_>>();
            panic!("Failed to resolve a path for commits: {hashes:?}");
        }
    }
    
    fn forward_pass(&self,
                    index: &Index, 
                    pairing: &Pairing, 
                    path: Vec<usize>, 
                    entries: &mut ResolverState) -> (
        HashMap<usize, Vec<(usize, usize, bool)>>,
        Vec<usize>,
        Vec<Vec<BackwardChange>>
    )
    {
        let mut files = index.resolve_commit(path[0])
            .into_iter()
            .map(|(k, v)| (k, (entries.register_file(k, v), false)))
            .collect::<HashMap<_, _>>();
        let mut samples_by_commit: HashMap<usize, Vec<(usize, usize, bool)>> = HashMap::new();
        
        let mut next_in_line = 0;
        let n_related_commits = pairing.resolving_commits.len();
        let mut previous_commit = None;
        
        let mut backward_changes = Vec::new();
        
        let mut line = pairing.resolving_commits.clone();
        line.sort_by_cached_key(|i| index.commit_order[*i]);
        if line != pairing.resolving_commits {
            // This warning is annoying; let's remove it
            // println!(
            //     "WARNING: Order of resolving commits is not topological order (issue = {}) [{:?}; {:?}]",
            //     pairing.issue_key, line, pairing.resolving_commits
            // )
        }

        for i in path {
            let is_related = next_in_line < n_related_commits
                && i == line[next_in_line];
            if is_related {
                next_in_line += 1;
            }
            let changes = self.get_changes_for_commit(index, i, previous_commit);
            let content = self.get_new_commit_content(index, i);
            let _ = previous_commit.replace(i);
            
            if is_related {
                samples_by_commit.insert(i, self.get_labels_for_commit(changes, &mut files));
            }
            
            let mut backward_changes_for_commit = Vec::new();
            for change in changes.iter().copied() {
                let backward_change = self.dispatch_forward_change(
                    change, &content, &mut files, entries
                );
                backward_changes_for_commit.push(backward_change);
            }
            backward_changes.push(backward_changes_for_commit);
        }
        
        let files_after_last = files.into_keys().collect();
        (samples_by_commit, files_after_last, backward_changes)
    }
    
    fn dispatch_forward_change(&self,
                               change: FileChange,
                               content: &HashMap<usize, FileIndex>,
                               files: &mut HashMap<usize, (usize, bool)>,
                               entries: &mut ResolverState) -> BackwardChange
    {
        match change {
            FileChange { kind: FileChangeType::Add, old_name: None, new_name: Some(name) } => {
                let content = content.get(&name)
                    .copied()
                    .expect("No content for new file");
                files.insert(
                    name,
                    (entries.register_file(name, content), false)
                );
                BackwardChange { original_change: change, uid_old: None }
            }
            FileChange { kind: FileChangeType::Remove, old_name: Some(name), new_name: None } => {
                let (uid, _) = files.remove(&name).expect("Removing non-existent file");
                BackwardChange { original_change: change, uid_old: Some(uid) }
            }
            FileChange { kind: FileChangeType::Modify, old_name: Some(old_name), new_name: Some(new_name) } => {
                let content = content.get(&new_name)
                    .copied()
                    .expect("Missing content for modified file");
                // Will re-use uid if possible
                let uid = entries.register_file(new_name, content);
                let (old_uid, state) = files.get(&old_name)
                    .copied()
                    .expect("Missing old file");
                if old_name != new_name {
                    let _ = files.remove(&old_name);
                }
                files.insert(new_name, (uid, state));
                BackwardChange { original_change: change, uid_old: Some(old_uid) }
            }
            FileChange { kind: FileChangeType::ModifySpecial, old_name: Some(_old_name), new_name: Some(new_name) } => {
                // Equivalent to a new file
                let content = content.get(&new_name)
                    .copied()
                    .expect("No content for new (mod special) file");
                files.insert(
                    new_name,
                    (entries.register_file(new_name, content), false)
                );
                BackwardChange { original_change: change, uid_old: None }
            }
            _ => panic!("Invalid change: {change:?}")
        }    
    }
    
    fn backward_pass(
        &self,
        path: Vec<usize>,
        mut samples_by_commit: HashMap<usize, Vec<(usize, usize, bool)>>,
        files_after_last: Vec<usize>,
        backward_changes: Vec<Vec<BackwardChange>>
    ) -> HashMap<usize, Vec<(usize, bool)>>
    {
        let mut new_samples_by_commit = HashMap::new();
        let mut files = files_after_last.into_iter()
            .map(|name| (name, false))
            .collect::<HashMap<_, _>>();
        let stream = path.into_iter().rev().zip(
            backward_changes.into_iter().rev()
        );
        for (commit, changes) in stream {
            // First, apply backward change
            let is_related = samples_by_commit.contains_key(&commit);
            for change in changes {
                self.dispatch_backward_change(change,
                                              &mut files, 
                                              is_related && self.transitive_future);
            }
            
            // Next, apply transitive label transformations;
            // Also update with the labels of the current commit.
            if let Some(current_labels) = samples_by_commit.remove(&commit) {
                let new_labels = current_labels.into_iter()
                    .map(|(name, uid, label)| {
                        let transitive_positive = files.get(&name)
                            .copied()
                            .unwrap_or_else(|| panic!("Missing file {} in backward pass", name));
                        (uid, label || transitive_positive)
                    })
                    .collect::<Vec<_>>();
                new_samples_by_commit.insert(commit, new_labels);
            }
        }
        
        new_samples_by_commit
    }
    
    fn dispatch_backward_change(&self,
                                change: BackwardChange,
                                files: &mut HashMap<usize, bool>, 
                                flag: bool)
    {
        match change.original_change {
            FileChange { kind: FileChangeType::Add, old_name: None, new_name: Some(name) } => {
                let _ = files.remove(&name);
            }
            FileChange { kind: FileChangeType::Remove, old_name: Some(name), new_name: None } => {
                files.insert(name, flag);
            }
            FileChange { kind: FileChangeType::Modify, old_name: Some(old_name), new_name: Some(new_name) } => {
                let old_flag = files.remove(&new_name).expect("Missing new file in backward pass");
                files.insert(old_name, flag || old_flag);
            }
            FileChange { kind: FileChangeType::ModifySpecial, old_name: Some(_old_name), new_name: Some(new_name) } => {
                let _ = files.remove(&new_name);
            }
            _ => panic!("Invalid change: {:?}", change.original_change)
        }
    }

    fn get_changes_for_commit<'a, 'b: 'a>(&'a self,
                                          index: &'b Index, 
                                          commit: usize, 
                                          previous_commit: Option<usize>) -> &'b Vec<FileChange>
    {
        let n_parents = index.parents.get(&commit)
            .map(|x| x.len())
            .unwrap_or(0);
        if n_parents <= 1 {
            // Normal commit
            &index.changes_by_commit[commit]
        } else {
            // Merge commit
            let prev = match previous_commit {
                None => {
                    // This commit is the first in the sequence.
                    // We need to take the path with respect to the 'incoming' 
                    // branch, since the merge commit _must_ 
                    // correspond to that branch 
                    if n_parents != 2 {
                        panic!("Merge commits which are first in sequence with > 2 parents are not supported");
                    }
                    let parents = index.parents.get(&commit)
                        .expect("No parents for merge commit");
                    parents[1]
                }
                Some(p) => p
            };
            index.merge_commit_changes.get(&commit)
                .expect("Cannot find changes for merge commit")
                .get(&prev)
                .expect("No branch for given parent")
        }
    }
    
    fn get_new_commit_content(&self, 
                              index: &Index,
                              commit: usize) -> HashMap<usize, FileIndex>
    {
        if index.delta_by_commit.contains_key(&commit) {
            index.delta_by_commit.get(&commit)
                .expect(format!("No delta for commit {commit}").as_str())
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
            index.packed_commits.get(&commit)
                .expect("Packed commit not found").clone()
        }
    }
    
    fn get_labels_for_commit(&self, 
                             changes: &[FileChange], 
                             files: &mut HashMap<usize, (usize, bool)>) -> Vec<(usize, usize, bool)> 
    {
        let mut changed_for_commit = HashSet::new();
        for change in changes.iter().copied() {
            if matches!(change.kind, FileChangeType::Modify | FileChangeType::Remove) {
                changed_for_commit.insert(
                    change.old_name.expect("No old name")
                );
            }
        }
        let mut labels_for_commit = Vec::new();
        let stream = files.iter()
            .map(|(k, (u, p))| (*k, (*u, *p)));
        for (name, (uid, previous_positive)) in stream {
            if previous_positive && !self.reuse_old {
                continue;
            }
            labels_for_commit.push(
                (name, uid, changed_for_commit.contains(&name))
            );
        }
        for name in changed_for_commit {
            files.entry(name).and_modify(|x| x.1 = true);
        }
        labels_for_commit
    }
}
