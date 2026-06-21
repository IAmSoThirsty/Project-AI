//! Canonical, hash-bound Genesis evidence emission without execution authority.

use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::fmt::Write;

pub const GENESIS_HASH: &str = "0000000000000000000000000000000000000000000000000000000000000000";

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct GenesisInput {
    pub sequence: u64,
    pub event_type: String,
    pub payload: BTreeMap<String, Value>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct GenesisRecord {
    pub sequence: u64,
    pub event_type: String,
    pub payload: BTreeMap<String, Value>,
    pub previous_hash: String,
    pub record_hash: String,
}

#[derive(Debug, Serialize)]
struct RecordBody<'a> {
    sequence: u64,
    event_type: &'a str,
    payload: &'a BTreeMap<String, Value>,
    previous_hash: &'a str,
}

pub fn emit(input: GenesisInput, previous_hash: &str) -> Result<GenesisRecord, String> {
    if input.sequence == 0 {
        return Err("sequence must be positive".to_owned());
    }
    if input.event_type.trim().is_empty() {
        return Err("event_type must not be empty".to_owned());
    }
    if !is_sha256(previous_hash) {
        return Err("previous_hash must be a lowercase SHA-256 value".to_owned());
    }
    let body = RecordBody {
        sequence: input.sequence,
        event_type: &input.event_type,
        payload: &input.payload,
        previous_hash,
    };
    let canonical = serde_json::to_vec(&body).map_err(|error| error.to_string())?;
    let record_hash = sha256_hex(&canonical);
    Ok(GenesisRecord {
        sequence: input.sequence,
        event_type: input.event_type,
        payload: input.payload,
        previous_hash: previous_hash.to_owned(),
        record_hash,
    })
}

pub fn verify(record: &GenesisRecord) -> bool {
    if record.sequence == 0
        || record.event_type.trim().is_empty()
        || !is_sha256(&record.previous_hash)
        || !is_sha256(&record.record_hash)
    {
        return false;
    }
    let body = RecordBody {
        sequence: record.sequence,
        event_type: &record.event_type,
        payload: &record.payload,
        previous_hash: &record.previous_hash,
    };
    serde_json::to_vec(&body)
        .map(|canonical| sha256_hex(&canonical) == record.record_hash)
        .unwrap_or(false)
}

fn is_sha256(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
}

fn sha256_hex(content: &[u8]) -> String {
    let digest = Sha256::digest(content);
    let mut output = String::with_capacity(64);
    for byte in digest {
        write!(&mut output, "{byte:02x}").expect("writing to String cannot fail");
    }
    output
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn input() -> GenesisInput {
        GenesisInput {
            sequence: 1,
            event_type: "execution.completed".to_owned(),
            payload: BTreeMap::from([
                ("action_id".to_owned(), json!("a-1")),
                ("outcome".to_owned(), json!("ALLOW")),
            ]),
        }
    }

    #[test]
    fn emission_is_deterministic_and_verifiable() {
        let first = emit(input(), GENESIS_HASH).expect("valid record");
        let second = emit(input(), GENESIS_HASH).expect("valid record");
        assert_eq!(first, second);
        assert!(verify(&first));
    }

    #[test]
    fn tamper_and_invalid_inputs_fail_closed() {
        let mut record = emit(input(), GENESIS_HASH).expect("valid record");
        record.payload.insert("outcome".to_owned(), json!("DENY"));
        assert!(!verify(&record));
        assert!(emit(input(), "invalid").is_err());
        let mut empty = input();
        empty.event_type.clear();
        assert!(emit(empty, GENESIS_HASH).is_err());
        let mut zero = input();
        zero.sequence = 0;
        assert!(emit(zero, GENESIS_HASH).is_err());
    }
}
