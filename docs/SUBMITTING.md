# Submitting your results

Submissions are made by **pull request**. A bot validates the file format
automatically; once a maintainer merges your PR, your RMSE and MAE are computed
against the held-out ground truth and appear on the
[leaderboard](https://wedowind.github.io/Static-Yaw-Ground-Truth-Challenge/).

The challenge deadline is **May 31st, 2026**. You may submit multiple variations
before then; the leaderboard shows every submission, not just your best one.

## File format

- **Filename:** `Results_NN_x.csv` — `NN` = your participant id (e.g. `01`),
  `x` = submission number (`1` for your first submission).
- **Header:** exactly `row_id,yaw_offset`
- **Rows:** exactly **1,064,641**, one per public test `row_id`
  (`pub_00000000` … `pub_01064640`).
- **Values:** a finite number in every `yaw_offset` cell — no NaN, no empty fields.

### Final submission (private test set)

The final ranking (presented June 17th) is scored on the held-out **private**
test set. The final submission file is named `Results_NN_final.csv` and must
cover the private rows instead: exactly **3,627,380** rows,
`priv_00000000` … `priv_03627379`, same `row_id,yaw_offset` header. Details on
when/how to submit the final file will be announced before the deadline.

## Code

Please also submit the code you used to produce your predictions, in the same
pull request, under `Submissions/Code/PARTICIPANT_NN/`. Include whatever a
reader would need to understand your approach (scripts/notebooks, and a short
note on how to run them); no need to include large data files. We archive the
challenge results — including this code — on Zenodo after the challenge ends.

## Steps

1. Create a branch named `sub/Submission_NN_x` (matching your file).
2. Add your file as `Submissions/Results_NN_x.csv`, and your code under
   `Submissions/Code/PARTICIPANT_NN/`.
   > Submission CSVs are tracked with **Git LFS**. Run `git lfs install` once,
   > then `git add Submissions/Results_NN_x.csv` as usual — LFS handles the rest.
3. Commit and push the branch, then open a **pull request** against `main`.
4. The **Validate submission** check runs automatically and reports any format
   problems with your results file. Fix them and push again until it's green.
5. A maintainer merges your PR. Scoring runs and the leaderboard updates within
   a few minutes.

## Notes

- A submission PR must **only add** files under `Submissions/` — your
  `Results_NN_x.csv` plus, optionally, files under `Submissions/Code/PARTICIPANT_NN/`.
  Editing other files (or changing an existing submission) will fail validation.
- Submissions are immutable once merged. To revise, submit a new `x`.
