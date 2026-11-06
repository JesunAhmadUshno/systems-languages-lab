// UNEXECUTED source. See lib.rs: no Rust toolchain on this VM.
// The Build error shape, carried into Deep unchanged: a custom
// error type with a clean source chain, used with Result and the
// ? operator across checker.rs, rules.rs, and main.rs.
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
