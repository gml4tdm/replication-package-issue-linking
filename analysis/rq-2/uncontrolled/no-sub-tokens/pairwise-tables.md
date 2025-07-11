# lsa-1000

### Specific

| Metric                    | Combination  | Avro         | Maven            | Tika             | Thrift           | Tomee | Spring Data Mongodb | Spring Roo       |
|---------------------------|--------------|--------------|------------------|------------------|------------------|-------|---------------------|------------------|
| Bug / Improvement         | Precision@1  | N/A          | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / Improvement         | Precision@5  | N/A          | **0.031 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / Improvement         | Precision@10 | N/A          | **0.009 (&lt;)** | **0.028 (&lt;)** | N/A              | N/A   | N/A                 | N/A              |
| Bug / Improvement         | hit@5        | N/A          | 0.298 (&lt;)     | N/A              | 0.063 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Improvement         | hit@10       | 0.168 (&gt;) | 0.139 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / Improvement         | Recall@1     | 0.654 (&lt;) | N/A              | N/A              | 0.205 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Improvement         | Recall@5     | 0.173 (&gt;) | N/A              | **0.004 (&gt;)** | **0.000 (&gt;)** | N/A   | N/A                 | N/A              |
| Bug / Improvement         | Recall@10    | 0.109 (&gt;) | N/A              | **0.003 (&gt;)** | **0.001 (&gt;)** | N/A   | N/A                 | 0.304 (&gt;)     |
| Bug / Improvement         | r-Precision  | N/A          | **0.004 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / Improvement         | MRR          | 0.160 (&lt;) | **0.012 (&lt;)** | N/A              | 0.132 (&gt;)     | N/A   | N/A                 | N/A              |
| Improvement / New Feature | Precision@1  | N/A          | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Improvement / New Feature | Precision@5  | N/A          | **0.009 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Improvement / New Feature | Precision@10 | N/A          | **0.005 (&gt;)** | **0.024 (&lt;)** | N/A              | N/A   | N/A                 | N/A              |
| Improvement / New Feature | hit@5        | N/A          | **0.011 (&gt;)** | N/A              | 0.201 (&gt;)     | N/A   | N/A                 | N/A              |
| Improvement / New Feature | hit@10       | 0.565 (&gt;) | **0.004 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Improvement / New Feature | Recall@1     | 0.432 (&gt;) | N/A              | N/A              | 0.155 (&gt;)     | N/A   | N/A                 | N/A              |
| Improvement / New Feature | Recall@5     | 0.419 (&gt;) | N/A              | 0.057 (&lt;)     | **0.000 (&gt;)** | N/A   | N/A                 | N/A              |
| Improvement / New Feature | Recall@10    | 0.152 (&gt;) | N/A              | 0.257 (&gt;)     | **0.000 (&gt;)** | N/A   | N/A                 | **0.025 (&lt;)** |
| Improvement / New Feature | r-Precision  | N/A          | **0.008 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Improvement / New Feature | MRR          | 0.903 (&gt;) | **0.000 (&lt;)** | N/A              | 0.196 (&gt;)     | N/A   | N/A                 | N/A              |
| Improvement / Task        | Precision@1  | N/A          | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Improvement / Task        | Precision@5  | N/A          | **0.031 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Improvement / Task        | Precision@10 | N/A          | **0.009 (&lt;)** | **0.028 (&gt;)** | N/A              | N/A   | N/A                 | N/A              |
| Improvement / Task        | hit@5        | N/A          | 0.298 (&gt;)     | N/A              | 0.063 (&gt;)     | N/A   | N/A                 | N/A              |
| Improvement / Task        | hit@10       | 0.168 (&gt;) | 0.139 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Improvement / Task        | Recall@1     | 0.654 (&gt;) | N/A              | N/A              | 0.205 (&gt;)     | N/A   | N/A                 | N/A              |
| Improvement / Task        | Recall@5     | 0.173 (&gt;) | N/A              | **0.004 (&gt;)** | **0.000 (&gt;)** | N/A   | N/A                 | N/A              |
| Improvement / Task        | Recall@10    | 0.109 (&gt;) | N/A              | **0.003 (&gt;)** | **0.001 (&gt;)** | N/A   | N/A                 | 0.304 (&lt;)     |
| Improvement / Task        | r-Precision  | N/A          | **0.004 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Improvement / Task        | MRR          | 0.160 (&gt;) | **0.012 (&gt;)** | N/A              | 0.132 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / New Feature         | Precision@1  | N/A          | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / New Feature         | Precision@5  | N/A          | **0.009 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / New Feature         | Precision@10 | N/A          | **0.005 (&lt;)** | **0.024 (&lt;)** | N/A              | N/A   | N/A                 | N/A              |
| Bug / New Feature         | hit@5        | N/A          | **0.011 (&lt;)** | N/A              | 0.201 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / New Feature         | hit@10       | 0.565 (&gt;) | **0.004 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / New Feature         | Recall@1     | 0.432 (&gt;) | N/A              | N/A              | 0.155 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / New Feature         | Recall@5     | 0.419 (&gt;) | N/A              | 0.057 (&gt;)     | **0.000 (&gt;)** | N/A   | N/A                 | N/A              |
| Bug / New Feature         | Recall@10    | 0.152 (&gt;) | N/A              | 0.257 (&gt;)     | **0.000 (&gt;)** | N/A   | N/A                 | **0.025 (&gt;)** |
| Bug / New Feature         | r-Precision  | N/A          | **0.008 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / New Feature         | MRR          | 0.903 (&gt;) | **0.000 (&lt;)** | N/A              | 0.196 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Task                | Precision@1  | N/A          | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / Task                | Precision@5  | N/A          | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / Task                | Precision@10 | N/A          | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A   | N/A                 | N/A              |
| Bug / Task                | hit@5        | N/A          | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Task                | hit@10       | 1.000 (&gt;) | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / Task                | Recall@1     | 1.000 (&gt;) | N/A              | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Task                | Recall@5     | 1.000 (&gt;) | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Task                | Recall@10    | 1.000 (&gt;) | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | N/A                 | 1.000 (&gt;)     |
| Bug / Task                | r-Precision  | N/A          | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / Task                | MRR          | 1.000 (&gt;) | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| New Feature / Task        | Precision@1  | N/A          | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A              |
| New Feature / Task        | Precision@5  | N/A          | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| New Feature / Task        | Precision@10 | N/A          | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A              | N/A   | N/A                 | N/A              |
| New Feature / Task        | hit@5        | N/A          | 1.000 (&gt;)     | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| New Feature / Task        | hit@10       | 1.000 (&lt;) | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| New Feature / Task        | Recall@1     | 1.000 (&lt;) | N/A              | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A              |
| New Feature / Task        | Recall@5     | 1.000 (&lt;) | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| New Feature / Task        | Recall@10    | 1.000 (&lt;) | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | N/A                 | 1.000 (&gt;)     |
| New Feature / Task        | r-Precision  | N/A          | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| New Feature / Task        | MRR          | 1.000 (&lt;) | 1.000 (&gt;)     | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A              |


