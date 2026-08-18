# Submissions

Put your results file here via a pull request. See
[../docs/SUBMITTING.md](../docs/SUBMITTING.md) for the full step-by-step.

- One file per submission, named `Results_NN_x.csv`
  (`NN` = your participant id, `x` = submission number, starting at 1).
- Header `row_id,yaw_offset`, exactly 1,064,641 rows, no NaN/empty values.
- Files are tracked with **Git LFS** (see [../.gitattributes](../.gitattributes)).
- Submissions are immutable once merged — submit a new `x` to revise.

## Code

Also submit the code you used to produce your predictions separately or in the same pull
request, under `Code/PARTICIPANT_NN/`. We archive it alongside the results on
Zenodo after the challenge ends.
