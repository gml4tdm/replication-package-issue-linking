//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Imports
//////////////////////////////////////////////////////////////////////////////////////////////////

use std::collections::HashMap;

use super::errors::IndexDecodingError;
use super::shared_types::{Delta, FileChange, FileIndex, Index, Pairing};
use super::shared_types::FileChangeType;

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Types
//////////////////////////////////////////////////////////////////////////////////////////////////

pub type DecodingResult<T> = Result<T, IndexDecodingError>;

type RawChangeList = Vec<(FileChangeType, Option<String>, Option<String>)>;
type RawDeltaList = Vec<(String, String, Option<FileIndex>)>;

#[derive(Debug)]
#[derive(serde::Deserialize)]
pub(super) struct RawIndex {
    file_registry: HashMap<String, String>,
    commit_registry: HashMap<String, String>,
    delta_by_commit: HashMap<String, RawDeltaList>,
    packed_commits: HashMap<String, HashMap<String, FileIndex>>,
    restoration_points: HashMap<String, String>,
    filename_index: Vec<FileIndex>,
    parents: HashMap<String, Vec<String>>,
    pairings: Vec<RawPairing>,
    changes_by_commit: HashMap<String, RawChangeList>,
    merge_commit_changes: HashMap<String, HashMap<String, RawChangeList>>,
    commit_order: HashMap<String, usize>,
    diff_points: HashMap<String, String>,
}

#[derive(Debug, serde::Deserialize)]
struct RawPairing {
    issue_key: String,
    resolving_commits: Vec<String>,
    files_changed_for_commits: Vec<Vec<String>>,
    #[serde(rename = "issue-data")] issue_file: FileIndex,
}

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Delta Conversion
//////////////////////////////////////////////////////////////////////////////////////////////////

impl TryFrom<(String, String, Option<FileIndex>)> for Delta {
    type Error = IndexDecodingError;

    fn try_from(value: (String, String, Option<FileIndex>)) -> Result<Self, Self::Error> {
        let delta = match value.0.as_str() {
            "add" => Delta::Add {
                file_id: str2num(value.1, "deltas_by_commit.<commit>.<file_id@1>")?,
                index: value.2
                    .ok_or_else(|| IndexDecodingError::AddDeltaWithoutFileIndex)?
            },
            "rem" => {
                if !value.2.is_none() {
                    return Err(IndexDecodingError::RemDeltaWithFileIndex);
                }
                Delta::Remove {
                    file_id: str2num(value.1, "deltas_by_commit.<commit>.<file_id@1>")?
                }
            }
            _ => return Err(IndexDecodingError::InvalidDeltaAction {action: value.0})
        };
        Ok(delta)
    }
}

fn try_convert_deltas(
    value: HashMap<String, RawDeltaList>) -> DecodingResult<HashMap<usize, Vec<Delta>>>
{
    value.into_iter()
        .map(|(commit_id, deltas)| {
            let converted_id = str2num(commit_id, "deltas_by_commit.<commit>")?;
            let converted_deltas = deltas.into_iter()
                .map(Delta::try_from)
                .collect::<Result<Vec<_>, _>>()?;
            Ok((converted_id, converted_deltas))
        })
        .collect::<Result<HashMap<_, _>, _>>()
}

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Packed Commit Conversion
//////////////////////////////////////////////////////////////////////////////////////////////////

fn try_convert_packed_commits(
    value: HashMap<String, HashMap<String, FileIndex>>
) -> DecodingResult<HashMap<usize, HashMap<usize, FileIndex>>>
{
    value.into_iter()
        .map(|(commit_id, files)| {
            let converted_id = str2num(commit_id, "packed_commits.<commit>")?;
            let converted_files = files.into_iter()
                .map(|(file_id, file_index)| {
                    let converted_file_id = str2num(
                        file_id, "packed_commits.<commit>.<file_id>"
                    )?;
                    Result::<_, IndexDecodingError>::Ok((converted_file_id, file_index))
                })
                .collect::<Result<HashMap<_, _>, _>>()?;
            Ok((converted_id, converted_files))
        })
        .collect::<Result<HashMap<_, _>, _>>()
}

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Restoration Points
//////////////////////////////////////////////////////////////////////////////////////////////////

