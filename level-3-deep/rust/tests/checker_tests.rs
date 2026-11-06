// UNEXECUTED source. See ../src/lib.rs: no Rust toolchain on this
// VM, so these tests were never compiled or run here. Expected
// values mirror the Python Build oracle for the same fixtures:
// shell_runner breaks R1 R2 R6 R7 R8; file_reader breaks none.
use manifest_checker_deep::rules::{ExcessiveRate, WildcardPermission};
use manifest_checker_deep::{Checker, CheckerSet, Tool};

fn tool(name: &str) -> Tool {
    Tool {
        name: String::from(name),
        description: String::from("A tool."),
        permissions: vec![String::from("fs:read")],
        can_execute_shell: false,
        shell_allowlist: Vec::new(),
        network_access: false,
        allowed_hosts: Vec::new(),
        fs_write: false,
        allowed_paths: Vec::new(),
        version: String::from("1.0.0"),
        rate_limit_per_min: Some(60),
        owner: String::from("platform"),
    }
}

#[test]
fn safe_tool_has_no_flags() {
    let set = CheckerSet::with_build_rules();
    let flags = set.check_tool(&tool("file_reader")).unwrap();
    assert!(flags.is_empty());
}

#[test]
fn shell_runner_flags_match_python_oracle() {
    let mut t = tool("shell_runner");
    t.permissions = vec![String::from("shell:*")];
    t.can_execute_shell = true;
    t.version = String::from("*");
    t.rate_limit_per_min = Some(2000);
    t.owner = String::new();
    let set = CheckerSet::with_build_rules();
    let flags = set.check_tool(&t).unwrap();
    assert_eq!(flags, vec!["R1", "R2", "R6", "R7", "R8"]);
}

#[test]
fn generic_single_rule_checker() {
    let checker = Checker::new(WildcardPermission);
    let mut t = tool("admin_tool");
    assert_eq!(checker.flags(&t).unwrap(), false);
    t.permissions = vec![String::from("*")];
    assert_eq!(checker.flags(&t).unwrap(), true);
    let rate = Checker::new(ExcessiveRate);
    assert_eq!(rate.rule_id(), "R7");
    assert_eq!(rate.flags(&t).unwrap(), false);
}

#[test]
fn unnamed_tool_is_a_chained_error() {
    let set = CheckerSet::with_build_rules();
    let err = set.check_tool(&tool("")).unwrap_err();
    assert!(format!("{err}").contains("tool name is missing"));
}
