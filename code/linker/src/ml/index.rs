use std::collections::{BTreeSet, HashMap, HashSet};

use super::shared_types::{FileIndex, Index, Delta};

impl Index {
    pub(super) fn commit_path(&self, to_visit: Vec<usize>) -> Option<Vec<usize>> {
        if to_visit.is_empty() {
            return None;
        }
        
        if to_visit.len() == 1 {
            return Some(to_visit);
        }

        let start = to_visit.first().copied().unwrap();
        let stop = to_visit.iter().last().copied().unwrap();
        let targets = BTreeSet::from_iter(to_visit);
        
        let empty = Vec::new();
        let mut stack: Vec<(usize, Vec<usize>, BTreeSet<usize>)> = vec![
            (stop, Vec::new(), BTreeSet::from_iter(vec![stop]))
        ];
        let mut seen = HashSet::new();
        while let Some((current, path, mut found)) = stack.pop() {
            if current == start {
                // let rev = self.commit_registry.iter()
                //     .map(|(k, v)| (*v, k.clone()))
                //     .collect::<HashMap<_, _>>();
                // let t = self.make_path(start, stop, path.clone());
                // let nice = t.into_iter()
                //     .map(|id| rev.get(&id).unwrap()).collect::<Vec<_>>();
                // println!("Found candidate path: {:?}", nice);
                
                found.insert(current);
                if found == targets {
                    return Some(self.make_path(start, stop, path));
                } else {
                    continue;   // end of path 
                }
            }
            
            let key = (current, found.clone());
            if seen.contains(&key) {
                continue;
            }
            seen.insert(key);
            
            let is_linked = if targets.contains(&current) {
                found.insert(current);
                true
            } else {
                false
            };

            let have_diff_point = self.diff_points.contains_key(&current);
            if is_linked && have_diff_point {
                // We can safely skip to the diff point;
                //  - It is a linear sequence of commits
                //  - The commits contain no links (i.e. not on the path)
                //  - All changes in the path should be in the merge commit
                let diff_point = self.diff_points.get(&current).copied().unwrap();
                let mut new_path = path.clone();
                // TODO: check me
                new_path.push(1);       // diff point should always take the branching path
                stack.push((diff_point, new_path, found));
            } else {
                let parents = self.parents.get(&current).unwrap_or(&empty);
                if parents.is_empty() {
                    continue;                           // end of search path 
                } else if parents.len() == 1 {
                    stack.push((parents[0], path, found));     // Next in line 
                } else {
                    // We want the path closest to main, so we perform DFS
                    for (index, parent) in parents.iter().copied().enumerate().rev() {
                        let mut new_path = path.clone();
                        new_path.push(index);
                        stack.push((parent, new_path, found.clone()));
                    }
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
            if parents.is_empty() {
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

    pub(super) fn resolve_commit(&self, commit_id: usize) -> HashMap<usize, FileIndex> {
        // Resolve the code for the given commit.
        // First try the diff_point; otherwise, use the first parent.
        let target = self.diff_points.get(&commit_id)
            .copied()
            .or_else(
                || self.parents.get(&commit_id)
                    .map(|parents| 
                        parents.first().expect("Expected at least one parent")
                    )
                    .copied()
            );
        //let target = self.parents.get(&commit_id)
        //    .map(|parents| parents.first().expect("Expected at least one parent"));
        match target {
            None => HashMap::new(),
            Some(parent_id) => self.resolve_code_for_commit(parent_id)
        }
    }

    fn resolve_code_for_commit(&self, commit_id: usize) -> HashMap<usize, FileIndex> {
        let base = self.get_restoration_point(commit_id);
        let mut situation = self.packed_commits.get(&base)
            .unwrap_or_else(|| panic!("Missing packed commit {base}"))
            .clone();

        let mut stack = Vec::new();
        let mut current = commit_id;
        while current != base {
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