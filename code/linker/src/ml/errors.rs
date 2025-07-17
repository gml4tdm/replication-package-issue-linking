use std::sync::PoisonError;

error_set::error_set!{
    IndexLoadingError = IndexDecodingError || ResolverError || SampleGenerationError;
    
    IndexDecodingError = {
        #[display("IO Error: {0}")]
        IOError(std::io::Error),
        
        #[display("Error in library: {0}")]
        InternalLibraryError(Box<dyn std::error::Error>),
        
        #[display("Missing sequence number for field {field}: {index}")]
        MissingSequenceNumber{field: String, index: usize},
        
        #[display("Invalid integer value for field {field}: {value} ({error})")]
        InvalidInteger{field: String, value: String, error: String},
        
        #[display("Invalid action in delta: {action}")]
        InvalidDeltaAction{action: String},
        
        #[display("'Add' delta without file index")]
        AddDeltaWithoutFileIndex,
        
        #[display("'Rem' delta with file index")]
        RemDeltaWithFileIndex,
        
        #[display("Non-consecutive indices for field: {field}")]
        NonConsecutiveIndices{field: String}
    };
    
    ResolverError = {
        #[display("Index {index} is out of bounds for {field}")]
        IndexOutOfBounds{field: String, index: usize},
        
        #[display("Poisoned Lock")]
        ConcurrencyError
    };
    
    SampleGenerationError = LightweightSampleGenerationError;
    
    LightweightSampleGenerationError = {
        #[display("ID too large: {index}")]
        IdTooLarge{index: usize}
    };
}

impl<T> From<PoisonError<T>> for IndexLoadingError {
    fn from(_value: PoisonError<T>) -> Self {
        Self::ConcurrencyError
    }
}