// UNEXECUTED source. See lib.rs: no Rust toolchain on this VM.
// Ownership notes: Tool owns its Strings and Vecs. Rules borrow a
// Tool through a shared reference and return plain values, so the
// caller keeps ownership of every tool and no clone is needed to
// run all eight rules over one tool.

#[derive(Debug, Clone)]
pub struct Tool {
    pub name: String,
    pub description: String,
    pub permissions: Vec<String>,
    pub can_execute_shell: bool,
    pub shell_allowlist: Vec<String>,
    pub network_access: bool,
    pub allowed_hosts: Vec<String>,
    pub fs_write: bool,
    pub allowed_paths: Vec<String>,
    pub version: String,
    pub rate_limit_per_min: Option<u32>,
    pub owner: String,
}