### Holdout

| Metric                    | Combination  | Avro | Maven            | Tika | Thrift           | Tomee | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------|------------------|------|------------------|-------|---------------------|------------|
| Bug / Improvement         | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A  | **0.036 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A  | N/A              | N/A  | **0.001 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | N/A  | N/A              | N/A  | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | r-Precision  | N/A  | **0.025 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A  | **0.014 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A  | **0.036 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A  | N/A              | N/A  | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | N/A  | N/A              | N/A  | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | r-Precision  | N/A  | **0.025 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A  | **0.002 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A  | **0.036 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A  | N/A              | N/A  | **0.001 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | N/A  | N/A              | N/A  | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | r-Precision  | N/A  | **0.025 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A  | **0.014 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A  | **0.036 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A  | N/A              | N/A  | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | N/A  | N/A              | N/A  | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | r-Precision  | N/A  | **0.025 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A  | **0.002 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@10    | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | r-Precision  | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | r-Precision  | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A  | 1.000 (&lt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |



# bm25

### Specific

| Metric                    | Combination  | Avro             | Maven            | Tika             | Thrift           | Tomee            | Spring Data Mongodb | Spring Roo   |
|---------------------------|--------------|------------------|------------------|------------------|------------------|------------------|---------------------|--------------|
| Bug / Improvement         | Precision@1  | N/A              | 0.882 (&lt;)     | 0.051 (&gt;)     | 0.358 (&gt;)     | N/A              | N/A                 | N/A          |
| Bug / Improvement         | Precision@5  | N/A              | 0.491 (&lt;)     | N/A              | 0.130 (&gt;)     | 0.111 (&gt;)     | N/A                 | 0.359 (&lt;) |
| Bug / Improvement         | Precision@10 | 0.850 (&lt;)     | 0.236 (&lt;)     | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Bug / Improvement         | hit@5        | **0.036 (&gt;)** | 0.606 (&lt;)     | **0.010 (&gt;)** | 0.077 (&gt;)     | **0.004 (&lt;)** | N/A                 | 0.202 (&lt;) |
| Bug / Improvement         | hit@10       | 0.381 (&gt;)     | 0.300 (&lt;)     | N/A              | 0.087 (&gt;)     | **0.001 (&lt;)** | N/A                 | 0.139 (&lt;) |
| Bug / Improvement         | Recall@1     | 0.143 (&gt;)     | N/A              | **0.000 (&gt;)** | 0.262 (&gt;)     | N/A              | N/A                 | N/A          |
| Bug / Improvement         | Recall@5     | **0.008 (&gt;)** | 0.673 (&lt;)     | **0.000 (&gt;)** | **0.000 (&gt;)** | **0.001 (&gt;)** | N/A                 | N/A          |
| Bug / Improvement         | Recall@10    | 0.078 (&gt;)     | 0.794 (&lt;)     | **0.000 (&gt;)** | **0.001 (&gt;)** | **0.000 (&lt;)** | N/A                 | N/A          |
| Bug / Improvement         | r-Precision  | 0.133 (&lt;)     | 0.343 (&lt;)     | N/A              | 0.540 (&gt;)     | N/A              | N/A                 | N/A          |
| Bug / Improvement         | MRR          | 0.089 (&gt;)     | 0.184 (&lt;)     | **0.002 (&gt;)** | 0.087 (&gt;)     | **0.009 (&lt;)** | N/A                 | N/A          |
| Improvement / New Feature | Precision@1  | N/A              | **0.048 (&gt;)** | 0.105 (&lt;)     | 0.057 (&gt;)     | N/A              | N/A                 | N/A          |
| Improvement / New Feature | Precision@5  | N/A              | **0.001 (&gt;)** | N/A              | **0.002 (&gt;)** | 0.924 (&gt;)     | N/A                 | 0.106 (&gt;) |
| Improvement / New Feature | Precision@10 | 0.272 (&gt;)     | **0.000 (&gt;)** | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Improvement / New Feature | hit@5        | **0.032 (&gt;)** | **0.001 (&gt;)** | 0.644 (&gt;)     | **0.000 (&gt;)** | 0.720 (&gt;)     | N/A                 | 0.173 (&gt;) |
| Improvement / New Feature | hit@10       | **0.037 (&gt;)** | **0.000 (&gt;)** | N/A              | **0.020 (&gt;)** | 0.799 (&gt;)     | N/A                 | 0.139 (&gt;) |
| Improvement / New Feature | Recall@1     | 0.574 (&gt;)     | N/A              | **0.004 (&lt;)** | **0.001 (&gt;)** | N/A              | N/A                 | N/A          |
| Improvement / New Feature | Recall@5     | **0.008 (&gt;)** | **0.017 (&gt;)** | **0.004 (&gt;)** | **0.000 (&gt;)** | 0.930 (&gt;)     | N/A                 | N/A          |
| Improvement / New Feature | Recall@10    | **0.004 (&gt;)** | **0.010 (&gt;)** | **0.002 (&gt;)** | **0.000 (&gt;)** | 0.953 (&gt;)     | N/A                 | N/A          |
| Improvement / New Feature | r-Precision  | 0.928 (&gt;)     | **0.007 (&gt;)** | N/A              | **0.012 (&gt;)** | N/A              | N/A                 | N/A          |
| Improvement / New Feature | MRR          | 0.067 (&gt;)     | **0.000 (&gt;)** | 0.241 (&lt;)     | **0.001 (&gt;)** | 0.735 (&gt;)     | N/A                 | N/A          |
| Improvement / Task        | Precision@1  | N/A              | 0.882 (&gt;)     | 0.051 (&gt;)     | 0.358 (&lt;)     | N/A              | N/A                 | N/A          |
| Improvement / Task        | Precision@5  | N/A              | 0.491 (&gt;)     | N/A              | 0.130 (&gt;)     | 0.111 (&lt;)     | N/A                 | 0.359 (&gt;) |
| Improvement / Task        | Precision@10 | 0.850 (&lt;)     | 0.236 (&gt;)     | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Improvement / Task        | hit@5        | **0.036 (&gt;)** | 0.606 (&gt;)     | **0.010 (&gt;)** | 0.077 (&lt;)     | **0.004 (&gt;)** | N/A                 | 0.202 (&gt;) |
| Improvement / Task        | hit@10       | 0.381 (&lt;)     | 0.300 (&gt;)     | N/A              | 0.087 (&gt;)     | **0.001 (&gt;)** | N/A                 | 0.139 (&gt;) |
| Improvement / Task        | Recall@1     | 0.143 (&gt;)     | N/A              | **0.000 (&gt;)** | 0.262 (&lt;)     | N/A              | N/A                 | N/A          |
| Improvement / Task        | Recall@5     | **0.008 (&gt;)** | 0.673 (&gt;)     | **0.000 (&gt;)** | **0.000 (&gt;)** | **0.001 (&gt;)** | N/A                 | N/A          |
| Improvement / Task        | Recall@10    | 0.078 (&gt;)     | 0.794 (&gt;)     | **0.000 (&gt;)** | **0.001 (&gt;)** | **0.000 (&gt;)** | N/A                 | N/A          |
| Improvement / Task        | r-Precision  | 0.133 (&gt;)     | 0.343 (&gt;)     | N/A              | 0.540 (&lt;)     | N/A              | N/A                 | N/A          |
| Improvement / Task        | MRR          | 0.089 (&gt;)     | 0.184 (&gt;)     | **0.002 (&gt;)** | 0.087 (&lt;)     | **0.009 (&gt;)** | N/A                 | N/A          |
| Bug / New Feature         | Precision@1  | N/A              | **0.048 (&gt;)** | 0.105 (&gt;)     | 0.057 (&gt;)     | N/A              | N/A                 | N/A          |
| Bug / New Feature         | Precision@5  | N/A              | **0.001 (&gt;)** | N/A              | **0.002 (&gt;)** | 0.924 (&gt;)     | N/A                 | 0.106 (&gt;) |
| Bug / New Feature         | Precision@10 | 0.272 (&gt;)     | **0.000 (&lt;)** | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Bug / New Feature         | hit@5        | **0.032 (&gt;)** | **0.001 (&gt;)** | 0.644 (&gt;)     | **0.000 (&gt;)** | 0.720 (&gt;)     | N/A                 | 0.173 (&gt;) |
| Bug / New Feature         | hit@10       | **0.037 (&gt;)** | **0.000 (&lt;)** | N/A              | **0.020 (&gt;)** | 0.799 (&gt;)     | N/A                 | 0.139 (&gt;) |
| Bug / New Feature         | Recall@1     | 0.574 (&gt;)     | N/A              | **0.004 (&gt;)** | **0.001 (&gt;)** | N/A              | N/A                 | N/A          |
| Bug / New Feature         | Recall@5     | **0.008 (&gt;)** | **0.017 (&gt;)** | **0.004 (&gt;)** | **0.000 (&gt;)** | 0.930 (&gt;)     | N/A                 | N/A          |
| Bug / New Feature         | Recall@10    | **0.004 (&gt;)** | **0.010 (&gt;)** | **0.002 (&gt;)** | **0.000 (&gt;)** | 0.953 (&gt;)     | N/A                 | N/A          |
| Bug / New Feature         | r-Precision  | 0.928 (&gt;)     | **0.007 (&lt;)** | N/A              | **0.012 (&gt;)** | N/A              | N/A                 | N/A          |
| Bug / New Feature         | MRR          | 0.067 (&gt;)     | **0.000 (&gt;)** | 0.241 (&gt;)     | **0.001 (&gt;)** | 0.735 (&gt;)     | N/A                 | N/A          |
| Bug / Task                | Precision@1  | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A              | N/A                 | N/A          |
| Bug / Task                | Precision@5  | N/A              | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | 1.000 (&gt;) |
| Bug / Task                | Precision@10 | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Bug / Task                | hit@5        | 1.000 (&gt;)     | 1.000 (&lt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | 1.000 (&gt;) |
| Bug / Task                | hit@10       | 1.000 (&gt;)     | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | 1.000 (&gt;) |
| Bug / Task                | Recall@1     | 1.000 (&gt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A              | N/A                 | N/A          |
| Bug / Task                | Recall@5     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| Bug / Task                | Recall@10    | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| Bug / Task                | r-Precision  | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A              | 1.000 (&gt;)     | N/A              | N/A                 | N/A          |
| Bug / Task                | MRR          | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| New Feature / Task        | Precision@1  | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&lt;)     | N/A              | N/A                 | N/A          |
| New Feature / Task        | Precision@5  | N/A              | 1.000 (&lt;)     | N/A              | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A                 | 1.000 (&lt;) |
| New Feature / Task        | Precision@10 | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A              | N/A              | N/A                 | N/A          |
| New Feature / Task        | hit@5        | 1.000 (&lt;)     | 1.000 (&lt;)     | 1.000 (&gt;)     | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A                 | 1.000 (&lt;) |
| New Feature / Task        | hit@10       | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A              | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A                 | 1.000 (&gt;) |
| New Feature / Task        | Recall@1     | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&lt;)     | N/A              | N/A                 | N/A          |
| New Feature / Task        | Recall@5     | 1.000 (&lt;)     | 1.000 (&lt;)     | 1.000 (&gt;)     | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| New Feature / Task        | Recall@10    | 1.000 (&lt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| New Feature / Task        | r-Precision  | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A              | 1.000 (&lt;)     | N/A              | N/A                 | N/A          |
| New Feature / Task        | MRR          | 1.000 (&lt;)     | 1.000 (&lt;)     | 1.000 (&gt;)     | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A                 | N/A          |


### Holdout

| Metric                    | Combination  | Avro | Maven            | Tika             | Thrift           | Tomee            | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------|------------------|------------------|------------------|------------------|---------------------|------------|
| Bug / Improvement         | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A              | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A  | N/A              | N/A              | **0.016 (&lt;)** | N/A              | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A  | 0.144 (&gt;)     | N/A              | N/A              | N/A              | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A  | N/A              | N/A              | **0.001 (&lt;)** | N/A              | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A  | 0.150 (&gt;)     | N/A              | **0.031 (&lt;)** | N/A              | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A  | N/A              | **0.008 (&lt;)** | **0.011 (&lt;)** | N/A              | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A  | N/A              | **0.000 (&lt;)** | **0.000 (&lt;)** | **0.022 (&lt;)** | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | N/A  | N/A              | **0.000 (&lt;)** | **0.000 (&lt;)** | **0.026 (&lt;)** | N/A                 | N/A        |
| Bug / Improvement         | r-Precision  | N/A  | N/A              | N/A              | 0.054 (&lt;)     | N/A              | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A  | 0.083 (&gt;)     | N/A              | **0.007 (&lt;)** | N/A              | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A              | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A  | N/A              | N/A              | **0.003 (&gt;)** | N/A              | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A  | **0.018 (&lt;)** | N/A              | N/A              | N/A              | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A  | N/A              | N/A              | **0.000 (&gt;)** | N/A              | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A  | **0.012 (&lt;)** | N/A              | **0.019 (&gt;)** | N/A              | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A  | N/A              | 0.058 (&gt;)     | **0.001 (&gt;)** | N/A              | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A  | N/A              | **0.022 (&gt;)** | **0.000 (&gt;)** | 0.215 (&lt;)     | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | N/A  | N/A              | **0.015 (&gt;)** | **0.000 (&gt;)** | 0.232 (&lt;)     | N/A                 | N/A        |
| Improvement / New Feature | r-Precision  | N/A  | N/A              | N/A              | **0.017 (&gt;)** | N/A              | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A  | **0.004 (&lt;)** | N/A              | **0.001 (&gt;)** | N/A              | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A              | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A  | N/A              | N/A              | **0.016 (&gt;)** | N/A              | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A  | 0.144 (&lt;)     | N/A              | N/A              | N/A              | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A  | N/A              | N/A              | **0.001 (&gt;)** | N/A              | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A  | 0.150 (&lt;)     | N/A              | **0.031 (&gt;)** | N/A              | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A  | N/A              | **0.008 (&lt;)** | **0.011 (&gt;)** | N/A              | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A  | N/A              | **0.000 (&lt;)** | **0.000 (&gt;)** | **0.022 (&lt;)** | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | N/A  | N/A              | **0.000 (&lt;)** | **0.000 (&gt;)** | **0.026 (&lt;)** | N/A                 | N/A        |
| Improvement / Task        | r-Precision  | N/A  | N/A              | N/A              | 0.054 (&gt;)     | N/A              | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A  | 0.083 (&lt;)     | N/A              | **0.007 (&gt;)** | N/A              | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A              | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A  | N/A              | N/A              | **0.003 (&lt;)** | N/A              | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A  | **0.018 (&gt;)** | N/A              | N/A              | N/A              | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A  | N/A              | N/A              | **0.000 (&lt;)** | N/A              | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A  | **0.012 (&gt;)** | N/A              | **0.019 (&lt;)** | N/A              | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A  | N/A              | 0.058 (&lt;)     | **0.001 (&lt;)** | N/A              | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A  | N/A              | **0.022 (&lt;)** | **0.000 (&lt;)** | 0.215 (&lt;)     | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | N/A  | N/A              | **0.015 (&lt;)** | **0.000 (&lt;)** | 0.232 (&lt;)     | N/A                 | N/A        |
| Bug / New Feature         | r-Precision  | N/A  | N/A              | N/A              | **0.017 (&lt;)** | N/A              | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A  | **0.004 (&gt;)** | N/A              | **0.001 (&lt;)** | N/A              | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A              | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A              | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A              | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A              | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A  | 1.000 (&gt;)     | N/A              | 1.000 (&lt;)     | N/A              | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A  | N/A              | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A  | N/A              | 1.000 (&lt;)     | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A                 | N/A        |
| Bug / Task                | Recall@10    | N/A  | N/A              | 1.000 (&lt;)     | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A                 | N/A        |
| Bug / Task                | r-Precision  | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A              | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A  | 1.000 (&gt;)     | N/A              | 1.000 (&lt;)     | N/A              | N/A                 | N/A        |
| New Feature / Task        | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A              | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A              | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A              | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A              | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A  | 1.000 (&lt;)     | N/A              | 1.000 (&lt;)     | N/A              | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A  | N/A              | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A              | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A  | N/A              | 1.000 (&lt;)     | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | N/A  | N/A              | 1.000 (&lt;)     | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A                 | N/A        |
| New Feature / Task        | r-Precision  | N/A  | N/A              | N/A              | 1.000 (&gt;)     | N/A              | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A  | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | N/A              | N/A                 | N/A        |



# lsa-500

### Specific

| Metric                    | Combination  | Avro         | Maven            | Tika             | Thrift           | Tomee | Spring Data Mongodb | Spring Roo       |
|---------------------------|--------------|--------------|------------------|------------------|------------------|-------|---------------------|------------------|
| Bug / Improvement         | Precision@1  | N/A          | N/A              | N/A              | 0.095 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Improvement         | Precision@5  | N/A          | 0.085 (&lt;)     | N/A              | 0.063 (&lt;)     | N/A   | N/A                 | N/A              |
| Bug / Improvement         | Precision@10 | N/A          | **0.008 (&lt;)** | 0.059 (&lt;)     | N/A              | N/A   | N/A                 | N/A              |
| Bug / Improvement         | hit@5        | N/A          | 0.311 (&lt;)     | N/A              | **0.023 (&gt;)** | N/A   | N/A                 | N/A              |
| Bug / Improvement         | hit@10       | N/A          | 0.172 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / Improvement         | Recall@1     | N/A          | N/A              | N/A              | **0.025 (&gt;)** | N/A   | N/A                 | N/A              |
| Bug / Improvement         | Recall@5     | 0.157 (&lt;) | N/A              | **0.001 (&gt;)** | **0.001 (&gt;)** | N/A   | N/A                 | N/A              |
| Bug / Improvement         | Recall@10    | 0.317 (&gt;) | N/A              | **0.001 (&gt;)** | **0.002 (&gt;)** | N/A   | N/A                 | 0.674 (&gt;)     |
| Bug / Improvement         | r-Precision  | 0.536 (&lt;) | **0.008 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / Improvement         | MRR          | 0.098 (&lt;) | **0.003 (&lt;)** | N/A              | **0.028 (&gt;)** | N/A   | N/A                 | N/A              |
| Improvement / New Feature | Precision@1  | N/A          | N/A              | N/A              | 0.143 (&gt;)     | N/A   | N/A                 | N/A              |
| Improvement / New Feature | Precision@5  | N/A          | **0.038 (&gt;)** | N/A              | 0.805 (&gt;)     | N/A   | N/A                 | N/A              |
| Improvement / New Feature | Precision@10 | N/A          | **0.004 (&gt;)** | 0.056 (&lt;)     | N/A              | N/A   | N/A                 | N/A              |
| Improvement / New Feature | hit@5        | N/A          | 0.051 (&lt;)     | N/A              | 0.260 (&gt;)     | N/A   | N/A                 | N/A              |
| Improvement / New Feature | hit@10       | N/A          | **0.004 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Improvement / New Feature | Recall@1     | N/A          | N/A              | N/A              | **0.022 (&gt;)** | N/A   | N/A                 | N/A              |
| Improvement / New Feature | Recall@5     | 0.744 (&gt;) | N/A              | **0.036 (&lt;)** | **0.001 (&gt;)** | N/A   | N/A                 | N/A              |
| Improvement / New Feature | Recall@10    | 0.317 (&gt;) | N/A              | 0.195 (&gt;)     | **0.000 (&gt;)** | N/A   | N/A                 | **0.028 (&lt;)** |
| Improvement / New Feature | r-Precision  | 0.352 (&gt;) | **0.008 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Improvement / New Feature | MRR          | 0.972 (&gt;) | **0.000 (&gt;)** | N/A              | 0.103 (&gt;)     | N/A   | N/A                 | N/A              |
| Improvement / Task        | Precision@1  | N/A          | N/A              | N/A              | 0.095 (&gt;)     | N/A   | N/A                 | N/A              |
| Improvement / Task        | Precision@5  | N/A          | 0.085 (&lt;)     | N/A              | 0.063 (&gt;)     | N/A   | N/A                 | N/A              |
| Improvement / Task        | Precision@10 | N/A          | **0.008 (&lt;)** | 0.059 (&lt;)     | N/A              | N/A   | N/A                 | N/A              |
| Improvement / Task        | hit@5        | N/A          | 0.311 (&gt;)     | N/A              | **0.023 (&gt;)** | N/A   | N/A                 | N/A              |
| Improvement / Task        | hit@10       | N/A          | 0.172 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Improvement / Task        | Recall@1     | N/A          | N/A              | N/A              | **0.025 (&gt;)** | N/A   | N/A                 | N/A              |
| Improvement / Task        | Recall@5     | 0.157 (&gt;) | N/A              | **0.001 (&gt;)** | **0.001 (&gt;)** | N/A   | N/A                 | N/A              |
| Improvement / Task        | Recall@10    | 0.317 (&gt;) | N/A              | **0.001 (&gt;)** | **0.002 (&gt;)** | N/A   | N/A                 | 0.674 (&lt;)     |
| Improvement / Task        | r-Precision  | 0.536 (&gt;) | **0.008 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Improvement / Task        | MRR          | 0.098 (&gt;) | **0.003 (&gt;)** | N/A              | **0.028 (&gt;)** | N/A   | N/A                 | N/A              |
| Bug / New Feature         | Precision@1  | N/A          | N/A              | N/A              | 0.143 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / New Feature         | Precision@5  | N/A          | **0.038 (&lt;)** | N/A              | 0.805 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / New Feature         | Precision@10 | N/A          | **0.004 (&lt;)** | 0.056 (&lt;)     | N/A              | N/A   | N/A                 | N/A              |
| Bug / New Feature         | hit@5        | N/A          | 0.051 (&lt;)     | N/A              | 0.260 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / New Feature         | hit@10       | N/A          | **0.004 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / New Feature         | Recall@1     | N/A          | N/A              | N/A              | **0.022 (&gt;)** | N/A   | N/A                 | N/A              |
| Bug / New Feature         | Recall@5     | 0.744 (&gt;) | N/A              | **0.036 (&gt;)** | **0.001 (&gt;)** | N/A   | N/A                 | N/A              |
| Bug / New Feature         | Recall@10    | 0.317 (&gt;) | N/A              | 0.195 (&gt;)     | **0.000 (&gt;)** | N/A   | N/A                 | **0.028 (&gt;)** |
| Bug / New Feature         | r-Precision  | 0.352 (&gt;) | **0.008 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / New Feature         | MRR          | 0.972 (&gt;) | **0.000 (&lt;)** | N/A              | 0.103 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Task                | Precision@1  | N/A          | N/A              | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Task                | Precision@5  | N/A          | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Task                | Precision@10 | N/A          | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A   | N/A                 | N/A              |
| Bug / Task                | hit@5        | N/A          | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Task                | hit@10       | N/A          | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / Task                | Recall@1     | N/A          | N/A              | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Task                | Recall@5     | 1.000 (&gt;) | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| Bug / Task                | Recall@10    | 1.000 (&gt;) | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | N/A                 | 1.000 (&gt;)     |
| Bug / Task                | r-Precision  | 1.000 (&lt;) | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| Bug / Task                | MRR          | 1.000 (&gt;) | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| New Feature / Task        | Precision@1  | N/A          | N/A              | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A              |
| New Feature / Task        | Precision@5  | N/A          | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| New Feature / Task        | Precision@10 | N/A          | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A              | N/A   | N/A                 | N/A              |
| New Feature / Task        | hit@5        | N/A          | 1.000 (&gt;)     | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A              |
| New Feature / Task        | hit@10       | N/A          | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| New Feature / Task        | Recall@1     | N/A          | N/A              | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A              |
| New Feature / Task        | Recall@5     | 1.000 (&lt;) | N/A              | 1.000 (&gt;)     | 1.000 (&lt;)     | N/A   | N/A                 | N/A              |
| New Feature / Task        | Recall@10    | 1.000 (&lt;) | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | N/A                 | 1.000 (&gt;)     |
| New Feature / Task        | r-Precision  | 1.000 (&lt;) | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A              |
| New Feature / Task        | MRR          | 1.000 (&lt;) | 1.000 (&gt;)     | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A              |


### Holdout

| Metric                    | Combination  | Avro | Maven            | Tika             | Thrift           | Tomee | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------|------------------|------------------|------------------|-------|---------------------|------------|
| Bug / Improvement         | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A  | **0.030 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A  | N/A              | N/A              | **0.029 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A  | N/A              | **0.035 (&lt;)** | **0.002 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | N/A  | N/A              | N/A              | **0.001 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | r-Precision  | N/A  | **0.029 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A  | **0.007 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A  | **0.030 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A  | N/A              | N/A              | **0.029 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A  | N/A              | 0.193 (&gt;)     | **0.001 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | N/A  | N/A              | N/A              | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | r-Precision  | N/A  | **0.029 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A  | **0.001 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A  | **0.030 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A  | N/A              | N/A              | **0.029 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A  | N/A              | **0.035 (&lt;)** | **0.002 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | N/A  | N/A              | N/A              | **0.001 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | r-Precision  | N/A  | **0.029 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A  | **0.007 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A  | **0.030 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A  | N/A              | N/A              | **0.029 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A  | N/A              | 0.193 (&lt;)     | **0.001 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | N/A  | N/A              | N/A              | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | r-Precision  | N/A  | **0.029 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A  | **0.001 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A  | N/A              | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@10    | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | r-Precision  | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A  | N/A              | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | r-Precision  | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |



# rvsm

### Specific

| Metric                    | Combination  | Avro             | Maven            | Tika             | Thrift           | Tomee        | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------------------|------------------|------------------|------------------|--------------|---------------------|------------|
| Bug / Improvement         | Precision@1  | N/A              | N/A              | N/A              | N/A              | 0.723 (&gt;) | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | 0.519 (&lt;)     | N/A              | N/A              | N/A              | 0.476 (&gt;) | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | 0.632 (&lt;)     | 0.063 (&lt;)     | N/A              | N/A              | 0.666 (&gt;) | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | 0.129 (&gt;)     | N/A              | N/A              | **0.046 (&gt;)** | 0.830 (&gt;) | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | 0.271 (&gt;)     | 0.313 (&lt;)     | N/A              | **0.049 (&gt;)** | 0.698 (&gt;) | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A              | N/A              | **0.030 (&gt;)** | 0.149 (&gt;)     | 0.612 (&gt;) | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | 0.119 (&gt;)     | N/A              | **0.000 (&gt;)** | **0.001 (&gt;)** | 0.679 (&gt;) | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | **0.041 (&gt;)** | N/A              | **0.000 (&gt;)** | **0.000 (&gt;)** | 0.470 (&gt;) | N/A                 | N/A        |
| Bug / Improvement         | r-Precision  | N/A              | N/A              | N/A              | N/A              | 0.500 (&gt;) | 0.120 (&lt;)        | N/A        |
| Bug / Improvement         | MRR          | 0.163 (&gt;)     | 0.052 (&lt;)     | N/A              | 0.083 (&gt;)     | 0.197 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A              | N/A              | N/A              | N/A              | 0.208 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | 0.802 (&gt;)     | N/A              | N/A              | N/A              | 0.276 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | 0.632 (&gt;)     | **0.023 (&gt;)** | N/A              | N/A              | 0.312 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | 0.464 (&gt;)     | N/A              | N/A              | 0.338 (&gt;)     | 0.401 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | **0.020 (&gt;)** | 0.055 (&lt;)     | N/A              | 0.141 (&gt;)     | 0.450 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A              | N/A              | **0.035 (&lt;)** | 0.199 (&gt;)     | 0.234 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | 0.463 (&gt;)     | N/A              | 0.068 (&lt;)     | **0.001 (&gt;)** | 0.337 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | **0.033 (&gt;)** | N/A              | **0.050 (&gt;)** | **0.000 (&gt;)** | 0.457 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | r-Precision  | N/A              | N/A              | N/A              | N/A              | 0.500 (&gt;) | 0.120 (&gt;)        | N/A        |
| Improvement / New Feature | MRR          | 0.238 (&gt;)     | **0.000 (&gt;)** | N/A              | 0.206 (&gt;)     | 0.540 (&gt;) | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A              | N/A              | N/A              | N/A              | 0.723 (&lt;) | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | 0.519 (&gt;)     | N/A              | N/A              | N/A              | 0.476 (&lt;) | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | 0.632 (&lt;)     | 0.063 (&lt;)     | N/A              | N/A              | 0.666 (&lt;) | N/A                 | N/A        |
| Improvement / Task        | hit@5        | 0.129 (&gt;)     | N/A              | N/A              | **0.046 (&gt;)** | 0.830 (&lt;) | N/A                 | N/A        |
| Improvement / Task        | hit@10       | 0.271 (&lt;)     | 0.313 (&gt;)     | N/A              | **0.049 (&gt;)** | 0.698 (&lt;) | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A              | N/A              | **0.030 (&lt;)** | 0.149 (&gt;)     | 0.612 (&gt;) | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | 0.119 (&gt;)     | N/A              | **0.000 (&gt;)** | **0.001 (&gt;)** | 0.679 (&gt;) | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | **0.041 (&gt;)** | N/A              | **0.000 (&gt;)** | **0.000 (&gt;)** | 0.470 (&gt;) | N/A                 | N/A        |
| Improvement / Task        | r-Precision  | N/A              | N/A              | N/A              | N/A              | 0.500 (&lt;) | 0.120 (&gt;)        | N/A        |
| Improvement / Task        | MRR          | 0.163 (&gt;)     | 0.052 (&gt;)     | N/A              | 0.083 (&gt;)     | 0.197 (&lt;) | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A              | N/A              | N/A              | N/A              | 0.208 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | 0.802 (&gt;)     | N/A              | N/A              | N/A              | 0.276 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | 0.632 (&gt;)     | **0.023 (&lt;)** | N/A              | N/A              | 0.312 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | 0.464 (&gt;)     | N/A              | N/A              | 0.338 (&gt;)     | 0.401 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | **0.020 (&gt;)** | 0.055 (&lt;)     | N/A              | 0.141 (&gt;)     | 0.450 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A              | N/A              | **0.035 (&gt;)** | 0.199 (&gt;)     | 0.234 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | 0.463 (&gt;)     | N/A              | 0.068 (&gt;)     | **0.001 (&gt;)** | 0.337 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | **0.033 (&gt;)** | N/A              | **0.050 (&gt;)** | **0.000 (&gt;)** | 0.457 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | r-Precision  | N/A              | N/A              | N/A              | N/A              | 0.500 (&gt;) | 0.120 (&gt;)        | N/A        |
| Bug / New Feature         | MRR          | 0.238 (&gt;)     | **0.000 (&lt;)** | N/A              | 0.206 (&gt;)     | 0.540 (&gt;) | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A              | N/A              | N/A              | N/A              | 1.000 (&gt;) | N/A                 | N/A        |
| Bug / Task                | Precision@5  | 1.000 (&lt;)     | N/A              | N/A              | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| Bug / Task                | Precision@10 | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| Bug / Task                | hit@5        | 1.000 (&gt;)     | N/A              | N/A              | 1.000 (&gt;)     | 1.000 (&lt;) | N/A                 | N/A        |
| Bug / Task                | hit@10       | 1.000 (&gt;)     | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&gt;) | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A              | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;) | N/A                 | N/A        |
| Bug / Task                | Recall@5     | 1.000 (&gt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;) | N/A                 | N/A        |
| Bug / Task                | Recall@10    | 1.000 (&gt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;) | N/A                 | N/A        |
| Bug / Task                | r-Precision  | N/A              | N/A              | N/A              | N/A              | 1.000 (&gt;) | 1.000 (&gt;)        | N/A        |
| Bug / Task                | MRR          | 1.000 (&gt;)     | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | Precision@1  | N/A              | N/A              | N/A              | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | 1.000 (&lt;)     | N/A              | N/A              | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | hit@5        | 1.000 (&lt;)     | N/A              | N/A              | 1.000 (&gt;)     | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | hit@10       | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A              | N/A              | 1.000 (&gt;)     | 1.000 (&lt;)     | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | r-Precision  | N/A              | N/A              | N/A              | N/A              | 1.000 (&lt;) | 1.000 (&gt;)        | N/A        |
| New Feature / Task        | MRR          | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A              | 1.000 (&lt;)     | 1.000 (&lt;) | N/A                 | N/A        |


