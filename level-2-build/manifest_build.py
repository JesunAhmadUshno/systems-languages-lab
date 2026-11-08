"""Build level MCP tool manifest checker: the Rust Build idea,
executed in Python.

SPEC Track B (Rust) Build asks for ownership and borrowing in real
code and error handling with Result types and clean error chains.

This VM has no Rust toolchain (rechecked 2026-11-05: rustc and cargo
not found), so this file is the executed Build reference in Python
stdlib. The Rust Build source sits in rust/ in this folder (Cargo
layout, a custom error type with a source chain, Result and the ?
operator in spirit) and is labelled UNEXECUTED there and in the
REPORT.md. No claim says it was compiled or run.

Build extension over Learn (rules R1 to R5 unchanged):
- R6 unpinned_version: version missing, empty, "*" or "latest".
- R7 excessive_rate: rate limit missing or above 1000 per minute.
- R8 missing_owner: owner empty or missing.
Each rule has a severity. Validation failures raise ManifestError
with a chain, the analogue of a Rust error type with a source chain.
Duplicate tool names are reported, not hidden.
"""


class ManifestError(Exception):
    """An error with a context string, a cause, and a chain list."""

    def __init__(self, context, cause=None):
        super().__init__(context)
        self.context = context
        self.cause = cause
        if isinstance(cause, ManifestError):
            self.chain = cause.chain + [context]
        elif cause is not None:
            self.chain = [str(cause), context]
        else:
            self.chain = [context]

    def __str__(self):
        return ": caused by: ".join(reversed(self.chain))


RULE_IDS_BUILD = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]

SEVERITY = {"R1": "high", "R2": "high", "R3": "medium", "R4": "medium",
            "R5": "low", "R6": "low", "R7": "medium", "R8": "low"}

TOOLS_BUILD = [
    {"name": "file_reader", "description": "Read a file inside the workspace.",
     "permissions": ["fs:read"], "can_execute_shell": False, "shell_allowlist": [],
     "network_access": False, "allowed_hosts": [], "fs_write": False,
     "allowed_paths": [], "version": "1.2.0", "rate_limit_per_min": 60, "owner": "platform"},
    {"name": "shell_runner", "description": "Run shell commands for the user.",
     "permissions": ["shell:*"], "can_execute_shell": True, "shell_allowlist": [],
     "network_access": False, "allowed_hosts": [], "fs_write": False,
     "allowed_paths": [], "version": "*", "rate_limit_per_min": 2000, "owner": ""},
    {"name": "web_fetch", "description": "Fetch a web page.",
     "permissions": ["net:fetch"], "can_execute_shell": False, "shell_allowlist": [],
     "network_access": True, "allowed_hosts": [], "fs_write": False,
     "allowed_paths": [], "version": "0.9.1", "rate_limit_per_min": 120, "owner": "data"},
    {"name": "code_writer", "description": "",
     "permissions": ["fs:write"], "can_execute_shell": False, "shell_allowlist": [],
     "network_access": False, "allowed_hosts": [], "fs_write": True,
     "allowed_paths": [], "version": "latest", "rate_limit_per_min": 30, "owner": "dev"},
    {"name": "data_query", "description": "Query the internal data API.",
     "permissions": ["db:read"], "can_execute_shell": False, "shell_allowlist": [],
     "network_access": True, "allowed_hosts": ["api.internal"], "fs_write": False,
     "allowed_paths": [], "version": "2.0.0", "rate_limit_per_min": 500, "owner": "data"},
    {"name": "admin_tool", "description": "Administration helper.",
     "permissions": ["*"], "can_execute_shell": True, "shell_allowlist": ["ls"],
     "network_access": True, "allowed_hosts": [], "fs_write": True,
     "allowed_paths": ["/tmp/work"], "version": "1.0.0", "rate_limit_per_min": 1500, "owner": "platform"},
    {"name": "vision_tool", "description": "Run the vision model.",
     "permissions": ["model:vision"], "can_execute_shell": False, "shell_allowlist": [],
     "network_access": False, "allowed_hosts": [], "fs_write": False,
     "allowed_paths": [], "version": "", "rate_limit_per_min": None, "owner": "ml"},
    {"name": "scoped_writer", "description": "Write scoped reports.",
     "permissions": ["fs:write"], "can_execute_shell": False, "shell_allowlist": [],
     "network_access": False, "allowed_hosts": [], "fs_write": True,
     "allowed_paths": ["/tmp/reports"], "version": "3.1.0", "rate_limit_per_min": 100, "owner": "ml"},
]


def validate_tool(tool):
    """Raise a chained ManifestError when a tool is malformed."""
    if not isinstance(tool, dict):
        raise ManifestError("validate tool", cause=ManifestError("tool is not a mapping"))
    if not (tool.get("name") or "").strip():
        raise ManifestError("validate tool", cause=ManifestError("tool name is missing"))
    return tool


def check_tool_build(tool):
    """Return the sorted list of rule ids this tool breaks (R1 to R8)."""
    validate_tool(tool)
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
    version = (tool.get("version") or "").strip()
    if version in ("", "*", "latest"):
        flags.append("R6")
    rate = tool.get("rate_limit_per_min")
    if rate is None or rate > 1000:
        flags.append("R7")
    if not (tool.get("owner") or "").strip():
        flags.append("R8")
    return sorted(flags)


def check_all_build(tools):
    """Check every tool. Returns per tool records in input order."""
    out = []
    for tool in tools:
        flags = check_tool_build(tool)
        out.append({"name": tool["name"], "flags": flags,
                    "flag_count": len(flags), "safe": not flags,
                    "severities": sorted({SEVERITY[f] for f in flags})})
    return out


def find_duplicates(tools):
    seen = {}
    dups = []
    for tool in tools:
        name = tool.get("name")
        seen[name] = seen.get(name, 0) + 1
        if seen[name] == 2:
            dups.append(name)
    return sorted(dups)


def summarise_build(records):
    per_rule = {rid: 0 for rid in RULE_IDS_BUILD}
    per_severity = {"high": 0, "medium": 0, "low": 0}
    total = 0
    unsafe = 0
    for rec in records:
        total += rec["flag_count"]
        if not rec["safe"]:
            unsafe += 1
        for f in rec["flags"]:
            per_rule[f] += 1
            per_severity[SEVERITY[f]] += 1
    return {"tools_total": len(records), "tools_unsafe": unsafe,
            "tools_safe": len(records) - unsafe, "total_flags": total,
            "flags_per_rule": per_rule, "flags_per_severity": per_severity}
