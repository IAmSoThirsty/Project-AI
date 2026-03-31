#[derive(Debug, Clone)]
pub struct TARL {
    pub version: &'static str,
    pub intent: String,
    pub scope: String,
    pub authority: String,
    pub constraints: Vec<String>,
}

impl TARL {
    pub fn new(intent: &str, scope: &str, authority: &str, constraints: Vec<String>) -> TARL {
        TARL {
            version: "2.0",
            intent: intent.to_string(),
            scope: scope.to_string(),
            authority: authority.to_string(),
            constraints,
        }
    }
}
