// UNEXECUTED source. See ../src/error.rs: no Rust toolchain on this
// VM, so these integration tests were never run here. They show the
// native shape: tests in tests/, run with cargo test on a node with
// the toolchain, with hand computed expected flags.
use manifest_checker::{check_all, check_tool, Tool};

fn tool(name: &str) -> Tool {
    Tool {
        name: String::from(name),
        description: String::from("A scoped tool."),
        permissions: vec![String::from("fs:read")],
        can_execute_shell: false,
        shell_allowlist: vec![],
        network_access: false,
        allowed_hosts: vec![],
        fs_write: false,
        allowed_paths: vec![],
        version: String::from("1.0.0"),
        rate_limit_per_min: Some(60),
        owner: String::from("platform"),
    }
}

#[test]
fn scoped_tool_is_safe() {
    let flags = check_tool(&tool("file_reader")).expect("check");
    assert!(flags.is_empty());
}

#[test]
fn wildcard_and_unscoped_shell_flag_five_rules() {
    let mut t = tool("shell_runner");
    t.permissions = vec![String::from("shell:*")];
    t.can_execute_shell = true;
    t.version = String::from("*");
    t.rate_limit_per_min = Some(2000);
    t.owner = String::new();
    let flags = check_tool(&t).expect("check");
    assert_eq!(flags, vec!["R1", "R2", "R6", "R7", "R8"]);
}

#[test]
fn missing_name_is_a_chained_error() {
    let t = tool("");
    let err = check_tool(&t).expect_err("empty name must fail");
    assert!(err.to_string().contains("tool name is missing"));
}

#[test]
fn check_all_counts_unsafe() {
    let mut bad = tool("web_fetch");
    bad.network_access = true;
    let records = check_all(vec![tool("file_reader"), bad]).expect("check all");
    assert_eq!(records.len(), 2);
    assert!(records[0].safe);
    assert!(!records[1].safe);
    assert_eq!(records[1].flags, vec!["R3"]);
}
