"""Unit tests for Level 1, Learn (P21 systems-languages-lab).

Every expected value below is hand computed from the fixtures in
level-1-learn/health_service.py and level-1-learn/manifest_checker.py.

Health hand computation:
- 6 endpoints, probe_ok true for alpha-chat, beta-chat, alpha-embed,
  beta-embed: 4 healthy, 2 unhealthy (gamma-chat 503, gamma-vision
  timeout).
- By model: chat 2 of 3 healthy, embed 2 of 2, vision 0 of 1.
- Routing rule (healthy only, lowest latency, name tie break):
  chat picks beta-chat (25 against 40), embed picks alpha-embed
  (15 against 30), vision picks nothing (no healthy endpoint).
- 8 requests (chat, chat, embed, vision, chat, embed, vision, chat):
  6 routed (beta-chat 4, alpha-embed 2), 2 unrouted (both vision).

Manifest hand computation (rules R1 to R5 in manifest_checker.py):
- file_reader: no flags. shell_runner: R1, R2. web_fetch: R3.
  code_writer: R4, R5. data_query: no flags. admin_tool: R1, R3
  (shell has an allowlist, fs write has paths, so no R2 and no R4).
- Totals: 6 tools, 4 unsafe, 2 safe, 7 flags.
  Per rule: R1 2, R2 1, R3 2, R4 1, R5 1. Sum 2+1+2+1+1 = 7.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-1-learn"))

import health_service as hs  # noqa: E402
import manifest_checker as mc  # noqa: E402


class TestHealth(unittest.TestCase):
    def setUp(self):
        self.records = hs.run_probes(hs.ENDPOINTS, workers=3)

    def test_counts(self):
        s = hs.summarise_health(self.records)
        self.assertEqual(s["endpoints_total"], 6)
        self.assertEqual(s["endpoints_healthy"], 4)

    def test_by_model(self):
        s = hs.summarise_health(self.records)
        self.assertEqual(s["by_model"], {
            "chat": {"total": 3, "healthy": 2},
            "embed": {"total": 2, "healthy": 2},
            "vision": {"total": 1, "healthy": 0},
        })

    def test_unhealthy_named(self):
        bad = sorted(r["name"] for r in self.records if not r["healthy"])
        self.assertEqual(bad, ["gamma-chat", "gamma-vision"])

    def test_worker_count_invariance(self):
        one = hs.run_probes(hs.ENDPOINTS, workers=1)
        four = hs.run_probes(hs.ENDPOINTS, workers=4)
        self.assertEqual(one, self.records)
        self.assertEqual(four, self.records)

    def test_workers_zero_rejected(self):
        with self.assertRaises(ValueError):
            hs.run_probes(hs.ENDPOINTS, workers=0)

    def test_records_sorted_by_name(self):
        names = [r["name"] for r in self.records]
        self.assertEqual(names, sorted(names))


class TestRouting(unittest.TestCase):
    def setUp(self):
        self.records = hs.run_probes(hs.ENDPOINTS, workers=3)

    def test_route_choices(self):
        self.assertEqual(hs.route("chat", self.records), "beta-chat")
        self.assertEqual(hs.route("embed", self.records), "alpha-embed")
        self.assertIsNone(hs.route("vision", self.records))
        self.assertIsNone(hs.route("unknown-model", self.records))

    def test_unhealthy_never_routed(self):
        # gamma-chat ties beta-chat on latency (25) but is unhealthy.
        for _ in range(3):
            self.assertNotEqual(hs.route("chat", self.records), "gamma-chat")

    def test_routing_summary(self):
        recs = hs.run_routing(hs.REQUEST_MODELS, self.records)
        s = hs.summarise_routing(recs)
        self.assertEqual(s["requests_total"], 8)
        self.assertEqual(s["requests_routed"], 6)
        self.assertEqual(s["requests_unrouted"], 2)
        self.assertEqual(s["per_endpoint"], {"alpha-embed": 2, "beta-chat": 4})

    def test_routing_order(self):
        recs = hs.run_routing(hs.REQUEST_MODELS, self.records)
        targets = [r["routed_to"] for r in recs]
        self.assertEqual(targets, ["beta-chat", "beta-chat", "alpha-embed", None,
                                   "beta-chat", "alpha-embed", None, "beta-chat"])


class TestManifest(unittest.TestCase):
    def setUp(self):
        self.records = mc.check_all(mc.TOOLS)
        self.by_name = {r["name"]: r for r in self.records}

    def test_per_tool_flags(self):
        self.assertEqual(self.by_name["file_reader"]["flags"], [])
        self.assertEqual(self.by_name["shell_runner"]["flags"], ["R1", "R2"])
        self.assertEqual(self.by_name["web_fetch"]["flags"], ["R3"])
        self.assertEqual(self.by_name["code_writer"]["flags"], ["R4", "R5"])
        self.assertEqual(self.by_name["data_query"]["flags"], [])
        self.assertEqual(self.by_name["admin_tool"]["flags"], ["R1", "R3"])

    def test_summary(self):
        s = mc.summarise(self.records)
        self.assertEqual(s["tools_total"], 6)
        self.assertEqual(s["tools_unsafe"], 4)
        self.assertEqual(s["tools_safe"], 2)
        self.assertEqual(s["total_flags"], 7)
        self.assertEqual(s["flags_per_rule"], {"R1": 2, "R2": 1, "R3": 2, "R4": 1, "R5": 1})

    def test_scoped_shell_not_flagged_r2(self):
        tool = {"name": "scoped", "description": "d", "permissions": ["shell:run"],
                "can_execute_shell": True, "shell_allowlist": ["ls"],
                "network_access": False, "allowed_hosts": [],
                "fs_write": False, "allowed_paths": []}
        self.assertEqual(mc.check_tool(tool), [])

    def test_empty_tool_flags_only_r5(self):
        tool = {"name": "empty", "description": "  ", "permissions": [],
                "can_execute_shell": False, "shell_allowlist": [],
                "network_access": False, "allowed_hosts": [],
                "fs_write": False, "allowed_paths": []}
        self.assertEqual(mc.check_tool(tool), ["R5"])

    def test_wildcard_variants(self):
        base = {"name": "w", "description": "d", "can_execute_shell": False,
                "shell_allowlist": [], "network_access": False, "allowed_hosts": [],
                "fs_write": False, "allowed_paths": []}
        self.assertEqual(mc.check_tool(dict(base, permissions=["*"])), ["R1"])
        self.assertEqual(mc.check_tool(dict(base, permissions=["db:*"])), ["R1"])
        self.assertEqual(mc.check_tool(dict(base, permissions=["db:read"])), [])


if __name__ == "__main__":
    unittest.main()
