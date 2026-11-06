"""Unit tests for Level 2, Build (P21 systems-languages-lab).

Every expected value is hand computed in BUILD-SPEC.md from the
fixtures in level-2-build/service_build.py and manifest_build.py:
health 8 of 10 healthy, routing 11 of 12 routed, errors 2 (one
http_error, one timeout), cancellation 0 probed and 10 skipped,
manifest 5 of 8 unsafe with 14 flags (per rule R1 2, R2 1, R3 2,
R4 1, R5 1, R6 3, R7 3, R8 1; per severity high 3, medium 6, low 5).
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))

import manifest_build as mb
import service_build as sb


class TestBuildHealth(unittest.TestCase):
    def setUp(self):
        self.records, self.info = sb.run_probes_build(sb.ENDPOINTS_BUILD, workers=4)

    def test_counts(self):
        s = sb.summarise_health_build(self.records)
        self.assertEqual(s["endpoints_total"], 10)
        self.assertEqual(s["endpoints_healthy"], 8)

    def test_by_model(self):
        s = sb.summarise_health_build(self.records)
        self.assertEqual(s["by_model"], {
            "chat": {"total": 4, "healthy": 3},
            "code": {"total": 2, "healthy": 2},
            "embed": {"total": 2, "healthy": 2},
            "vision": {"total": 2, "healthy": 1},
        })

    def test_pool_completed(self):
        self.assertEqual(self.info, {"probed": 10, "skipped": 0, "status": "completed"})

    def test_worker_count_invariance(self):
        one, _ = sb.run_probes_build(sb.ENDPOINTS_BUILD, workers=1)
        self.assertEqual(one, self.records)

    def test_workers_zero_rejected(self):
        with self.assertRaises(ValueError):
            sb.run_probes_build(sb.ENDPOINTS_BUILD, workers=0)

    def test_error_summary(self):
        e = sb.summarise_errors_build(self.records)
        self.assertEqual(e, {"errors_total": 2, "per_kind": {"http_error": 1, "timeout": 1}})

    def test_error_chain_shape(self):
        by_name = {r["name"]: r for r in self.records}
        self.assertEqual(by_name["gamma-chat"]["error_chain"],
                         ["probe transport failed: 503 unavailable", "probe gamma-chat"])
        self.assertEqual(by_name["gamma-vision"]["error_kind"], "timeout")
        self.assertEqual(by_name["alpha-chat"]["error_chain"], [])

    def test_service_error_chain(self):
        base = sb.ServiceError("transport failed")
        wrapped = sb.ServiceError("probe x", cause=base)
        self.assertEqual(wrapped.chain, ["transport failed", "probe x"])
        self.assertIn("probe x", str(wrapped))
        self.assertIn("transport failed", str(wrapped))


class TestBuildCancellation(unittest.TestCase):
    def test_cancelled_before_start(self):
        token = sb.CancelToken()
        token.cancel()
        records, info = sb.run_probes_build(sb.ENDPOINTS_BUILD, workers=4, token=token)
        self.assertEqual(records, [])
        self.assertEqual(info, {"probed": 0, "skipped": 10, "status": "cancelled"})

    def test_uncancelled_token_completes(self):
        token = sb.CancelToken()
        self.assertFalse(token.cancelled)
        records, info = sb.run_probes_build(sb.ENDPOINTS_BUILD, workers=2, token=token)
        self.assertEqual(len(records), 10)
        self.assertEqual(info["status"], "completed")


class TestBuildRouting(unittest.TestCase):
    def setUp(self):
        self.records, _ = sb.run_probes_build(sb.ENDPOINTS_BUILD, workers=4)

    def test_route_picks(self):
        self.assertEqual(sb.route_build("chat", self.records), "delta-chat")
        self.assertEqual(sb.route_build("embed", self.records), "alpha-embed")
        self.assertEqual(sb.route_build("vision", self.records), "epsilon-vision")
        self.assertEqual(sb.route_build("code", self.records), "eta-code")
        self.assertIsNone(sb.route_build("unknown", self.records))

    def test_code_tie_break_is_name(self):
        # eta-code and zeta-code both healthy at 18; name ascending wins.
        self.assertEqual(sb.route_build("code", self.records), "eta-code")

    def test_routing_summary(self):
        recs = sb.run_routing_build(sb.REQUEST_MODELS_BUILD, self.records)
        s = sb.summarise_routing_build(recs)
        self.assertEqual(s["requests_total"], 12)
        self.assertEqual(s["requests_routed"], 11)
        self.assertEqual(s["requests_unrouted"], 1)
        self.assertEqual(s["per_endpoint"],
                         {"alpha-embed": 2, "delta-chat": 3, "epsilon-vision": 3, "eta-code": 3})

    def test_routing_order(self):
        recs = sb.run_routing_build(sb.REQUEST_MODELS_BUILD, self.records)
        self.assertEqual([r["routed_to"] for r in recs],
                         ["delta-chat", "alpha-embed", "epsilon-vision", "eta-code",
                          "delta-chat", "epsilon-vision", "eta-code", "alpha-embed",
                          "delta-chat", "eta-code", "epsilon-vision", None])


class TestBuildManifest(unittest.TestCase):
    def setUp(self):
        self.records = mb.check_all_build(mb.TOOLS_BUILD)
        self.by_name = {r["name"]: r for r in self.records}

    def test_per_tool_flags(self):
        self.assertEqual(self.by_name["file_reader"]["flags"], [])
        self.assertEqual(self.by_name["shell_runner"]["flags"], ["R1", "R2", "R6", "R7", "R8"])
        self.assertEqual(self.by_name["web_fetch"]["flags"], ["R3"])
        self.assertEqual(self.by_name["code_writer"]["flags"], ["R4", "R5", "R6"])
        self.assertEqual(self.by_name["data_query"]["flags"], [])
        self.assertEqual(self.by_name["admin_tool"]["flags"], ["R1", "R3", "R7"])
        self.assertEqual(self.by_name["vision_tool"]["flags"], ["R6", "R7"])
        self.assertEqual(self.by_name["scoped_writer"]["flags"], [])

    def test_summary(self):
        s = mb.summarise_build(self.records)
        self.assertEqual(s["tools_total"], 8)
        self.assertEqual(s["tools_unsafe"], 5)
        self.assertEqual(s["tools_safe"], 3)
        self.assertEqual(s["total_flags"], 14)
        self.assertEqual(s["flags_per_rule"],
                         {"R1": 2, "R2": 1, "R3": 2, "R4": 1, "R5": 1, "R6": 3, "R7": 3, "R8": 1})

    def test_severity_summary(self):
        s = mb.summarise_build(self.records)
        self.assertEqual(s["flags_per_severity"], {"high": 3, "medium": 6, "low": 5})

    def test_rate_boundary(self):
        base = dict(mb.TOOLS_BUILD[0])
        self.assertEqual(mb.check_tool_build(dict(base, rate_limit_per_min=1000)), [])
        self.assertEqual(mb.check_tool_build(dict(base, rate_limit_per_min=1001)), ["R7"])
        self.assertEqual(mb.check_tool_build(dict(base, rate_limit_per_min=None)), ["R7"])

    def test_version_variants(self):
        base = dict(mb.TOOLS_BUILD[0])
        for bad in ("", "*", "latest"):
            self.assertEqual(mb.check_tool_build(dict(base, version=bad)), ["R6"])
        self.assertEqual(mb.check_tool_build(dict(base, version="0.1.0")), [])

    def test_missing_name_raises_chained(self):
        bad = dict(mb.TOOLS_BUILD[0], name="")
        with self.assertRaises(mb.ManifestError) as ctx:
            mb.check_tool_build(bad)
        self.assertEqual(ctx.exception.chain, ["tool name is missing", "validate tool"])

    def test_duplicates(self):
        self.assertEqual(mb.find_duplicates(mb.TOOLS_BUILD), [])
        doubled = mb.TOOLS_BUILD + [mb.TOOLS_BUILD[0]]
        self.assertEqual(mb.find_duplicates(doubled), ["file_reader"])

    def test_scoped_writer_safe_despite_write(self):
        # fs_write is true but allowed_paths is set, so no R4.
        self.assertTrue(self.by_name["scoped_writer"]["safe"])


if __name__ == "__main__":
    unittest.main()