fn try_convert_restoration_points(
    v: HashMap<String, String>) -> DecodingResult<HashMap<usize, usize>>
{
    v.into_iter()
        .map(|(commit_id, parent_id)| {
            let converted_id = str2num(commit_id, "restoration_points.<i>.commit")?;
            let parent_id = str2num(parent_id, "restoration_points.<i>.parent")?;
            Ok((converted_id, parent_id))
        })
        .collect()
}

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Parents
//////////////////////////////////////////////////////////////////////////////////////////////////

fn try_convert_parents(
    v: HashMap<String, Vec<String>>) -> DecodingResult<HashMap<usize, Vec<usize>>>
{
    v.into_iter()
        .map(|(commit_id, parent_ids)| {
            let converted_id = str2num(commit_id, "parents.<i>.<commit>")?;
            let parent_ids = parent_ids.into_iter()
                .map(|p| str2num(p, "parents.<i>.<parent>"))
                .collect::<Result<_, _>>()?;
            Ok((converted_id, parent_ids))
        })
        .collect()
}

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Pairings
//////////////////////////////////////////////////////////////////////////////////////////////////

fn try_convert_pairings(
    v: Vec<RawPairing>, order: &[usize]) -> DecodingResult<Vec<Pairing>>
{
    let mut out = v.into_iter()
        .map(|p| {
            let p = Pairing {
                issue_key: p.issue_key,
                resolving_commits: p.resolving_commits.into_iter()
                    .map(|x| str2num(x, "pairings.<i>.resolving_commits"))
                    .collect::<Result<_, _>>()?,
                files_changed_for_commits: p.files_changed_for_commits.into_iter()
                    .map(|files| {
                        let f = files.into_iter()
                            .map(|f|
                                str2num(f, "pairings.<i>.files_changed_for_commits.<i>")
                            )
                            .collect::<Result<Vec<_>, _>>()?;
                        Result::<_, IndexDecodingError>::Ok(f)
                    }
                    )
                    .collect::<Result<_, _>>()?,
                issue_file: p.issue_file
            };
            Result::<_, IndexDecodingError>::Ok(p)
        })
        .collect::<Result<Vec<_>, _>>()?;
    out.sort_by_key(
        |p| p.resolving_commits.iter().copied().map(|c| order[c]).min()
    );
    Ok(out)
}

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Change Lists
//////////////////////////////////////////////////////////////////////////////////////////////////

fn try_convert_changes_by_commit(
    value: HashMap<String, RawChangeList>) -> DecodingResult<Vec<Vec<FileChange>>>
{
    let mut changes = value.into_iter()
        .map(|(k, v)| {
            let converted_key = str2num(k, "changes_by_commit.<commit>")?;
            let converted_value = try_convert_raw_change_list(v)?;
            Result::<_, IndexDecodingError>::Ok((converted_key, converted_value))
        })
        .collect::<Result<HashMap<_, _>, _>>()?;
    let mut changes_by_commit = Vec::new();
    for i in 0..changes.len() {
        changes_by_commit.push(
            changes.remove(&i)
                .ok_or_else(|| IndexDecodingError::NonConsecutiveIndices {
                    field: "changes_by_commit.<commit>".to_string()
                })?
        );
    }
    if !changes.is_empty() {
        return Err(IndexDecodingError::NonConsecutiveIndices {
            field: "changes_by_commit.<commit>".to_string()
        })
    }
    Ok(changes_by_commit)
}

