// UNEXECUTED source. This VM has no Rust toolchain (rustc and cargo
// not found, rechecked 2026-11-05), so this code was never compiled
// or run here. It is the Build grade Rust error shape the SPEC asks
// for: a custom error type with a clean source chain, used with
// Result and the ? operator in checker.rs and main.rs.
use std::fmt;

#[derive(Debug)]
pub enum CheckError {
    /// The tool record is malformed (for example, its name is empty).
    Malformed { tool: String, reason: String },
    /// Loading a manifest failed; the source error stays chained.
    Load { path: String, source: std::io::Error },
}

impl fmt::Display for CheckError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            CheckError::Malformed { tool, reason } => {
                write!(f, "malformed tool {tool}: {reason}")
            }
            CheckError::Load { path, source } => {
                write!(f, "load manifest {path}: {source}")
            }
        }
    }
}

impl std::error::Error for CheckError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            CheckError::Malformed { .. } => None,
            CheckError::Load { source, .. } => Some(source),
        }
    }
}

impl From<std::io::Error> for CheckError {
    fn from(source: std::io::Error) -> Self {
        CheckError::Load {
            path: String::from("<manifest>"),
            source,
        }
    }
}
