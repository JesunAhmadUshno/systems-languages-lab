// Teaching source, NOT compiled or run in this Learn level.
// This VM has no Rust toolchain (rustc not found, checked 2026-11-05), so
// this file was never built here. It shows the same manifest checker
// rules as the executed Python reference (../manifest_checker.py) in a
// Rust shape: a struct with borrowed string slices, a check function
// returning a Vec of rule ids, and a main that prints the fixture
// verdicts. Read it beside the Python file. The Build level compiles
// and tests this track with a real toolchain, with ownership and
// Result based error handling as the SPEC Build scope names.

struct Tool {
    name: &'static str,
    description: &'static str,
    permissions: &'static [&'static str],
    can_execute_shell: bool,
    shell_allowlist: &'static [&'static str],
    network_access: bool,
    allowed_hosts: &'static [&'static str],
    fs_write: bool,
    allowed_paths: &'static [&'static str],
}

fn check(tool: &Tool) -> Vec<&'static str> {
    let mut flags = Vec::new();
    if tool.permissions.iter().any(|p| *p == "*" || p.ends_with(":*")) {
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
    flags
}

fn main() {
    let tools = [
        Tool { name: "file_reader", description: "Read a file inside the workspace.",
               permissions: &["fs:read"], can_execute_shell: false, shell_allowlist: &[],
               network_access: false, allowed_hosts: &[], fs_write: false, allowed_paths: &[] },
        Tool { name: "shell_runner", description: "Run shell commands for the user.",
               permissions: &["shell:*"], can_execute_shell: true, shell_allowlist: &[],
               network_access: false, allowed_hosts: &[], fs_write: false, allowed_paths: &[] },
        Tool { name: "admin_tool", description: "Administration helper.",
               permissions: &["*"], can_execute_shell: true, shell_allowlist: &["ls"],
               network_access: true, allowed_hosts: &[], fs_write: true, allowed_paths: &["/tmp/work"] },
    ];
    for tool in &tools {
        println!("{} flags {:?}", tool.name, check(tool));
    }
}
