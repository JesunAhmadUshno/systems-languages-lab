"""MCP tool manifest checker: the Rust Learn idea, executed in Python.

SPEC Track B (Rust) asks for a small CLI in the P09 toolkit family: a tool
manifest checker that reads MCP tool definitions and flags unsafe rules.

This VM has no Rust toolchain (checked 2026-11-05: rustc not found), so
this file is the executed reference implementation of the same checker
logic in Python stdlib. The Rust teaching source sits beside this file in
rust/manifest_checker.rs and is labelled unexecuted there and in the
level README. No claim in this repo says the Rust source was compiled
or run.

Checker rules (each flag names its rule id):
- R1 wildcard_permission: a permission is "*" or ends with ":*".
- R2 shell_exec_unscoped: the tool can execute shell commands and its
  shell allowlist is empty.
- R3 network_unscoped: the tool has network access and its allowed
  hosts list is empty.
- R4 fs_write_unscoped: the tool can write files and its allowed
  paths list is empty.
- R5 missing_description: the tool description is empty or missing.

A tool with at least one flag is unsafe. A tool with no flags is safe.
"""

# Fixture manifests, authored for teaching. Every expected flag in the
# tests is hand computed from this table and the rules above.
TOOLS = [
    {"name": "file_reader", "description": "Read a file inside the workspace.",
     "permissions": ["fs:read"], "can_execute_shell": False, "shell_allowlist": [],
     "network_access": False, "allowed_hosts": [], "fs_write": False, "allowed_paths": []},
    {"name": "shell_runner", "description": "Run shell commands for the user.",
     "permissions": ["shell:*"], "can_execute_shell": True, "shell_allowlist": [],
     "network_access": False, "allowed_hosts": [], "fs_write": False, "allowed_paths": []},
    {"name": "web_fetch", "description": "Fetch a web page.",
     "permissions": ["net:fetch"], "can_execute_shell": False, "shell_allowlist": [],
     "network_access": True, "allowed_hosts": [], "fs_write": False, "allowed_paths": []},
    {"name": "code_writer", "description": "",
     "permissions": ["fs:write"], "can_execute_shell": False, "shell_allowlist": [],
     "network_access": False, "allowed_hosts": [], "fs_write": True, "allowed_paths": []},
    {"name": "data_query", "description": "Query the internal data API.",
     "permissions": ["db:read"], "can_execute_shell": False, "shell_allowlist": [],
     "network_access": True, "allowed_hosts": ["api.internal"], "fs_write": False, "allowed_paths": []},
    {"name": "admin_tool", "description": "Administration helper.",
     "permissions": ["*"], "can_execute_shell": True, "shell_allowlist": ["ls"],
     "network_access": True, "allowed_hosts": [], "fs_write": True, "allowed_paths": ["/tmp/work"]},
]

RULE_IDS = ["R1", "R2", "R3", "R4", "R5"]


def check_tool(tool):
    """Return the sorted list of rule ids this tool breaks."""
    flags = []
    perms = tool.get("permissions", [])
    if any(p == "*" or p.endswith(":*") for p in perms):
        flags.append("R1")
    if tool.get("can_execute_shell") and not tool.get("shell_allowlist"):
        flags.append("R2")
    if tool.get("network_access") and not tool.get("allowed_hosts"):
        flags.append("R3")
    if tool.get("fs_write") and not tool.get("allowed_paths"):
        flags.append("R4")
    if not (tool.get("description") or "").strip():
        flags.append("R5")
    return sorted(flags)


def check_all(tools):
    """Check every tool. Returns per-tool records in input order."""
    out = []
    for tool in tools:
        flags = check_tool(tool)
        out.append({"name": tool["name"], "flags": flags, "flag_count": len(flags), "safe": not flags})
    return out


def summarise(records):
    per_rule = {rid: 0 for rid in RULE_IDS}
    total_flags = 0
    unsafe = 0
    for rec in records:
        total_flags += rec["flag_count"]
        if not rec["safe"]:
            unsafe += 1
        for f in rec["flags"]:
            per_rule[f] += 1
    return {
        "tools_total": len(records),
        "tools_unsafe": unsafe,
        "tools_safe": len(records) - unsafe,
        "total_flags": total_flags,
        "flags_per_rule": per_rule,
    }
