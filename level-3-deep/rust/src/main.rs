// UNEXECUTED source. See lib.rs: no Rust toolchain on this VM, so
// this command was never built or run here. It shows the native
// entry point shape for the Deep checker: the trait object set
// runs the full manifest, one generic Checker shows a single rule
// hot path, and errors propagate with ? to main as a Result.
use manifest_checker_deep::rules::WildcardPermission;
use manifest_checker_deep::{CheckError, Checker, CheckerSet, Tool};

fn sample_tools() -> Vec<Tool> {
    vec![
        Tool {
            name: String::from("file_reader"),
            description: String::from("Read a file inside the workspace."),
            permissions: vec![String::from("fs:read")],
            can_execute_shell: false,
            shell_allowlist: Vec::new(),
            network_access: false,
            allowed_hosts: Vec::new(),
            fs_write: false,
            allowed_paths: Vec::new(),
            version: String::from("1.2.0"),
            rate_limit_per_min: Some(60),
            owner: String::from("platform"),
        },
        Tool {
            name: String::from("shell_runner"),
            description: String::from("Run shell commands for the user."),
            permissions: vec![String::from("shell:*")],
            can_execute_shell: true,
            shell_allowlist: Vec::new(),
            network_access: false,
            allowed_hosts: Vec::new(),
            fs_write: false,
            allowed_paths: Vec::new(),
            version: String::from("*"),
            rate_limit_per_min: Some(2000),
            owner: String::new(),
        },
    ]
}

fn run() -> Result<(), CheckError> {
    let tools = sample_tools();
    let set = CheckerSet::with_build_rules();
    let records = set.check_all(&tools)?;
    for record in &records {
        println!("{} flags {:?}", record.name, record.flags);
    }
    let single = Checker::new(WildcardPermission);
    println!("R1 on first tool: {}", single.flags(&tools[0])?);
    Ok(())
}

fn main() {
    if let Err(err) = run() {
        eprintln!("manifest-checker-deep: {err}");
        std::process::exit(1);
    }
}
