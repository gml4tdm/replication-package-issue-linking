use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone)]
pub struct Query {
    words: HashSet<String>
}

impl Query {
    pub fn new(words: Vec<String>) -> Self {
        Self { 
            words: words.into_iter()
                .collect::<HashSet<_>>()
        }
    }
    
    fn unique_words(self) -> HashSet<String> {
        self.words
    }
}

#[derive(Debug, Clone)]
pub struct Document {
    fields: Vec<Vec<String>>
}

impl Document {
    pub fn new(fields: Vec<Vec<String>>) -> Self {
        Self { fields }
    }
    
    fn len(&self) -> usize {
        self.fields.iter().map(Vec::len).sum()
    }
    
    fn histograms(self) -> (HashMap<String, usize>, Vec<HashMap<String, usize>>) {
        let mut global_hist = HashMap::new();
        let mut field_hists = Vec::new();
        
        for field in self.fields.into_iter() {
            let mut hist = HashMap::new();
            for word in field {
                global_hist.entry(word.clone())
                    .and_modify(|x| *x += 1).or_insert(1);
                hist.entry(word)
                    .and_modify(|x| *x += 1).or_insert(1);
            }
            field_hists.push(hist);
        }
        
        (global_hist, field_hists)
    }
}


#[derive(Debug, Clone)]
pub struct BM25 {
    k1: f64,
    b: f64,
    delta: f64,
    component_weights: Option<Vec<f64>>
}

impl BM25 {
    pub fn new(k1: f64, b: f64, delta: f64, component_weights: Option<Vec<f64>>) -> Self {
        Self { k1, b, delta, component_weights }
    }
    
    pub fn rank(&self, query: Query, corpus: Vec<Document>) -> Vec<f64> {
        if corpus.is_empty() {
            return Vec::new();
        }
        
        // Determine vocabulary 
        let restrict_to = query.unique_words();
        let vocab = restrict_to.iter().cloned().collect::<Vec<_>>();
        
        // Calculate word frequencies 
        let lengths = corpus.iter()
            .map(Document::len).collect::<Vec<_>>();
        let histograms = corpus.into_iter()
            .map(Document::histograms).collect::<Vec<_>>();
        
        // Compute IDF
        let n = histograms.len() as f64;
        let idf = vocab.iter()
            .map(|word| {
                histograms.iter()
                    .map(|(h, _)| h.contains_key(word) as usize)
                    .sum::<usize>() 
            })
            .map(|f| {
                let m = f as f64;
                f64::ln(
                    (n - m + 0.5) / (m + 0.5) + 1.0
                )
            })
            .collect::<Vec<_>>();
        
        // Average length 
        let total_length = lengths.iter().sum::<usize>() as f64;
        let avg_length = total_length / (lengths.len() as f64);
        
        // Prepare weights 
        let weights = match &self.component_weights {
            None => {
                vec![1.0; histograms[0].0.len()]
            }
            Some(w) => w.clone()
        };
        
        // Rank
        let result = histograms.into_iter()
            .zip(lengths)
            .map(|((_, fields), length)| {
                let ell = (length as f64) / avg_length;
                let score = vocab.iter()
                    .zip(idf.iter().copied())
                    .map(|(term, c_idf)| {
                        let f_d = fields.iter()
                            .zip(weights.iter().copied())
                            .map(|(hist, w)| {
                                w * hist.get(term).copied().unwrap_or(0) as f64
                            })
                            .sum::<f64>();
                        let numerator = f_d * (self.k1 + 1.0);
                        let denominator = f_d + (self.k1 * (1.0 - self.b + self.b*ell));
                        let term_score = numerator/denominator + self.delta;
                        term_score * c_idf 
                    })
                    .sum::<f64>();
                score
            })
            .collect::<Vec<_>>();
        
        result
    }
}
