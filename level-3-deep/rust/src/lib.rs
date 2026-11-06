// UNEXECUTED source. This VM has no Rust toolchain (rustc and cargo
// not found, rechecked 2026-11-05), so this code was never compiled
// or run here. It is the Deep grade Rust shape of the executed
// Python reference in ../../level-2-build/manifest_build.py: the
// eight checker rules shared through a Rule trait, a generic
// Checker<R: Rule> (static dispatch), and a CheckerSet of trait
// objects (dynamic dispatch). No result in this level comes from
// this code.
pub mod checker;
pub mod error;
pub mod rules;
pub mod tool;

pub use checker::{CheckRecord, Checker, CheckerSet};
pub use error::CheckError;
pub use rules::Rule;
pub use tool::Tool;
