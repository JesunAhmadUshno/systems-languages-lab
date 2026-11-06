// UNEXECUTED source. See error.rs: no Rust toolchain on this VM.
pub mod checker;
pub mod error;

pub use checker::{check_all, check_tool, severity, CheckRecord, Tool};
pub use error::CheckError;
