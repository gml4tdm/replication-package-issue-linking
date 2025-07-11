# rvsm

### Specific

| Metric                    | Combination  | Avro         | Maven | Tika             | Thrift           | Tomee        | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|--------------|-------|------------------|------------------|--------------|---------------------|------------|
| New Feature / Task        | Precision@1  | N/A          | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A          | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | 1.000 (&lt;) | N/A   | 1.000 (&lt;)     | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | hit@5        | 1.000 (&lt;) | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| New Feature / Task        | hit@10       | 1.000 (&lt;) | N/A   | N/A              | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A          | N/A   | N/A              | 1.000 (&gt;)     | N/A          | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | 1.000 (&lt;) | N/A   | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | 1.000 (&lt;) | N/A   | 1.000 (&lt;)     | 1.000 (&gt;)     | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | r-Precision  | N/A          | N/A   | N/A              | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| New Feature / Task        | MRR          | 1.000 (&lt;) | N/A   | N/A              | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A          | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A          | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | 0.945 (&lt;) | N/A   | **0.023 (&gt;)** | N/A              | 0.151 (&lt;) | N/A                 | N/A        |
| Improvement / Task        | hit@5        | 0.773 (&gt;) | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / Task        | hit@10       | 0.297 (&gt;) | N/A   | N/A              | N/A              | 0.496 (&lt;) | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A          | N/A   | N/A              | 0.095 (&gt;)     | N/A          | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | 0.323 (&gt;) | N/A   | **0.000 (&gt;)** | **0.011 (&gt;)** | 0.889 (&gt;) | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | 0.114 (&gt;) | N/A   | **0.000 (&gt;)** | **0.007 (&gt;)** | 0.818 (&gt;) | N/A                 | N/A        |
| Improvement / Task        | r-Precision  | N/A          | N/A   | N/A              | N/A              | 0.510 (&lt;) | N/A                 | N/A        |
| Improvement / Task        | MRR          | 0.412 (&gt;) | N/A   | N/A              | N/A              | 0.838 (&lt;) | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A          | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A          | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Task                | Precision@10 | 1.000 (&lt;) | N/A   | 1.000 (&lt;)     | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| Bug / Task                | hit@5        | 1.000 (&gt;) | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Task                | hit@10       | 1.000 (&gt;) | N/A   | N/A              | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A          | N/A   | N/A              | 1.000 (&gt;)     | N/A          | N/A                 | N/A        |
| Bug / Task                | Recall@5     | 1.000 (&gt;) | N/A   | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;) | N/A                 | N/A        |
| Bug / Task                | Recall@10    | 1.000 (&gt;) | N/A   | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&lt;) | N/A                 | N/A        |
| Bug / Task                | r-Precision  | N/A          | N/A   | N/A              | N/A              | 1.000 (&gt;) | N/A                 | N/A        |
| Bug / Task                | MRR          | 1.000 (&gt;) | N/A   | N/A              | N/A              | 1.000 (&lt;) | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A          | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A          | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | 0.492 (&gt;) | N/A   | **0.003 (&gt;)** | N/A              | 0.792 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | 0.773 (&gt;) | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | 0.773 (&gt;) | N/A   | N/A              | N/A              | 0.935 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A          | N/A   | N/A              | 0.095 (&gt;)     | N/A          | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | 0.641 (&gt;) | N/A   | 0.090 (&gt;)     | **0.008 (&gt;)** | 0.827 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | 0.774 (&gt;) | N/A   | 0.338 (&gt;)     | **0.000 (&gt;)** | 0.818 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | r-Precision  | N/A          | N/A   | N/A              | N/A              | 0.669 (&gt;) | N/A                 | N/A        |
| Improvement / New Feature | MRR          | 0.822 (&gt;) | N/A   | N/A              | N/A              | 0.882 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A          | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A          | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | 0.492 (&gt;) | N/A   | **0.003 (&lt;)** | N/A              | 0.792 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | 0.773 (&gt;) | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | 0.773 (&gt;) | N/A   | N/A              | N/A              | 0.935 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A          | N/A   | N/A              | 0.095 (&gt;)     | N/A          | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | 0.641 (&gt;) | N/A   | 0.090 (&gt;)     | **0.008 (&gt;)** | 0.827 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | 0.774 (&gt;) | N/A   | 0.338 (&gt;)     | **0.000 (&gt;)** | 0.818 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | r-Precision  | N/A          | N/A   | N/A              | N/A              | 0.669 (&gt;) | N/A                 | N/A        |
| Bug / New Feature         | MRR          | 0.822 (&gt;) | N/A   | N/A              | N/A              | 0.882 (&gt;) | N/A                 | N/A        |
| Bug / Improvement         | Precision@1  | N/A          | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A          | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | 0.945 (&lt;) | N/A   | **0.023 (&lt;)** | N/A              | 0.151 (&gt;) | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | 0.773 (&gt;) | N/A   | N/A              | N/A              | N/A          | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | 0.297 (&lt;) | N/A   | N/A              | N/A              | 0.496 (&lt;) | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A          | N/A   | N/A              | 0.095 (&gt;)     | N/A          | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | 0.323 (&gt;) | N/A   | **0.000 (&gt;)** | **0.011 (&gt;)** | 0.889 (&gt;) | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | 0.114 (&gt;) | N/A   | **0.000 (&gt;)** | **0.007 (&gt;)** | 0.818 (&lt;) | N/A                 | N/A        |
| Bug / Improvement         | r-Precision  | N/A          | N/A   | N/A              | N/A              | 0.510 (&gt;) | N/A                 | N/A        |
| Bug / Improvement         | MRR          | 0.412 (&lt;) | N/A   | N/A              | N/A              | 0.838 (&gt;) | N/A                 | N/A        |


