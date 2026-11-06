// UNEXECUTED source. See lib.rs: no Rust toolchain on this VM.
// Two ways the Rule trait is shared, side by side on purpose:
// 1. Checker<R: Rule> is generic over one rule type. The compiler
//    monomorphises it, so a single rule check inlines with no
//    dynamic dispatch cost. It serves hot single rule callers.
// 2. CheckerSet owns Vec<Box<dyn Rule>> trait objects. The eight
//    heterogeneous rules share one check and check_all path with
//    dynamic dispatch. It serves the full manifest run, where the
//    rule set is data, not a type.
use crate::error::CheckError;
use crate::rules::{all_rules, Rule};
use crate::tool::Tool;

#[derive(Debug)]
pub struct CheckRecord {
    pub name: String,
    pub flags: Vec<&'static str>,
    pub severities: Vec<&'static str>,
    pub safe: bool,
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

/// Generic single rule checker (static dispatch).
pub struct Checker<R: Rule> {
    rule: R,
}

impl<R: Rule> Checker<R> {
    pub fn new(rule: R) -> Self {
        Checker { rule }
    }

    /// Borrow a tool, answer whether this one rule flags it.
    pub fn flags(&self, tool: &Tool) -> Result<bool, CheckError> {
        validate(tool)?;
        Ok(self.rule.applies(tool))
    }

    pub fn rule_id(&self) -> &'static str {
        self.rule.id()
    }
}

/// The full rule set as trait objects (dynamic dispatch).
pub struct CheckerSet {
    rules: Vec<Box<dyn Rule>>,
}

impl CheckerSet {
    pub fn with_build_rules() -> Self {
        CheckerSet { rules: all_rules() }
    }

    pub fn check_tool(&self, tool: &Tool) -> Result<Vec<&'static str>, CheckError> {
        validate(tool)?;
        let mut flags: Vec<&'static str> = Vec::new();
        for rule in &self.rules {
            if rule.applies(tool) {
                flags.push(rule.id());
            }
        }
        flags.sort_unstable();
        Ok(flags)
    }

    pub fn check_all(&self, tools: &[Tool]) -> Result<Vec<CheckRecord>, CheckError> {
        let mut out = Vec::with_capacity(tools.len());
        for tool in tools {
            let flags = self.check_tool(tool)?;
            let mut severities: Vec<&'static str> = flags
                .iter()
                .map(|id| {
                    self.rules
                        .iter()
                        .find(|r| r.id() == *id)
                        .map(|r| r.severity())
                        .unwrap_or("low")
                })
                .collect();
            severities.sort_unstable();
            severities.dedup();
            out.push(CheckRecord {
                name: tool.name.clone(),
                safe: flags.is_empty(),
                flags,
                severities,
            });
        }
        Ok(out)
    }
}
