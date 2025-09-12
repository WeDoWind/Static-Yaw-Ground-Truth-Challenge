# Static Yaw Ground Truth Challenge

This is the official results submission repository for the [WeDoWind Static Yaw Ground Truth Challenge](https://community.wedowind.ch/posts/open-data-exploration-challenge-4-static-yaw-ground-truth-challenge).

Here you will also be able to see the current leaderboard.

In order to submit a result, you need to open a new issue in the Issues tab above and select "Submit results". You are then asked to enter a title, a team name and a version identifier.
Via drag and drop you can then upload your results submission csv file, which should have the following specifications:

1. No header
2. No NaNs or empty fields
3. Exactly N comma separated floats

The contents of the file should look something like this
```shell
1.1,3.5,2.12312,8.123,100.105,...,5.4321
```

Based on this we will calculate the root mean squared error (RMSE) and the mean absolute error (MAE), which will be listed in the leaderboard below.
The leaderboard only shows the best scores per team in case of multiple submissions.

# Leaderboard

<!-- leaderboard:start -->
| Rank | Team | RMSE | MAE | Version | Submission |
|---:|:-----|----:|----:|:--:|:--|
| 1 | WeDoWinders | 2.0 | 4.0 | v1 | [issue #7](https://github.com/WeDoWind/Static-Yaw-Ground-Truth-Challenge/issues/7) |
<!-- leaderboard:end -->