### Holdout

| Metric                    | Combination  | Avro | Maven | Tika             | Thrift           | Tomee | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------|-------|------------------|------------------|-------|---------------------|------------|
| New Feature / Task        | Precision@1  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A  | N/A   | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | N/A  | N/A   | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | r-Precision  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A  | N/A   | **0.019 (&lt;)** | **0.013 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | N/A  | N/A   | **0.014 (&lt;)** | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | r-Precision  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A  | N/A   | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@10    | N/A  | N/A   | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | r-Precision  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A  | N/A   | 0.175 (&gt;)     | **0.007 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | N/A  | N/A   | 0.322 (&lt;)     | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | r-Precision  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A  | N/A   | 0.175 (&lt;)     | **0.007 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | N/A  | N/A   | 0.322 (&lt;)     | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | r-Precision  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@1  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A  | N/A   | **0.019 (&lt;)** | **0.013 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | N/A  | N/A   | **0.014 (&lt;)** | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | r-Precision  | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A  | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |



# lsa-500

### Specific

| Metric                    | Combination  | Avro | Maven            | Tika             | Thrift           | Tomee | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------|------------------|------------------|------------------|-------|---------------------|------------|
| New Feature / Task        | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A  | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | N/A  | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | 1.000 (&lt;)        | N/A        |
| New Feature / Task        | r-Precision  | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A  | 1.000 (&gt;)     | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A  | **0.022 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A  | **0.002 (&lt;)** | **0.013 (&lt;)** | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A  | 0.195 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A  | **0.043 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A  | N/A              | N/A              | **0.031 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A  | N/A              | N/A              | **0.015 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | N/A  | 0.594 (&gt;)     | **0.007 (&gt;)** | **0.000 (&gt;)** | N/A   | 0.388 (&lt;)        | N/A        |
| Improvement / Task        | r-Precision  | N/A  | **0.023 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A  | **0.007 (&gt;)** | N/A              | 0.067 (&gt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A  | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A  | N/A              | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A  | N/A              | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@10    | N/A  | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | 1.000 (&lt;)        | N/A        |
| Bug / Task                | r-Precision  | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A  | 1.000 (&lt;)     | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A  | **0.016 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A  | **0.001 (&gt;)** | **0.032 (&lt;)** | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A  | **0.013 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A  | **0.001 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A  | N/A              | N/A              | **0.031 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A  | N/A              | N/A              | **0.007 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | N/A  | **0.021 (&gt;)** | 0.220 (&gt;)     | **0.000 (&lt;)** | N/A   | 0.160 (&gt;)        | N/A        |
| Improvement / New Feature | r-Precision  | N/A  | **0.023 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A  | **0.000 (&lt;)** | N/A              | 0.276 (&gt;)     | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A  | **0.016 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A  | **0.001 (&lt;)** | **0.032 (&lt;)** | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A  | **0.013 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A  | **0.001 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A  | N/A              | N/A              | **0.031 (&gt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A  | N/A              | N/A              | **0.007 (&gt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | N/A  | **0.021 (&gt;)** | 0.220 (&gt;)     | **0.000 (&gt;)** | N/A   | 0.160 (&gt;)        | N/A        |
| Bug / New Feature         | r-Precision  | N/A  | **0.023 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A  | **0.000 (&lt;)** | N/A              | 0.276 (&gt;)     | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A  | **0.022 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A  | **0.002 (&lt;)** | **0.013 (&lt;)** | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A  | 0.195 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A  | **0.043 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A  | N/A              | N/A              | **0.031 (&gt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A  | N/A              | N/A              | **0.015 (&gt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | N/A  | 0.594 (&lt;)     | **0.007 (&gt;)** | **0.000 (&gt;)** | N/A   | 0.388 (&lt;)        | N/A        |
| Bug / Improvement         | r-Precision  | N/A  | **0.023 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A  | **0.007 (&lt;)** | N/A              | 0.067 (&gt;)     | N/A   | N/A                 | N/A        |


### Holdout

| Metric                    | Combination  | Avro | Maven            | Tika | Thrift           | Tomee | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------|------------------|------|------------------|-------|---------------------|------------|
| New Feature / Task        | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A  | **0.010 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A  | 0.057 (&lt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A  | N/A              | N/A  | **0.013 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | N/A  | N/A              | N/A  | **0.002 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A  | **0.009 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@10    | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A  | **0.010 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A  | **0.016 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A  | N/A              | N/A  | **0.006 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | N/A  | N/A              | N/A  | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A  | **0.002 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A  | **0.010 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A  | **0.016 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A  | N/A              | N/A  | **0.006 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | N/A  | N/A              | N/A  | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A  | **0.002 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A  | **0.010 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A  | 0.057 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A  | N/A              | N/A  | **0.013 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | N/A  | N/A              | N/A  | **0.002 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A  | **0.009 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |



# lsa-1000

### Specific

| Metric                    | Combination  | Avro | Maven            | Tika             | Thrift           | Tomee | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------|------------------|------------------|------------------|-------|---------------------|------------|
| New Feature / Task        | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A  | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A  | N/A              | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | N/A  | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | 1.000 (&lt;)        | N/A        |
| New Feature / Task        | r-Precision  | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A  | 0.091 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A  | **0.001 (&lt;)** | **0.023 (&lt;)** | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A  | 0.367 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A  | **0.016 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A  | N/A              | N/A              | 0.189 (&gt;)     | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A  | N/A              | N/A              | **0.004 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | N/A  | 0.552 (&gt;)     | **0.005 (&gt;)** | **0.001 (&gt;)** | N/A   | 0.381 (&lt;)        | N/A        |
| Improvement / Task        | r-Precision  | N/A  | **0.027 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A  | **0.006 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A  | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A  | N/A              | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A  | N/A              | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@10    | N/A  | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | 1.000 (&lt;)        | N/A        |
| Bug / Task                | r-Precision  | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A  | **0.025 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A  | **0.000 (&gt;)** | 0.098 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A  | **0.017 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A  | **0.000 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A  | N/A              | N/A              | **0.023 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A  | N/A              | N/A              | **0.002 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | N/A  | **0.018 (&gt;)** | 0.078 (&gt;)     | **0.001 (&lt;)** | N/A   | 0.153 (&gt;)        | N/A        |
| Improvement / New Feature | r-Precision  | N/A  | **0.027 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A  | **0.000 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A  | **0.025 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A  | **0.000 (&lt;)** | 0.098 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A  | **0.017 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A  | **0.000 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A  | N/A              | N/A              | **0.023 (&gt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A  | N/A              | N/A              | **0.002 (&gt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | N/A  | **0.018 (&gt;)** | 0.078 (&gt;)     | **0.001 (&gt;)** | N/A   | 0.153 (&gt;)        | N/A        |
| Bug / New Feature         | r-Precision  | N/A  | **0.027 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A  | **0.000 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A  | 0.091 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A  | **0.001 (&lt;)** | **0.023 (&lt;)** | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A  | 0.367 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A  | **0.016 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A  | N/A              | N/A              | 0.189 (&gt;)     | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A  | N/A              | N/A              | **0.004 (&gt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | N/A  | 0.552 (&lt;)     | **0.005 (&gt;)** | **0.001 (&gt;)** | N/A   | 0.381 (&lt;)        | N/A        |
| Bug / Improvement         | r-Precision  | N/A  | **0.027 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A  | **0.006 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |


### Holdout

| Metric                    | Combination  | Avro | Maven            | Tika | Thrift           | Tomee | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------|------------------|------|------------------|-------|---------------------|------------|
| New Feature / Task        | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A  | **0.008 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A  | **0.029 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A  | N/A              | N/A  | 0.064 (&gt;)     | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A  | N/A              | N/A  | **0.008 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | N/A  | N/A              | N/A  | **0.003 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A  | **0.010 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@10    | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A  | **0.008 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A  | **0.009 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A  | N/A              | N/A  | **0.030 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A  | N/A              | N/A  | **0.002 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | N/A  | N/A              | N/A  | **0.001 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A  | **0.002 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A  | **0.008 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A  | **0.009 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A  | N/A              | N/A  | **0.030 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A  | N/A              | N/A  | **0.002 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | N/A  | N/A              | N/A  | **0.001 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A  | **0.002 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A  | **0.008 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A  | **0.029 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A  | N/A              | N/A  | 0.064 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A  | N/A              | N/A  | **0.008 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | N/A  | N/A              | N/A  | **0.003 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A  | **0.010 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |



# tfidf

### Specific

| Metric                    | Combination  | Avro | Maven            | Tika             | Thrift           | Tomee | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------|------------------|------------------|------------------|-------|---------------------|------------|
| New Feature / Task        | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A  | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A  | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A  | N/A              | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A  | N/A              | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | N/A  | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | 1.000 (&lt;)        | N/A        |
| New Feature / Task        | r-Precision  | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A  | 1.000 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A  | 0.059 (&lt;)     | 0.074 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A  | **0.002 (&lt;)** | **0.034 (&lt;)** | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A  | 0.308 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A  | 0.060 (&gt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A  | N/A              | N/A              | 0.223 (&gt;)     | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A  | N/A              | N/A              | **0.004 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | N/A  | N/A              | **0.002 (&gt;)** | **0.000 (&gt;)** | N/A   | 0.172 (&lt;)        | N/A        |
| Improvement / Task        | r-Precision  | N/A  | **0.035 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A  | **0.021 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A  | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A  | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A  | N/A              | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A  | N/A              | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@10    | N/A  | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A   | 1.000 (&lt;)        | N/A        |
| Bug / Task                | r-Precision  | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A  | 1.000 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A  | **0.015 (&gt;)** | 0.074 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A  | **0.001 (&gt;)** | 0.060 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A  | **0.011 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A  | **0.002 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A  | N/A              | N/A              | **0.045 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A  | N/A              | N/A              | **0.001 (&lt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | N/A  | N/A              | 0.095 (&gt;)     | **0.000 (&lt;)** | N/A   | 0.143 (&gt;)        | N/A        |
| Improvement / New Feature | r-Precision  | N/A  | **0.040 (&gt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A  | **0.000 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A  | **0.015 (&lt;)** | 0.074 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A  | **0.001 (&lt;)** | 0.060 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A  | **0.011 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A  | **0.002 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A  | N/A              | N/A              | **0.045 (&gt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A  | N/A              | N/A              | **0.001 (&gt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | N/A  | N/A              | 0.095 (&gt;)     | **0.000 (&gt;)** | N/A   | 0.143 (&gt;)        | N/A        |
| Bug / New Feature         | r-Precision  | N/A  | **0.040 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A  | **0.000 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@1  | N/A  | N/A              | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A  | 0.059 (&lt;)     | 0.074 (&lt;)     | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A  | **0.002 (&lt;)** | **0.034 (&lt;)** | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A  | 0.308 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A  | 0.060 (&lt;)     | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A  | N/A              | N/A              | 0.223 (&gt;)     | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A  | N/A              | N/A              | **0.004 (&gt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | N/A  | N/A              | **0.002 (&gt;)** | **0.000 (&gt;)** | N/A   | 0.172 (&lt;)        | N/A        |
| Bug / Improvement         | r-Precision  | N/A  | **0.035 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A  | **0.021 (&lt;)** | N/A              | N/A              | N/A   | N/A                 | N/A        |


### Holdout

| Metric                    | Combination  | Avro | Maven            | Tika | Thrift           | Tomee | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|------|------------------|------|------------------|-------|---------------------|------------|
| New Feature / Task        | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A  | **0.012 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A  | 0.069 (&lt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A  | N/A              | N/A  | **0.006 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | N/A  | N/A              | N/A  | **0.003 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A  | **0.018 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@10    | N/A  | N/A              | N/A  | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A  | 1.000 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A  | **0.012 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A  | **0.029 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A  | N/A              | N/A  | **0.001 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | N/A  | N/A              | N/A  | **0.001 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A  | **0.003 (&lt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A  | **0.012 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A  | **0.029 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A  | N/A              | N/A  | **0.001 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | N/A  | N/A              | N/A  | **0.001 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A  | **0.003 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@1  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A  | **0.012 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A  | 0.069 (&gt;)     | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A  | N/A              | N/A  | **0.006 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | N/A  | N/A              | N/A  | **0.003 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | r-Precision  | N/A  | N/A              | N/A  | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A  | **0.018 (&gt;)** | N/A  | N/A              | N/A   | N/A                 | N/A        |



# bm25

### Specific

| Metric                    | Combination  | Avro             | Maven            | Tika             | Thrift           | Tomee            | Spring Data Mongodb | Spring Roo   |
|---------------------------|--------------|------------------|------------------|------------------|------------------|------------------|---------------------|--------------|
| New Feature / Task        | Precision@1  | N/A              | N/A              | 1.000 (&lt;)     | N/A              | N/A              | N/A                 | N/A          |
| New Feature / Task        | Precision@5  | 1.000 (&lt;)     | N/A              | N/A              | 1.000 (&lt;)     | N/A              | N/A                 | N/A          |
| New Feature / Task        | Precision@10 | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A              | N/A              | N/A                 | N/A          |
| New Feature / Task        | hit@5        | 1.000 (&lt;)     | N/A              | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | 1.000 (&gt;) |
| New Feature / Task        | hit@10       | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A              | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| New Feature / Task        | Recall@1     | N/A              | N/A              | 1.000 (&gt;)     | 1.000 (&lt;)     | N/A              | N/A                 | N/A          |
| New Feature / Task        | Recall@5     | 1.000 (&lt;)     | N/A              | 1.000 (&lt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| New Feature / Task        | Recall@10    | 1.000 (&lt;)     | 1.000 (&gt;)     | 1.000 (&lt;)     | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| New Feature / Task        | r-Precision  | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A              | N/A              | N/A              | N/A                 | N/A          |
| New Feature / Task        | MRR          | 1.000 (&lt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| Improvement / Task        | Precision@1  | N/A              | N/A              | **0.026 (&gt;)** | N/A              | N/A              | N/A                 | N/A          |
| Improvement / Task        | Precision@5  | 0.823 (&lt;)     | N/A              | N/A              | 0.104 (&gt;)     | N/A              | N/A                 | N/A          |
| Improvement / Task        | Precision@10 | 0.467 (&lt;)     | 0.613 (&lt;)     | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Improvement / Task        | hit@5        | 0.430 (&gt;)     | N/A              | N/A              | **0.022 (&gt;)** | **0.030 (&gt;)** | N/A                 | 0.085 (&gt;) |
| Improvement / Task        | hit@10       | 0.859 (&lt;)     | 0.836 (&gt;)     | N/A              | 0.162 (&lt;)     | **0.010 (&gt;)** | N/A                 | N/A          |
| Improvement / Task        | Recall@1     | N/A              | N/A              | **0.000 (&gt;)** | 0.338 (&lt;)     | N/A              | N/A                 | N/A          |
| Improvement / Task        | Recall@5     | 0.124 (&gt;)     | N/A              | **0.000 (&gt;)** | **0.000 (&gt;)** | **0.005 (&gt;)** | N/A                 | N/A          |
| Improvement / Task        | Recall@10    | 0.236 (&lt;)     | 0.126 (&gt;)     | **0.000 (&gt;)** | **0.003 (&lt;)** | **0.002 (&gt;)** | N/A                 | N/A          |
| Improvement / Task        | r-Precision  | 0.841 (&lt;)     | 0.168 (&gt;)     | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Improvement / Task        | MRR          | 0.721 (&lt;)     | 0.985 (&gt;)     | **0.023 (&gt;)** | 0.249 (&gt;)     | **0.008 (&gt;)** | N/A                 | N/A          |
| Bug / Task                | Precision@1  | N/A              | N/A              | 1.000 (&gt;)     | N/A              | N/A              | N/A                 | N/A          |
| Bug / Task                | Precision@5  | 1.000 (&lt;)     | N/A              | N/A              | 1.000 (&gt;)     | N/A              | N/A                 | N/A          |
| Bug / Task                | Precision@10 | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Bug / Task                | hit@5        | 1.000 (&gt;)     | N/A              | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | 1.000 (&gt;) |
| Bug / Task                | hit@10       | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| Bug / Task                | Recall@1     | N/A              | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A              | N/A                 | N/A          |
| Bug / Task                | Recall@5     | 1.000 (&gt;)     | N/A              | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| Bug / Task                | Recall@10    | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| Bug / Task                | r-Precision  | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Bug / Task                | MRR          | 1.000 (&gt;)     | 1.000 (&lt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | 1.000 (&gt;)     | N/A                 | N/A          |
| Improvement / New Feature | Precision@1  | N/A              | N/A              | 0.355 (&gt;)     | N/A              | N/A              | N/A                 | N/A          |
| Improvement / New Feature | Precision@5  | 0.464 (&gt;)     | N/A              | N/A              | **0.017 (&gt;)** | N/A              | N/A                 | N/A          |
| Improvement / New Feature | Precision@10 | 0.126 (&gt;)     | **0.039 (&lt;)** | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Improvement / New Feature | hit@5        | 0.203 (&gt;)     | N/A              | N/A              | **0.000 (&gt;)** | 0.710 (&gt;)     | N/A                 | 0.418 (&gt;) |
| Improvement / New Feature | hit@10       | 0.055 (&gt;)     | **0.043 (&gt;)** | N/A              | **0.000 (&gt;)** | 0.359 (&gt;)     | N/A                 | N/A          |
| Improvement / New Feature | Recall@1     | N/A              | N/A              | **0.027 (&gt;)** | **0.021 (&gt;)** | N/A              | N/A                 | N/A          |
| Improvement / New Feature | Recall@5     | **0.036 (&gt;)** | N/A              | **0.018 (&gt;)** | **0.000 (&gt;)** | 0.787 (&gt;)     | N/A                 | N/A          |
| Improvement / New Feature | Recall@10    | **0.003 (&gt;)** | 0.318 (&gt;)     | **0.006 (&gt;)** | **0.000 (&lt;)** | 0.268 (&gt;)     | N/A                 | N/A          |
| Improvement / New Feature | r-Precision  | 0.841 (&gt;)     | **0.013 (&gt;)** | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Improvement / New Feature | MRR          | 0.279 (&gt;)     | **0.028 (&gt;)** | 0.598 (&gt;)     | **0.004 (&gt;)** | 0.320 (&gt;)     | N/A                 | N/A          |
| Bug / New Feature         | Precision@1  | N/A              | N/A              | 0.355 (&gt;)     | N/A              | N/A              | N/A                 | N/A          |
| Bug / New Feature         | Precision@5  | 0.464 (&gt;)     | N/A              | N/A              | **0.017 (&gt;)** | N/A              | N/A                 | N/A          |
| Bug / New Feature         | Precision@10 | 0.126 (&gt;)     | **0.039 (&lt;)** | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Bug / New Feature         | hit@5        | 0.203 (&gt;)     | N/A              | N/A              | **0.000 (&gt;)** | 0.710 (&gt;)     | N/A                 | 0.418 (&gt;) |
| Bug / New Feature         | hit@10       | 0.055 (&gt;)     | **0.043 (&lt;)** | N/A              | **0.000 (&gt;)** | 0.359 (&gt;)     | N/A                 | N/A          |
| Bug / New Feature         | Recall@1     | N/A              | N/A              | **0.027 (&gt;)** | **0.021 (&gt;)** | N/A              | N/A                 | N/A          |
| Bug / New Feature         | Recall@5     | **0.036 (&gt;)** | N/A              | **0.018 (&gt;)** | **0.000 (&gt;)** | 0.787 (&gt;)     | N/A                 | N/A          |
| Bug / New Feature         | Recall@10    | **0.003 (&gt;)** | 0.318 (&gt;)     | **0.006 (&gt;)** | **0.000 (&gt;)** | 0.268 (&gt;)     | N/A                 | N/A          |
| Bug / New Feature         | r-Precision  | 0.841 (&gt;)     | **0.013 (&lt;)** | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Bug / New Feature         | MRR          | 0.279 (&gt;)     | **0.028 (&lt;)** | 0.598 (&gt;)     | **0.004 (&gt;)** | 0.320 (&gt;)     | N/A                 | N/A          |
| Bug / Improvement         | Precision@1  | N/A              | N/A              | **0.026 (&gt;)** | N/A              | N/A              | N/A                 | N/A          |
| Bug / Improvement         | Precision@5  | 0.823 (&gt;)     | N/A              | N/A              | 0.104 (&gt;)     | N/A              | N/A                 | N/A          |
| Bug / Improvement         | Precision@10 | 0.467 (&lt;)     | 0.613 (&lt;)     | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Bug / Improvement         | hit@5        | 0.430 (&gt;)     | N/A              | N/A              | **0.022 (&gt;)** | **0.030 (&lt;)** | N/A                 | 0.085 (&lt;) |
| Bug / Improvement         | hit@10       | 0.859 (&gt;)     | 0.836 (&lt;)     | N/A              | 0.162 (&gt;)     | **0.010 (&lt;)** | N/A                 | N/A          |
| Bug / Improvement         | Recall@1     | N/A              | N/A              | **0.000 (&gt;)** | 0.338 (&gt;)     | N/A              | N/A                 | N/A          |
| Bug / Improvement         | Recall@5     | 0.124 (&gt;)     | N/A              | **0.000 (&gt;)** | **0.000 (&gt;)** | **0.005 (&lt;)** | N/A                 | N/A          |
| Bug / Improvement         | Recall@10    | 0.236 (&gt;)     | 0.126 (&lt;)     | **0.000 (&gt;)** | **0.003 (&gt;)** | **0.002 (&lt;)** | N/A                 | N/A          |
| Bug / Improvement         | r-Precision  | 0.841 (&lt;)     | 0.168 (&lt;)     | N/A              | N/A              | N/A              | N/A                 | N/A          |
| Bug / Improvement         | MRR          | 0.721 (&gt;)     | 0.985 (&lt;)     | **0.023 (&gt;)** | 0.249 (&gt;)     | **0.008 (&lt;)** | N/A                 | N/A          |


### Holdout

| Metric                    | Combination  | Avro         | Maven | Tika             | Thrift           | Tomee | Spring Data Mongodb | Spring Roo |
|---------------------------|--------------|--------------|-------|------------------|------------------|-------|---------------------|------------|
| New Feature / Task        | Precision@1  | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@5  | N/A          | N/A   | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Precision@10 | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@5        | N/A          | N/A   | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | hit@10       | N/A          | N/A   | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@1     | N/A          | N/A   | 1.000 (&lt;)     | 1.000 (&gt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@5     | N/A          | N/A   | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | Recall@10    | 1.000 (&gt;) | N/A   | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| New Feature / Task        | r-Precision  | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| New Feature / Task        | MRR          | N/A          | N/A   | N/A              | 1.000 (&gt;)     | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@1  | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@5  | N/A          | N/A   | N/A              | **0.042 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Precision@10 | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@5        | N/A          | N/A   | N/A              | **0.004 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | hit@10       | N/A          | N/A   | N/A              | **0.004 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@1     | N/A          | N/A   | **0.008 (&lt;)** | 0.054 (&gt;)     | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@5     | N/A          | N/A   | **0.000 (&lt;)** | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | Recall@10    | 0.141 (&gt;) | N/A   | **0.001 (&lt;)** | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / Task        | r-Precision  | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / Task        | MRR          | N/A          | N/A   | N/A              | **0.022 (&gt;)** | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@1  | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@5  | N/A          | N/A   | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Precision@10 | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@5        | N/A          | N/A   | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | hit@10       | N/A          | N/A   | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@1     | N/A          | N/A   | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@5     | N/A          | N/A   | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | Recall@10    | 1.000 (&lt;) | N/A   | 1.000 (&lt;)     | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Task                | r-Precision  | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Task                | MRR          | N/A          | N/A   | N/A              | 1.000 (&lt;)     | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@1  | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@5  | N/A          | N/A   | N/A              | **0.021 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Precision@10 | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@5        | N/A          | N/A   | N/A              | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | hit@10       | N/A          | N/A   | N/A              | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@1     | N/A          | N/A   | 0.092 (&gt;)     | **0.026 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@5     | N/A          | N/A   | 0.066 (&lt;)     | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | Recall@10    | 0.060 (&gt;) | N/A   | **0.032 (&gt;)** | **0.000 (&gt;)** | N/A   | N/A                 | N/A        |
| Improvement / New Feature | r-Precision  | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Improvement / New Feature | MRR          | N/A          | N/A   | N/A              | **0.006 (&gt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@1  | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@5  | N/A          | N/A   | N/A              | **0.021 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Precision@10 | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@5        | N/A          | N/A   | N/A              | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | hit@10       | N/A          | N/A   | N/A              | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@1     | N/A          | N/A   | 0.092 (&lt;)     | **0.026 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@5     | N/A          | N/A   | 0.066 (&lt;)     | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | Recall@10    | 0.060 (&lt;) | N/A   | **0.032 (&lt;)** | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / New Feature         | r-Precision  | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / New Feature         | MRR          | N/A          | N/A   | N/A              | **0.006 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@1  | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@5  | N/A          | N/A   | N/A              | **0.042 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Precision@10 | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@5        | N/A          | N/A   | N/A              | **0.004 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | hit@10       | N/A          | N/A   | N/A              | **0.004 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@1     | N/A          | N/A   | **0.008 (&lt;)** | 0.054 (&lt;)     | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@5     | N/A          | N/A   | **0.000 (&lt;)** | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | Recall@10    | 0.141 (&lt;) | N/A   | **0.001 (&lt;)** | **0.000 (&lt;)** | N/A   | N/A                 | N/A        |
| Bug / Improvement         | r-Precision  | N/A          | N/A   | N/A              | N/A              | N/A   | N/A                 | N/A        |
| Bug / Improvement         | MRR          | N/A          | N/A   | N/A              | **0.022 (&lt;)** | N/A   | N/A                 | N/A        |



