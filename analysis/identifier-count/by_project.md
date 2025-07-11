# Analysis of Identifier Count by Project

### Global

Kruskal: statistic = 115.00062236746295, p-value = 1.82534678546132e-22

### Pairwise Comparison (Conover's Post Hoc)

| Category 1          | Category 2          | Order | p          |
|---------------------|---------------------|-------|------------|
| Avro                | Maven               | &gt;  | 1.0000     |
| Avro                | Tika                | &gt;  | **0.0000** |
| Avro                | Thrift              | &gt;  | **0.0001** |
| Avro                | TomEE               | &lt;  | 0.4074     |
| Avro                | Spring Data MongoDB | &lt;  | **0.0000** |
| Avro                | Spring Roo          | &lt;  | **0.0039** |
| Maven               | Tika                | &lt;  | **0.0000** |
| Maven               | Thrift              | &lt;  | 1.0000     |
| Maven               | TomEE               | &lt;  | **0.0005** |
| Maven               | Spring Data MongoDB | &lt;  | **0.0000** |
| Maven               | Spring Roo          | &lt;  | **0.0330** |
| Tika                | Thrift              | &lt;  | **0.0001** |
| Tika                | TomEE               | &lt;  | **0.0005** |
| Tika                | Spring Data MongoDB | &lt;  | 1.0000     |
| Tika                | Spring Roo          | &lt;  | **0.0005** |
| Thrift              | TomEE               | &lt;  | 0.4074     |
| Thrift              | Spring Data MongoDB | &lt;  | **0.0000** |
| Thrift              | Spring Roo          | &lt;  | **0.0005** |
| TomEE               | Spring Data MongoDB | &lt;  | **0.0000** |
| TomEE               | Spring Roo          | &gt;  | **0.0330** |
| Spring Data MongoDB | Spring Roo          | &gt;  | **0.0039** |
