use std::collections::HashMap;

#[derive(Debug)]
pub(super) struct Index {
    pub(super) file_registry: HashMap<String, usize>,
    pub(super) commit_registry: HashMap<String, usize>,
    pub(super) delta_by_commit: HashMap<usize, Vec<Delta>>,
    pub(super) packed_commits: HashMap<usize, HashMap<usize, FileIndex>>,
    pub(super) restoration_points: HashMap<usize, usize>,
    pub(super) parents: HashMap<usize, Vec<usize>>,
    pub(super) pairings: Vec<Pairing>,
    pub(super) filename_index: Vec<FileIndex>,
    pub(super) changes_by_commit: Vec<Vec<FileChange>>,
    pub(super) merge_commit_changes: HashMap<usize, HashMap<usize, Vec<FileChange>>>,
    pub(super) commit_order: Vec<usize>,
    pub(super) reversed_order: Vec<usize>,
    pub(super) diff_points: HashMap<usize, usize>,
}

#[derive(Debug)]
pub(super) struct Pairing {
    pub(super) issue_key: String,
    pub(super) resolving_commits: Vec<usize>,
    pub(super) files_changed_for_commits: Vec<Vec<usize>>,
    pub(super) issue_file: FileIndex,
}

#[derive(Debug, Copy, Clone, PartialEq, Eq)]
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
pub(super) enum Delta {
    Add{file_id: usize, index:FileIndex },
    Remove{file_id: usize}
}

#[derive(Debug, Copy, Clone, serde::Deserialize)]
pub(super) enum FileChangeType {
    #[serde(rename = "add")] Add,
    #[serde(rename = "mod")] Modify,
    #[serde(rename = "rem")] Remove,
    #[serde(rename = "mod-special")] ModifySpecial
}

#[derive(Debug, Copy, Clone)]
pub(super) struct FileChange {
    pub(super) kind: FileChangeType,
    pub(super) old_name: Option<usize>,
    pub(super) new_name: Option<usize>
}