### Holdout

| Metric                    | Combination  | Avro | Maven            | Tika             | Thrift           | Tomee        | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------|------------------|------------------|------------------|--------------|---------------------|------------|
| Bug / Improvement         | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A  | N/A              | N/A              | N/A              | 0.152 (&lt;) | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A  | N/A              | **0.004 (&lt;)** | **0.003 (&lt;)** | N/A          | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | N/A  | N/A              | **0.001 (&lt;)** | **0.000 (&lt;)** | 0.133 (&lt;) | N/A                 | N/A        |
| Bug / Improvement         | r-Precision  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A  | **0.040 (&gt;)** | N/A              | N/A              | 0.106 (&lt;) | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A  | N/A              | N/A              | N/A              | 0.152 (&lt;) | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A  | N/A              | 0.095 (&gt;)     | **0.002 (&gt;)** | N/A          | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | N/A  | N/A              | 0.075 (&lt;)     | **0.000 (&gt;)** | 0.133 (&lt;) | N/A                 | N/A        |
| Improvement / New Feature | r-Precision  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A  | **0.009 (&lt;)** | N/A              | N/A              | 0.177 (&lt;) | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A  | N/A              | N/A              | N/A              | 0.152 (&gt;) | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A  | N/A              | **0.004 (&lt;)** | **0.003 (&gt;)** | N/A          | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | N/A  | N/A              | **0.001 (&lt;)** | **0.000 (&gt;)** | 0.133 (&lt;) | N/A                 | N/A        |
| Improvement / Task        | r-Precision  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A  | **0.040 (&lt;)** | N/A              | N/A              | 0.106 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A  | N/A              | N/A              | N/A              | 0.152 (&lt;) | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A  | N/A              | 0.095 (&lt;)     | **0.002 (&lt;)** | N/A          | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | N/A  | N/A              | 0.075 (&lt;)     | **0.000 (&lt;)** | 0.133 (&lt;) | N/A                 | N/A        |
| Bug / New Feature         | r-Precision  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A  | **0.009 (&gt;)** | N/A              | N/A              | 0.177 (&lt;) | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A  | N/A              | N/A              | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A  | N/A              | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A          | N/A                 | N/A        |
| Bug / Task                | Recall@10    | N/A  | N/A              | 1.000 (&lt;)     | 1.000 (&lt;)     | 1.000 (&lt;) | N/A                 | N/A        |
| Bug / Task                | r-Precision  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A  | 1.000 (&gt;)     | N/A              | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A  | N/A              | N/A              | N/A              | 1.000 (&gt;) | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A  | N/A              | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A          | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | N/A  | N/A              | 1.000 (&lt;)     | 1.000 (&lt;)     | 1.000 (&gt;) | N/A                 | N/A        |
| New Feature / Task        | r-Precision  | N/A  | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A  | 1.000 (&gt;)     | N/A              | N/A              | 1.000 (&gt;) | N/A                 | N/A        |



