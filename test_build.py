"""公开看板构建契约的纯 stdlib 回归测试。"""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from build import validate_inputs

ROOT = Path(__file__).parent


class BuildContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((ROOT / "dashboard_data.json").read_text(encoding="utf-8"))
        self.strategy = json.loads((ROOT / "strategy_data.json").read_text(encoding="utf-8"))
        self.forward = json.loads((ROOT / "forward_status.json").read_text(encoding="utf-8"))
        self.long_horizon = json.loads(
            (ROOT / "long_horizon_data.json").read_text(encoding="utf-8")
        )
        self.template = (ROOT / "template.html").read_text(encoding="utf-8")

    def test_current_inputs_are_consistent(self) -> None:
        validate_inputs(
            self.data, self.strategy, self.forward, self.long_horizon, self.template
        )

    def test_rejects_forward_count_beyond_gate(self) -> None:
        forward = copy.deepcopy(self.forward)
        forward["forward_n"] = 31
        forward["target_n"] = 30

        with self.assertRaisesRegex(ValueError, "前瞻样本进度不合法"):
            validate_inputs(
                self.data, self.strategy, forward, self.long_horizon, self.template
            )

    def test_rejects_factor_date_mismatch(self) -> None:
        forward = copy.deepcopy(self.forward)
        forward["asset_dates"]["factor_research"] = "2026-07-13"

        with self.assertRaisesRegex(ValueError, "factor_research"):
            validate_inputs(
                self.data, self.strategy, forward, self.long_horizon, self.template
            )

    def test_rejects_missing_placeholder(self) -> None:
        template = self.template.replace("__FORWARD_STATUS__", "{}")

        with self.assertRaisesRegex(ValueError, "__FORWARD_STATUS__"):
            validate_inputs(
                self.data, self.strategy, self.forward, self.long_horizon, template
            )

    def test_rejects_long_horizon_production_promotion(self) -> None:
        long_horizon = copy.deepcopy(self.long_horizon)
        long_horizon["long_factor_pool"]["production_change"] = True

        with self.assertRaisesRegex(ValueError, "生产 Gate"):
            validate_inputs(
                self.data, self.strategy, self.forward, long_horizon, self.template
            )

    def test_rejects_backfill_database_write(self) -> None:
        long_horizon = copy.deepcopy(self.long_horizon)
        long_horizon["evidence_backfill"]["database_writes"] = True

        with self.assertRaisesRegex(ValueError, "dry-run"):
            validate_inputs(
                self.data, self.strategy, self.forward, long_horizon, self.template
            )

    def test_long_horizon_snapshot_exposes_verified_and_missing_states(self) -> None:
        assert self.long_horizon["schema_version"] == 3
        assert self.long_horizon["scope"]["rows"] == 281
        assert self.long_horizon["scope"]["registered_indicators"] == 100
        factors = {
            row["id"]: row
            for row in self.long_horizon["long_factor_pool"]["display_factors"]
        }
        assert factors["cornerstone_production_score"]["d180_post_d1_excess"][
            "bh_fdr_10pct"
        ]
        assert factors["cornerstone_pct_of_offer"]["d180_post_d1_excess"][
            "bh_fdr_10pct"
        ]
        assert factors["debt_asset_ratio"]["decision"] == "retain_priority"
        assert factors["debt_asset_ratio"]["d365_post_d1_excess"][
            "bh_fdr_10pct"
        ]
        assert self.long_horizon["evidence_backfill"]["summary"]["planned_updates"] == 0
        assert all(
            value == 0
            for value in self.long_horizon["evidence_backfill"]["existing_coverage"].values()
        )
        pilot = self.long_horizon["evidence_backfill"]["pilot"]["summary"]
        collection = self.long_horizon["evidence_backfill"]["collection"]
        assert collection["windowed"] == 69
        assert collection["nonempty_page_evidence"] == 69
        assert collection["manual_reviews_completed"] == 5
        assert collection["queued_for_manual_review"] == 64
        assert collection["factor_values_generated_automatically"] == 0
        assert pilot["research_factor_ready_values"] == 16
        assert pilot["public_float_denominators_ready"] == 5
        assert pilot["lockup_public_float_factor_ready"] == 4
        assert pilot["secondary_sell_down_ready"] == 5
        assert pilot["unlock_supply_shock_factor_ready"] == 0


if __name__ == "__main__":
    unittest.main()
