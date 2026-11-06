"""Unit tests for Level 3, Deep (P21 systems-languages-lab).

Expected values come from DEEP-SPEC.md and the Build oracle: on the
Build fixtures the indexed router must reproduce Build routing
exactly (11 of 12 routed; delta-chat 3, alpha-embed 2,
epsilon-vision 3, eta-code 3). On the deterministic Deep workload
(200 endpoints, 20,000 requests) baseline and indexed routing
records must be identical as full lists, with 16,000 routed and
4,000 unrouted (the unknown model share).
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "level-3-deep"))
sys.path.insert(0, os.path.join(ROOT, "level-2-build"))

import profile_deep as pd  # noqa: E402
import service_build as sb  # noqa: E402


class TestIndexedRouterOnBuildFixtures(unittest.TestCase):
    def setUp(self):
        self.records, _ = sb.run_probes_build(sb.ENDPOINTS_BUILD, workers=4)
        self.router = pd.IndexedRouter(self.records)

    def test_route_picks_match_build(self):
        for model in ["chat", "embed", "vision", "code", "unknown"]:
            self.assertEqual(self.router.route(model), sb.route_build(model, self.records))

    def test_routing_records_match_build_exactly(self):
        baseline = sb.run_routing_build(sb.REQUEST_MODELS_BUILD, self.records)
        indexed = self.router.run_routing(sb.REQUEST_MODELS_BUILD)
        self.assertEqual(indexed, baseline)

    def test_routing_summary_matches_build_oracle(self):
        indexed = self.router.run_routing(sb.REQUEST_MODELS_BUILD)
        s = sb.summarise_routing_build(indexed)
        self.assertEqual(s["requests_total"], 12)
        self.assertEqual(s["requests_routed"], 11)
        self.assertEqual(s["requests_unrouted"], 1)
        self.assertEqual(s["per_endpoint"],
                         {"alpha-embed": 2, "delta-chat": 3, "epsilon-vision": 3, "eta-code": 3})

    def test_unhealthy_never_indexed(self):
        self.assertIsNone(self.router.route("unknown"))
        names = {rec["name"] for rec in self.router._best.values()}
        self.assertNotIn("gamma-chat", names)
        self.assertNotIn("gamma-vision", names)

    def test_tie_break_is_name(self):
        self.assertEqual(self.router.route("code"), "eta-code")

    def test_empty_records_route_none(self):
        empty = pd.IndexedRouter([])
        self.assertIsNone(empty.route("chat"))


class TestWorkloadDeterminism(unittest.TestCase):
    def test_workload_generation_is_deterministic(self):
        self.assertEqual(pd.make_workload_endpoints(), pd.make_workload_endpoints())
        self.assertEqual(pd.make_workload_requests(), pd.make_workload_requests())
        self.assertEqual(len(pd.make_workload_endpoints()), 200)
        self.assertEqual(len(pd.make_workload_requests()), 20000)

    def test_workload_counts(self):
        endpoints = pd.make_workload_endpoints()
        records, info = sb.run_probes_build(endpoints, workers=4)
        self.assertEqual(info, {"probed": 200, "skipped": 0, "status": "completed"})
        health = sb.summarise_health_build(records)
        self.assertEqual(health["endpoints_total"], 200)
        self.assertEqual(health["endpoints_healthy"], 160)


class TestWorkloadCorrectnessEquality(unittest.TestCase):
    def test_baseline_and_indexed_records_identical(self):
        endpoints = pd.make_workload_endpoints()
        records, _info = sb.run_probes_build(endpoints, workers=4)
        requests = pd.make_workload_requests()
        baseline = sb.run_routing_build(requests, records)
        indexed = pd.IndexedRouter(records).run_routing(requests)
        self.assertEqual(indexed, baseline)
        s = sb.summarise_routing_build(indexed)
        self.assertEqual(s["requests_total"], 20000)
        self.assertEqual(s["requests_routed"], 16000)
        self.assertEqual(s["requests_unrouted"], 4000)
        self.assertEqual(s["per_endpoint"], {
            "ep-0007-epsilon-vision": 4000,
            "ep-0014-alpha-embed": 4000,
            "ep-0028-zeta-code": 4000,
            "ep-0063-delta-chat": 4000,
        })


if __name__ == "__main__":
    unittest.main()