# tfidf

### Specific

| Metric                    | Combination  | Avro         | Maven            | Tika             | Thrift           | Tomee        | Spring Data Mongodb | Spring Roo       |
|---------------------------|--------------|--------------|------------------|------------------|------------------|--------------|---------------------|------------------|
| Bug / Improvement         | Precision@1  | N/A          | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Bug / Improvement         | Precision@5  | N/A          | **0.042 (&lt;)** | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Bug / Improvement         | Precision@10 | N/A          | **0.005 (&lt;)** | 0.053 (&lt;)     | N/A              | N/A          | N/A                 | N/A              |
| Bug / Improvement         | hit@5        | N/A          | 0.304 (&lt;)     | N/A              | 0.072 (&gt;)     | N/A          | N/A                 | N/A              |
| Bug / Improvement         | hit@10       | 0.190 (&gt;) | 0.159 (&lt;)     | N/A              | 0.111 (&gt;)     | N/A          | N/A                 | N/A              |
| Bug / Improvement         | Recall@1     | 0.356 (&lt;) | N/A              | N/A              | 0.175 (&gt;)     | 0.355 (&gt;) | N/A                 | N/A              |
| Bug / Improvement         | Recall@5     | 0.183 (&gt;) | N/A              | **0.002 (&gt;)** | **0.000 (&gt;)** | N/A          | N/A                 | N/A              |
| Bug / Improvement         | Recall@10    | 0.102 (&gt;) | N/A              | **0.001 (&gt;)** | **0.000 (&gt;)** | N/A          | N/A                 | 0.212 (&gt;)     |
| Bug / Improvement         | r-Precision  | N/A          | **0.012 (&lt;)** | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Bug / Improvement         | MRR          | 0.115 (&lt;) | **0.005 (&lt;)** | N/A              | 0.074 (&gt;)     | N/A          | N/A                 | N/A              |
| Improvement / New Feature | Precision@1  | N/A          | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Improvement / New Feature | Precision@5  | N/A          | **0.040 (&gt;)** | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Improvement / New Feature | Precision@10 | N/A          | **0.003 (&gt;)** | **0.032 (&lt;)** | N/A              | N/A          | N/A                 | N/A              |
| Improvement / New Feature | hit@5        | N/A          | 0.053 (&lt;)     | N/A              | 0.192 (&gt;)     | N/A          | N/A                 | N/A              |
| Improvement / New Feature | hit@10       | 0.532 (&gt;) | **0.006 (&gt;)** | N/A              | 0.150 (&gt;)     | N/A          | N/A                 | N/A              |
| Improvement / New Feature | Recall@1     | 0.819 (&gt;) | N/A              | N/A              | 0.102 (&gt;)     | 0.390 (&gt;) | N/A                 | N/A              |
| Improvement / New Feature | Recall@5     | 0.299 (&gt;) | N/A              | 0.081 (&lt;)     | **0.000 (&gt;)** | N/A          | N/A                 | N/A              |
| Improvement / New Feature | Recall@10    | 0.171 (&gt;) | N/A              | 0.193 (&gt;)     | **0.000 (&gt;)** | N/A          | N/A                 | **0.021 (&lt;)** |
| Improvement / New Feature | r-Precision  | N/A          | **0.043 (&gt;)** | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Improvement / New Feature | MRR          | 0.791 (&gt;) | **0.000 (&lt;)** | N/A              | 0.169 (&gt;)     | N/A          | N/A                 | N/A              |
| Improvement / Task        | Precision@1  | N/A          | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Improvement / Task        | Precision@5  | N/A          | **0.042 (&lt;)** | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Improvement / Task        | Precision@10 | N/A          | **0.005 (&lt;)** | 0.053 (&gt;)     | N/A              | N/A          | N/A                 | N/A              |
| Improvement / Task        | hit@5        | N/A          | 0.304 (&gt;)     | N/A              | 0.072 (&gt;)     | N/A          | N/A                 | N/A              |
| Improvement / Task        | hit@10       | 0.190 (&gt;) | 0.159 (&gt;)     | N/A              | 0.111 (&gt;)     | N/A          | N/A                 | N/A              |
| Improvement / Task        | Recall@1     | 0.356 (&gt;) | N/A              | N/A              | 0.175 (&gt;)     | 0.355 (&gt;) | N/A                 | N/A              |
| Improvement / Task        | Recall@5     | 0.183 (&gt;) | N/A              | **0.002 (&gt;)** | **0.000 (&gt;)** | N/A          | N/A                 | N/A              |
| Improvement / Task        | Recall@10    | 0.102 (&gt;) | N/A              | **0.001 (&gt;)** | **0.000 (&gt;)** | N/A          | N/A                 | 0.212 (&lt;)     |
| Improvement / Task        | r-Precision  | N/A          | **0.012 (&lt;)** | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Improvement / Task        | MRR          | 0.115 (&gt;) | **0.005 (&gt;)** | N/A              | 0.074 (&gt;)     | N/A          | N/A                 | N/A              |
| Bug / New Feature         | Precision@1  | N/A          | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Bug / New Feature         | Precision@5  | N/A          | **0.040 (&lt;)** | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Bug / New Feature         | Precision@10 | N/A          | **0.003 (&lt;)** | **0.032 (&lt;)** | N/A              | N/A          | N/A                 | N/A              |
| Bug / New Feature         | hit@5        | N/A          | 0.053 (&lt;)     | N/A              | 0.192 (&gt;)     | N/A          | N/A                 | N/A              |
| Bug / New Feature         | hit@10       | 0.532 (&gt;) | **0.006 (&lt;)** | N/A              | 0.150 (&gt;)     | N/A          | N/A                 | N/A              |
| Bug / New Feature         | Recall@1     | 0.819 (&gt;) | N/A              | N/A              | 0.102 (&gt;)     | 0.390 (&gt;) | N/A                 | N/A              |
| Bug / New Feature         | Recall@5     | 0.299 (&gt;) | N/A              | 0.081 (&gt;)     | **0.000 (&gt;)** | N/A          | N/A                 | N/A              |
| Bug / New Feature         | Recall@10    | 0.171 (&gt;) | N/A              | 0.193 (&gt;)     | **0.000 (&gt;)** | N/A          | N/A                 | **0.021 (&gt;)** |
| Bug / New Feature         | r-Precision  | N/A          | **0.043 (&lt;)** | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Bug / New Feature         | MRR          | 0.791 (&gt;) | **0.000 (&lt;)** | N/A              | 0.169 (&gt;)     | N/A          | N/A                 | N/A              |
| Bug / Task                | Precision@1  | N/A          | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Bug / Task                | Precision@5  | N/A          | 1.000 (&lt;)     | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Bug / Task                | Precision@10 | N/A          | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A          | N/A                 | N/A              |
| Bug / Task                | hit@5        | N/A          | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | N/A          | N/A                 | N/A              |
| Bug / Task                | hit@10       | 1.000 (&gt;) | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | N/A          | N/A                 | N/A              |
| Bug / Task                | Recall@1     | 1.000 (&gt;) | N/A              | N/A              | 1.000 (&gt;)     | 1.000 (&gt;) | N/A                 | N/A              |
| Bug / Task                | Recall@5     | 1.000 (&gt;) | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A          | N/A                 | N/A              |
| Bug / Task                | Recall@10    | 1.000 (&gt;) | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A          | N/A                 | 1.000 (&gt;)     |
| Bug / Task                | r-Precision  | N/A          | 1.000 (&lt;)     | N/A              | N/A              | N/A          | N/A                 | N/A              |
| Bug / Task                | MRR          | 1.000 (&gt;) | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | N/A          | N/A                 | N/A              |
| New Feature / Task        | Precision@1  | N/A          | N/A              | N/A              | N/A              | N/A          | N/A                 | N/A              |
| New Feature / Task        | Precision@5  | N/A          | 1.000 (&lt;)     | N/A              | N/A              | N/A          | N/A                 | N/A              |
| New Feature / Task        | Precision@10 | N/A          | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A              | N/A          | N/A                 | N/A              |
| New Feature / Task        | hit@5        | N/A          | 1.000 (&gt;)     | N/A              | 1.000 (&gt;)     | N/A          | N/A                 | N/A              |
| New Feature / Task        | hit@10       | 1.000 (&lt;) | 1.000 (&gt;)     | N/A              | 1.000 (&gt;)     | N/A          | N/A                 | N/A              |
| New Feature / Task        | Recall@1     | 1.000 (&lt;) | N/A              | N/A              | 1.000 (&lt;)     | 1.000 (&lt;) | N/A                 | N/A              |
| New Feature / Task        | Recall@5     | 1.000 (&lt;) | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A          | N/A                 | N/A              |
| New Feature / Task        | Recall@10    | 1.000 (&lt;) | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A          | N/A                 | 1.000 (&gt;)     |
| New Feature / Task        | r-Precision  | N/A          | 1.000 (&lt;)     | N/A              | N/A              | N/A          | N/A                 | N/A              |
| New Feature / Task        | MRR          | 1.000 (&lt;) | 1.000 (&gt;)     | N/A              | 1.000 (&lt;)     | N/A          | N/A                 | N/A              |


### Holdout

| Metric                    | Combination  | Avro | Maven            | Tika | Thrift           | Tomee | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------|------------------|------|------------------|-------|---------------------|------------|
| Bug / Improvement         | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A  | **0.021 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A  | N/A              | N/A  | **0.001 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | N/A  | N/A              | N/A  | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A  | **0.012 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A  | **0.021 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A  | N/A              | N/A  | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | N/A  | N/A              | N/A  | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A  | **0.003 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A  | **0.021 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A  | N/A              | N/A  | **0.001 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | N/A  | N/A              | N/A  | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A  | **0.012 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A  | **0.021 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A  | N/A              | N/A  | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | N/A  | N/A              | N/A  | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A  | **0.003 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@10    | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A  | 1.000 (&lt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |



