// UNEXECUTED source. See error.rs: no Rust toolchain on this VM, so
// this code was never compiled or run here. Ownership notes: Tool
// owns its Strings and Vecs. check_tool borrows a Tool through a
// shared reference and returns an owned Vec of rule ids, so the
// caller keeps ownership of every tool. check_all takes ownership
// of a Vec<Tool> by value, checks each by reference, and returns
// owned CheckRecord values: no clone of a tool is ever needed.
use crate::error::CheckError;

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

#[derive(Debug)]
pub struct CheckRecord {
    pub name: String,
    pub flags: Vec<&'static str>,
    pub safe: bool,
}

pub fn severity(rule: &str) -> &'static str {
    match rule {
        "R1" | "R2" => "high",
        "R3" | "R4" | "R7" => "medium",
        _ => "low",
    }
}

fn validate(tool: &Tool) -> Result<(), CheckError> {
    if tool.name.trim().is_empty() {
        return Err(CheckError::Malformed {
            tool: String::from("<unnamed>"),
            reason: String::from("tool name is missing"),
        });
    }
    Ok(())
}

/// Check one borrowed tool. Errors propagate as CheckError, so a
/// caller can use ? and keep the chain intact.
pub fn check_tool(tool: &Tool) -> Result<Vec<&'static str>, CheckError> {
    validate(tool)?;
    let mut flags: Vec<&'static str> = Vec::new();
    if tool
        .permissions
        .iter()
        .any(|p| p == "*" || p.ends_with(":*"))
    {
        flags.push("R1");
    }
    if tool.can_execute_shell && tool.shell_allowlist.is_empty() {
        flags.push("R2");
    }
    if tool.network_access && tool.allowed_hosts.is_empty() {
        flags.push("R3");
    }
    if tool.fs_write && tool.allowed_paths.is_empty() {
        flags.push("R4");
    }
    if tool.description.trim().is_empty() {
        flags.push("R5");
    }
    let version = tool.version.trim();
    if version.is_empty() || version == "*" || version == "latest" {
        flags.push("R6");
    }
    match tool.rate_limit_per_min {
        None => flags.push("R7"),
        Some(rate) if rate > 1000 => flags.push("R7"),
        Some(_) => {}
    }
    if tool.owner.trim().is_empty() {
        flags.push("R8");
    }
    flags.sort_unstable();
    Ok(flags)
}

/// Check owned tools, moving each record out as an owned value.
pub fn check_all(tools: Vec<Tool>) -> Result<Vec<CheckRecord>, CheckError> {
    let mut out = Vec::with_capacity(tools.len());
    for tool in &tools {
        let flags = check_tool(tool)?;
        out.push(CheckRecord {
            name: tool.name.clone(),
            safe: flags.is_empty(),
            flags,
        });
    }
    Ok(out)
}