fn try_convert_merge_commit_changes(
    value: HashMap<String, HashMap<String, RawChangeList>>
) -> DecodingResult<HashMap<usize, HashMap<usize, Vec<FileChange>>>>
{
    let out = value.into_iter()
        .map(|(k, v)| {
            let converted_key = str2num(k, "merge_commit_changes.<commit>")?;
            let converted_value = v.into_iter()
                .map(|(x, y)| {
                    let converted_x = str2num(x, "merge_commit_changes.<commit>.<commit>")?;
                    let converted_y = try_convert_raw_change_list(y)?;
                    Result::<_, IndexDecodingError>::Ok((converted_x, converted_y))
                })
                .collect::<Result<_, _>>()?;
            Result::<_, IndexDecodingError>::Ok((converted_key, converted_value))
        })
        .collect::<Result<_, _>>()?;
    Ok(out)
}

fn try_convert_raw_change_list(value: RawChangeList) -> DecodingResult<Vec<FileChange>> {
    let out = value.into_iter()
        .map(|(kind, old, new)| {
            let old_converted = old
                .map(|x| str2num(x, "<change-list>.<i>.old"))
                .transpose()?;
            let new_converted = new
                .map(|x| str2num(x, "<change-list>.<i>.new"))
                .transpose()?;
            Result::<_, IndexDecodingError>::Ok(
                FileChange{kind, old_name: old_converted, new_name: new_converted}
            )
        })
        .collect::<Result<Vec<_>, _>>()?;
    Ok(out)
}

//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////
// Conversion
//////////////////////////////////////////////////////////////////////////////////////////////////


impl TryFrom<RawIndex> for Index {
    type Error = IndexDecodingError;

    fn try_from(mut value: RawIndex) -> Result<Self, Self::Error> {
        let file_registry = convert_mapping(
            value.file_registry, "file_registry"
        )?;
        let commit_registry = convert_mapping(
            value.commit_registry, "commit_registry"
        )?;

        let mut commit_order = Vec::new();
        let mut reversed_order = vec![0; value.commit_order.len()];
        for i in 0..value.commit_order.len() {
            let loc = value.commit_order
                .remove(&format!("{i}"))
                .ok_or_else(|| IndexDecodingError::NonConsecutiveIndices {
                    field: "commit_order.<commit>".to_string()
                })?;
            commit_order.push(loc);
            reversed_order[loc] = i;
        }

        let delta_by_commit = try_convert_deltas(value.delta_by_commit)?;
        let packed_commits = try_convert_packed_commits(value.packed_commits)?;
        let restoration_points = try_convert_restoration_points(value.restoration_points)?;
        let parents = try_convert_parents(value.parents)?;
        let pairings = try_convert_pairings(value.pairings, &commit_order)?;
        let filename_index = value.filename_index;
        let changes_by_commit = try_convert_changes_by_commit(value.changes_by_commit)?;
        let merge_commit_changes = try_convert_merge_commit_changes(value.merge_commit_changes)?;
        
        let diff_points = value.diff_points.into_iter()
            .map(|(k, v)| {
                let c_k = str2num(k, "diff_points.<commit>")?;
                let c_v = str2num(v, "diff_points.<commit>")?;
                Result::<_, IndexDecodingError>::Ok((c_k, c_v))
            })
            .collect::<Result<_, _>>()?;

        let out = Self {
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
            reversed_order,
            diff_points
        };
        Ok(out)
    }
}


fn convert_mapping(
    m: HashMap<String, String>,
    field: &'static str) -> DecodingResult<HashMap<String, usize>>
{
    m.into_iter()
        .map(
            |(k, v)| Ok((k, str2num(v, field)?))
        )
        .collect::<Result<_, _>>()
}

fn str2num(x: String, field: &'static str) -> DecodingResult<usize> {
    x.parse()
        .map_err(|e| IndexDecodingError::InvalidInteger {
            field: field.to_string(),
            value: x.to_string(),
            error: format!("{e}")
        })
}
