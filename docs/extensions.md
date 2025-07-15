# Extensions

## Support for *All Future Files* and *Exact Commits*

Here, we provide a description of the extensions we implemented compared to the paper in order to suppor the *All Future Files* and *Exact Commits* versions of the problem. This describes changes to the *Commit to Issue Linking* and *Labelled Sample Generation* steps from the paper.

### Temporal Commit Deletion

We observed that sometimes, issues are linked to by commits with a significant amount of time between them. In such cases, we excluded the later issues because the system has evolved significantly in the meantime. Specifically, we performed the following selection for every project separately: for every issue, we collected all commits linking to said issue. For issues with multiple commits, we computed the difference in timestamp between consecutive commits. We then set a maximum threshold for the difference in timestamps for issues to be merged such that 90% of all differences are within the threshold. This approach automatically adapts to different projects. Note that this step is only necessary for the *All Future Files* and *Exact Commits* versions.

This step is performed after the *Merge Commit Disambiguation* step in the *Commit to Issue Linking* step.

### Lablled Sample Generation Changes
Although not part of the evaluation in this study, our data pipeline does support the generation of labels for the other problem variations (*All Future Files* & *Exact Commits*). We briefly describe the required extensions to the procedure described in the paper here. The assumption here is that we have an issue `I` with a corresponding ordered collection of related commits `C_1, ..., C_n`, where a set of labels is generated for each commit. Commits without positive samples are excluded. If no commits linked to an issue have positive samples, the issue is excluded from the dataset. For both problem settings, we have the option of excluding (true) positives from previous commits from follow up commits (i.e. only predicting the *new* positive samples).

1. Find a path through the commit tree from `C_1` to `C_n` passing through all `C_i`. The existence of such a path is guaranteed because of the path requirement described in the issue to commit linking step.

2. Create a *candidate* set of labels for `C_1` using the procedure described above. Record the set of files after applying `C_1`, and track the positive samples.

3. Until the next related commit, update the set of known files according to the commits in between `C_i` and `C_{i + 1}`. Track positives across renames (e.g. if `A.java` was a positive file for commit `C_1`, and later renamed to `B.java`, then we remember the latter file name as the one of a former positive; If a new file `A.java` is then created later, we count this as a new file which has not been a positive sample before). Discard removed files from the set of known files, and update the set of known files with newly added files.

4. For the next related commit, create its candidate set of labelled samples using the procedure described above. If desired, ignore files that were previously positive according to the tracking described in point (3).

5. Repeat until the last commit in the sequence is reached and processed.


For the *Exact Commits* version of the problem, this is the final collection of sets of labelled files. For the *All Future Files* variant, a backward pass is also required to update each candidate set of positive samples with future positives. This backward pass starts from the last related commit and proceeds as follows:

1. Record the positive samples from `C_n`.

2. Traverse the commits in reverse order, and track the positives samples across all unrelated commits between `C_{i + 1}` and `C_i` -- accounting for additions, removals, and renames as in the forward pass (of course accounting for the fact that we are now moving backward through the commit history).

3. When encountering a related commit, update its set of candidate samples with the tracked set of positives to obtain its final set of samples, and add the positives of the related commit to the tracked set of positives.

4. Repeat until `C_1` is reached and processed.
