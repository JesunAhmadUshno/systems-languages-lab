// UNEXECUTED source. See lib.rs: no Rust toolchain on this VM.
// The Deep sharing design: one Rule trait, eight rule structs.
// Each Build rule R1 to R8 becomes a small struct that implements
// Rule, so the checking logic lives in exactly one place per rule
// and is shared by the generic Checker and by the CheckerSet of
// trait objects in checker.rs. Adding a rule means adding one
// struct and one line in all_rules; no checker code changes.
use crate::tool::Tool;

/// One manifest rule. Implementors borrow the tool and answer
/// whether the tool breaks the rule. Severity is a rule property,
/// not checker logic, so summaries can group by it for free.
pub trait Rule {
    fn id(&self) -> &'static str;
    fn severity(&self) -> &'static str;
    fn applies(&self, tool: &Tool) -> bool;
}

pub struct WildcardPermission;
pub struct ShellWithoutAllowlist;
pub struct NetworkWithoutHosts;
pub struct WriteWithoutPaths;
pub struct MissingDescription;
pub struct UnpinnedVersion;
pub struct ExcessiveRate;
pub struct MissingOwner;

impl Rule for WildcardPermission {
    fn id(&self) -> &'static str { "R1" }
    fn severity(&self) -> &'static str { "high" }
    fn applies(&self, tool: &Tool) -> bool {
        tool.permissions.iter().any(|p| p == "*" || p.ends_with(":*"))
    }
}

impl Rule for ShellWithoutAllowlist {
    fn id(&self) -> &'static str { "R2" }
    fn severity(&self) -> &'static str { "high" }
    fn applies(&self, tool: &Tool) -> bool {
        tool.can_execute_shell && tool.shell_allowlist.is_empty()
    }
}

impl Rule for NetworkWithoutHosts {
    fn id(&self) -> &'static str { "R3" }
    fn severity(&self) -> &'static str { "medium" }
    fn applies(&self, tool: &Tool) -> bool {
        tool.network_access && tool.allowed_hosts.is_empty()
    }
}

impl Rule for WriteWithoutPaths {
    fn id(&self) -> &'static str { "R4" }
    fn severity(&self) -> &'static str { "medium" }
    fn applies(&self, tool: &Tool) -> bool {
        tool.fs_write && tool.allowed_paths.is_empty()
    }
}

impl Rule for MissingDescription {
    fn id(&self) -> &'static str { "R5" }
    fn severity(&self) -> &'static str { "low" }
    fn applies(&self, tool: &Tool) -> bool {
        tool.description.trim().is_empty()
    }
}

impl Rule for UnpinnedVersion {
    fn id(&self) -> &'static str { "R6" }
    fn severity(&self) -> &'static str { "low" }
    fn applies(&self, tool: &Tool) -> bool {
        let version = tool.version.trim();
        version.is_empty() || version == "*" || version == "latest"
    }
}

impl Rule for ExcessiveRate {
    fn id(&self) -> &'static str { "R7" }
    fn severity(&self) -> &'static str { "medium" }
    fn applies(&self, tool: &Tool) -> bool {
        match tool.rate_limit_per_min {
            None => true,
            Some(rate) => rate > 1000,
        }
    }
}

impl Rule for MissingOwner {
    fn id(&self) -> &'static str { "R8" }
    fn severity(&self) -> &'static str { "low" }
    fn applies(&self, tool: &Tool) -> bool {
        tool.owner.trim().is_empty()
    }
}

/// The full Build rule set as trait objects, in rule id order.
/// The Vec<Box<dyn Rule>> shape is what lets eight different
/// concrete types share one checker path; see checker.rs.
pub fn all_rules() -> Vec<Box<dyn Rule>> {
    vec![
        Box::new(WildcardPermission),
        Box::new(ShellWithoutAllowlist),
        Box::new(NetworkWithoutHosts),
        Box::new(WriteWithoutPaths),
        Box::new(MissingDescription),
        Box::new(UnpinnedVersion),
        Box::new(ExcessiveRate),
        Box::new(MissingOwner),
    ]
}
