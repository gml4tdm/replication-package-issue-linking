# Results for Tuning Preprocessing

This tables presented averages over all methods + projects.

Highest performing method per metric (row) is underlined.

*Lower, Stemming*  and *Lower, Stemming, Sub Tokens* perform best, with the former achieving better top 1 performance, and the latter achieving better top 5 and top 10 performance. The first option is presented in the paper, but this replication package contains statistical analysis for both.


| Metric       | No~Processing | Sub Tokens | Lower | Lower, Sub Tokens | Lower, Stemming  | Lower, Stemming, Sub Tokens |
|--------------|---------------|------------|-------|-------------------|------------------|-----------------------------|
| Precision@1  | 0.299         | 0.293      | 0.315 | 0.308             | <ins>0.318</ins> | 0.303                       |
| Precision@5  | 0.145         | 0.159      | 0.155 | 0.165             | 0.157            | <ins>0.166</ins>            |
| Precision@10 | 0.100         | 0.109      | 0.107 | 0.115             | 0.109            | <ins>0.116</ins>            |
| hit@5        | 0.526         | 0.552      | 0.558 | 0.567             | 0.565            | <ins>0.569</ins>            |
| hit@10       | 0.628         | 0.652      | 0.661 | 0.678             | 0.668            | <ins>0.680</ins>            |
| Recall@1     | 0.179         | 0.172      | 0.189 | 0.181             | <ins>0.190</ins> | 0.177                       |
| Recall@5     | 0.362         | 0.391      | 0.388 | <ins>0.404</ins>  | 0.392            | 0.404                       |
| Recall@10    | 0.459         | 0.491      | 0.487 | 0.514             | 0.495            | <ins>0.515</ins>            |
| r-Precision  | 0.249         | 0.255      | 0.265 | 0.266             | <ins>0.267</ins> | 0.264                       |
| MRR          | 0.408         | 0.414      | 0.430 | 0.429             | <ins>0.435</ins> | 0.427                       |
