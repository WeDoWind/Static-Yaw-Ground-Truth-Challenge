# Static Yaw Ground Truth Challenge

This is the official leaderboard repository for the [WeDoWind Static Yaw Ground Truth Challenge](https://community.wedowind.ch/posts/open-data-exploration-challenge-4-static-yaw-ground-truth-challenge).

Based on your submissions we calculate the root mean squared error (RMSE) and the mean absolute error (MAE), which are listed in the [leaderboard](https://wedowind.github.io/Static-Yaw-Ground-Truth-Challenge/).
The leaderboard shows every submission, not just your best one.

## Submitting

Submissions are made by pull request — see **[docs/SUBMITTING.md](docs/SUBMITTING.md)**.
In short: add your `Submissions/Results_NN_x.csv` on a branch, open a PR, and once
the automated format check passes and a maintainer merges it, your scores appear
on the leaderboard automatically. The ground truth is held privately; scoring runs
in a separate evaluation repository.

Please also submit the code you used to produce your predictions, in the same
pull request, under `Submissions/Code/PARTICIPANT_NN/`. We use this to archive
the challenge results on Zenodo.
