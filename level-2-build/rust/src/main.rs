// UNEXECUTED source. See error.rs: no Rust toolchain on this VM, so
// this binary was never built or run here. main returns a Result,
// so a CheckError prints its Display text and the process exits
// nonzero, with the source chain available to any caller that
// inspects the error instead of only printing it.
use manifest_checker::{check_all, CheckError, Tool};

fn fixture_tools() -> Vec<Tool> {
    vec![
        Tool {
            name: String::from("file_reader"),
            description: String::from("Read a file inside the workspace."),
            permissions: vec![String::from("fs:read")],
            can_execute_shell: false,
            shell_allowlist: vec![],
            network_access: false,
            allowed_hosts: vec![],
            fs_write: false,
            allowed_paths: vec![],
            version: String::from("1.2.0"),
            rate_limit_per_min: Some(60),
            owner: String::from("platform"),
        },
        Tool {
            name: String::from("shell_runner"),
            description: String::from("Run shell commands for the user."),
            permissions: vec![String::from("shell:*")],
            can_execute_shell: true,
            shell_allowlist: vec![],
            network_access: false,
            allowed_hosts: vec![],
            fs_write: false,
            allowed_paths: vec![],
            version: String::from("*"),
            rate_limit_per_min: Some(2000),
            owner: String::new(),
        },
    ]
}

fn run() -> Result<(), CheckError> {
    let records = check_all(fixture_tools())?;
    for record in &records {
        println!("{} flags {:?}", record.name, record.flags);
    }
    Ok(())
}

fn main() {
    if let Err(err) = run() {
        eprintln!("manifest-checker: {err}");
        let mut source = std::error::Error::source(&err);
        while let Some(cause) = source {
            eprintln!("caused by: {cause}");
            source = cause.source();
        }
        std::process::exit(1);
    }
}
