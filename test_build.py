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
        self.template = (ROOT / "template.html").read_text(encoding="utf-8")

    def test_current_inputs_are_consistent(self) -> None:
        validate_inputs(self.data, self.strategy, self.forward, self.template)

    def test_rejects_forward_count_beyond_gate(self) -> None:
        forward = copy.deepcopy(self.forward)
        forward["forward_n"] = 31
        forward["target_n"] = 30

        with self.assertRaisesRegex(ValueError, "前瞻样本进度不合法"):
            validate_inputs(self.data, self.strategy, forward, self.template)

    def test_rejects_factor_date_mismatch(self) -> None:
        forward = copy.deepcopy(self.forward)
        forward["asset_dates"]["factor_research"] = "2026-07-13"

        with self.assertRaisesRegex(ValueError, "factor_research"):
            validate_inputs(self.data, self.strategy, forward, self.template)

    def test_rejects_missing_placeholder(self) -> None:
        template = self.template.replace("__FORWARD_STATUS__", "{}")

        with self.assertRaisesRegex(ValueError, "__FORWARD_STATUS__"):
            validate_inputs(self.data, self.strategy, self.forward, template)


if __name__ == "__main__":
    unittest.main()
