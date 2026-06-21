use project_ai_genesis_emitter::{GENESIS_HASH, GenesisInput, emit};
use std::env;
use std::io::{self, Read};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let previous_hash = env::args()
        .nth(1)
        .unwrap_or_else(|| GENESIS_HASH.to_owned());
    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;
    let event: GenesisInput = serde_json::from_str(&input)?;
    let record = emit(event, &previous_hash).map_err(io::Error::other)?;
    println!("{}", serde_json::to_string(&record)?);
    Ok(())
}
