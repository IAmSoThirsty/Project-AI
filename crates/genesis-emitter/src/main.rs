use project_ai_genesis_emitter::{GENESIS_HASH, GenesisInput, HEALTH_JSON, emit, serve_health};
use std::env;
use std::io::{self, Read};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut arguments = env::args().skip(1);
    let command = arguments.next();
    if command.as_deref() == Some("health") {
        println!("{HEALTH_JSON}");
        return Ok(());
    }
    if command.as_deref() == Some("serve") {
        let bind = arguments
            .next()
            .unwrap_or_else(|| "127.0.0.1:8080".to_owned());
        return serve_health(&bind).map_err(Into::into);
    }
    let previous_hash = command.unwrap_or_else(|| GENESIS_HASH.to_owned());
    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;
    let event: GenesisInput = serde_json::from_str(&input)?;
    let record = emit(event, &previous_hash).map_err(io::Error::other)?;
    println!("{}", serde_json::to_string(&record)?);
    Ok(())
}
