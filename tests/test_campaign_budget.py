"""Testes do orçamento agregado da campanha (F02-T04)."""

from __future__ import annotations

import hashlib
import json
import math

import pytest

from evobyte.campaign import (
    CampaignError,
    CampaignManifest,
    open_campaign,
)
from evobyte.candidate import canonical_json_bytes


def freeze_manifest(manifest):
    payload = {
        key: value
        for key, value in manifest.items()
        if key != "frozen_manifest_sha256"
    }
    digest = hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    frozen = dict(payload)
    frozen["frozen_manifest_sha256"] = digest
    return frozen


def entry(run_id, *, stage="development", wall_limit_s=600, max_attempts=1):
    return {
        "run_id": run_id,
        "stage": stage,
        "wall_limit_s": wall_limit_s,
        "max_attempts": max_attempts,
    }


def make_manifest(
    schedule,
    *,
    quotas=None,
    reserved_wall_s=None,
    planned_max=None,
    campaign_id="campaign-test",
    status="FROZEN",
    absolute_cap=300000,
):
    if reserved_wall_s is None:
        reserved_wall_s = sum(
            item["wall_limit_s"] * item.get("max_attempts", 1)
            for item in schedule
        )
    if quotas is None:
        quotas = {}
        for item in schedule:
            stage = item["stage"]
            quotas[stage] = quotas.get(stage, 0.0) + (
                item["wall_limit_s"] * item.get("max_attempts", 1)
            )
    if planned_max is None:
        planned_max = sum(item.get("max_attempts", 1) for item in schedule)
    manifest = {
        "schema_version": 1,
        "campaign_id": campaign_id,
        "status": status,
        "protocol_version": "P0-development-v1",
        "protocol_sha256": "b" * 64,
        "absolute_wall_cap_s": absolute_cap,
        "reserved_wall_s": reserved_wall_s,
        "planned_max_experimental_launches": planned_max,
        "quotas_s": quotas,
        "schedule": schedule,
        "frozen_manifest_sha256": None,
    }
    return freeze_manifest(manifest)


def open_test_campaign(tmp_path, manifest):
    return open_campaign(manifest, tmp_path / "ledger.json")


def test_manifest_hash_is_stable_under_key_order():
    first = make_manifest([entry("run-1")])
    reversed_payload = dict(reversed(list(first.items())))
    second = freeze_manifest(reversed_payload)

    first_validated = CampaignManifest.from_mapping(first)
    second_validated = CampaignManifest.from_mapping(second)

    assert first_validated.sha256 == second_validated.sha256
    assert first_validated.schedule["run-1"].wall_limit_s == 600.0


def test_reserve_persists_before_spawn(tmp_path):
    manifest = make_manifest([entry("run-1")])

    with open_test_campaign(tmp_path, manifest) as controller:
        reservation = controller.reserve("run-1")

        assert reservation.reservation_id == "run-1#1"
        assert reservation.wall_limit_s == 600.0
        ledger = json.loads((tmp_path / "ledger.json").read_bytes())
        assert ledger["reserved_seconds"] == 600.0
        assert ledger["launches"] == 1
        assert ledger["reservations"]["run-1#1"]["run_id"] == "run-1"

        snapshot = controller.snapshot()
        assert snapshot["global"]["reserved_seconds"] == 600.0
        assert snapshot["global"]["consumed_seconds"] == 0.0
        assert snapshot["global"]["available_seconds"] == 0.0
        assert len(snapshot["open_reservations"]) == 1


def test_reconcile_replaces_reservation_with_actual_consumption(tmp_path):
    manifest = make_manifest([entry("run-1")])

    with open_test_campaign(tmp_path, manifest) as controller:
        reservation = controller.reserve("run-1")
        reconciliation = controller.reconcile(
            reservation.reservation_id,
            500.0,
            "completed",
        )

        assert reconciliation.actual_seconds == 500.0
        assert reconciliation.overrun_seconds == 0.0
        assert reconciliation.consumed_seconds_total == 500.0
        assert reconciliation.reserved_seconds_total == 0.0
        assert controller.open_reservations() == ()

        snapshot = controller.snapshot()
        assert snapshot["global"]["consumed_seconds"] == 500.0
        assert snapshot["global"]["reserved_seconds"] == 0.0
        assert snapshot["global"]["available_seconds"] == 100.0
        assert snapshot["runs"]["run-1"]["last_status"] == "completed"
        assert len(snapshot["history"]) == 1


def test_failed_run_cost_is_not_refunded(tmp_path):
    manifest = make_manifest(
        [entry("run-1"), entry("run-2", wall_limit_s=500)],
        quotas={"development": 1100},
        reserved_wall_s=1100,
        planned_max=2,
    )

    with open_test_campaign(tmp_path, manifest) as controller:
        reservation = controller.reserve("run-1")
        controller.reconcile(reservation.reservation_id, 100.0, "crashed")

        snapshot = controller.snapshot()
        assert snapshot["global"]["consumed_seconds"] == 100.0
        assert snapshot["global"]["reserved_seconds"] == 0.0

        second = controller.reserve("run-2")
        assert second.wall_limit_s == 500.0


def test_stage_quota_is_enforced(tmp_path):
    manifest = make_manifest(
        [entry("run-1"), entry("run-2")],
        quotas={"development": 600},
        reserved_wall_s=1200,
        planned_max=2,
    )

    with open_test_campaign(tmp_path, manifest) as controller:
        controller.reserve("run-1")

        with pytest.raises(CampaignError) as exc:
            controller.reserve("run-2")

        assert exc.value.code == "STAGE_QUOTA_EXCEEDED"


def test_global_budget_with_599_remaining_refuses_600(tmp_path):
    manifest = make_manifest(
        [entry("run-1"), entry("run-2", stage="pilot")],
        quotas={"development": 600, "pilot": 600},
        reserved_wall_s=1200,
        planned_max=2,
    )

    with open_test_campaign(tmp_path, manifest) as controller:
        reservation = controller.reserve("run-1")
        controller.reconcile(reservation.reservation_id, 601.0, "timeout")

        snapshot = controller.snapshot()
        assert snapshot["global"]["consumed_seconds"] == 601.0
        assert snapshot["global"]["available_seconds"] == 599.0

        with pytest.raises(CampaignError) as exc:
            controller.reserve("run-2")

        assert exc.value.code == "GLOBAL_BUDGET_EXCEEDED"


def test_max_attempts_is_enforced(tmp_path):
    manifest = make_manifest([entry("run-1", max_attempts=1)])

    with open_test_campaign(tmp_path, manifest) as controller:
        reservation = controller.reserve("run-1")
        controller.reconcile(reservation.reservation_id, 10.0, "crashed")

        with pytest.raises(CampaignError) as exc:
            controller.reserve("run-1")

        assert exc.value.code == "MAX_ATTEMPTS_EXCEEDED"


def test_double_reconciliation_is_rejected(tmp_path):
    manifest = make_manifest([entry("run-1")])

    with open_test_campaign(tmp_path, manifest) as controller:
        reservation = controller.reserve("run-1")
        controller.reconcile(reservation.reservation_id, 10.0, "completed")

        with pytest.raises(CampaignError) as exc:
            controller.reconcile(reservation.reservation_id, 10.0, "completed")

        assert exc.value.code == "RESERVATION_NOT_FOUND"


def test_overrun_is_recorded_and_completed_is_rejected(tmp_path):
    manifest = make_manifest([entry("run-1", max_attempts=2)])

    with open_test_campaign(tmp_path, manifest) as controller:
        reservation = controller.reserve("run-1")

        with pytest.raises(CampaignError) as exc:
            controller.reconcile(reservation.reservation_id, 601.0, "completed")
        assert exc.value.code == "INVALID_RECONCILIATION"
        assert len(controller.open_reservations()) == 1

        reconciliation = controller.reconcile(
            reservation.reservation_id,
            650.0,
            "timeout",
        )
        assert reconciliation.overrun_seconds == 50.0
        assert controller.snapshot()["global"]["overrun_seconds"] == 50.0

        with pytest.raises(CampaignError) as exc:
            controller.reserve("run-1")
        assert exc.value.code in {
            "STAGE_QUOTA_EXCEEDED",
            "GLOBAL_BUDGET_EXCEEDED",
        }


def test_snapshot_keeps_negative_availability_after_overrun(tmp_path):
    manifest = make_manifest([entry("run-1")])

    with open_test_campaign(tmp_path, manifest) as controller:
        reservation = controller.reserve("run-1")
        controller.reconcile(reservation.reservation_id, 700.0, "timeout")

        snapshot = controller.snapshot()
        assert snapshot["global"]["available_seconds"] == -100.0
        assert snapshot["stages"]["development"]["available_seconds"] == -100.0
        assert snapshot["global"]["overrun_seconds"] == 100.0


def test_reopen_preserves_reservation_and_consumption(tmp_path):
    manifest = make_manifest([entry("run-1")])
    ledger_path = tmp_path / "ledger.json"

    with open_campaign(manifest, ledger_path) as controller:
        controller.reserve("run-1")

    with open_campaign(manifest, ledger_path) as controller:
        snapshot = controller.snapshot()
        assert snapshot["global"]["consumed_seconds"] == 0.0
        assert snapshot["global"]["reserved_seconds"] == 600.0
        assert len(controller.open_reservations()) == 1

        reconciliation = controller.abandon("run-1#1")
        assert reconciliation.reason == "ABANDONED"
        assert reconciliation.actual_seconds == 600.0
        assert controller.snapshot()["global"]["consumed_seconds"] == 600.0

    with open_campaign(manifest, ledger_path) as controller:
        snapshot = controller.snapshot()
        assert snapshot["global"]["consumed_seconds"] == 600.0
        assert snapshot["global"]["reserved_seconds"] == 0.0
        assert controller.open_reservations() == ()


def test_reopen_allows_reconciliation_with_observed_cost(tmp_path):
    manifest = make_manifest([entry("run-1")])
    ledger_path = tmp_path / "ledger.json"

    with open_campaign(manifest, ledger_path) as controller:
        controller.reserve("run-1")

    with open_campaign(manifest, ledger_path) as controller:
        reconciliation = controller.reconcile("run-1#1", 120.0, "crashed")
        assert reconciliation.consumed_seconds_total == 120.0

    with open_campaign(manifest, ledger_path) as controller:
        assert controller.snapshot()["global"]["consumed_seconds"] == 120.0


def test_reopen_blocks_new_launch_until_reservation_is_reconciled(tmp_path):
    manifest = make_manifest(
        [entry("run-1"), entry("run-2")],
        quotas={"development": 600},
        reserved_wall_s=1200,
        planned_max=2,
    )
    ledger_path = tmp_path / "ledger.json"

    with open_campaign(manifest, ledger_path) as controller:
        controller.reserve("run-1")

    with open_campaign(manifest, ledger_path) as controller:
        with pytest.raises(CampaignError) as exc:
            controller.reserve("run-2")
        assert exc.value.code == "STAGE_QUOTA_EXCEEDED"

        controller.abandon("run-1#1")

        with pytest.raises(CampaignError) as exc:
            controller.reserve("run-2")
        assert exc.value.code == "STAGE_QUOTA_EXCEEDED"


def test_second_controller_is_blocked_by_lock(tmp_path):
    manifest = make_manifest([entry("run-1")])
    ledger_path = tmp_path / "ledger.json"

    controller = open_campaign(manifest, ledger_path)
    try:
        with pytest.raises(CampaignError) as exc:
            open_campaign(manifest, ledger_path)
        assert exc.value.code == "CAMPAIGN_LOCKED"
    finally:
        controller.close()

    with open_campaign(manifest, ledger_path) as controller:
        assert controller.snapshot()["campaign_id"] == "campaign-test"


def test_corrupted_ledger_is_preserved(tmp_path):
    manifest = make_manifest([entry("run-1")])
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_bytes(b"{ledger-corrompido")
    before = ledger_path.read_bytes()

    with pytest.raises(CampaignError) as exc:
        open_campaign(manifest, ledger_path)

    assert exc.value.code == "LEDGER_CORRUPTED"
    assert ledger_path.read_bytes() == before


def test_manifest_change_invalidates_existing_ledger(tmp_path):
    first_manifest = make_manifest([entry("run-1")])
    ledger_path = tmp_path / "ledger.json"

    with open_campaign(first_manifest, ledger_path):
        pass

    second_manifest = make_manifest(
        [entry("run-1"), entry("run-2")],
        planned_max=2,
    )

    with pytest.raises(CampaignError) as exc:
        open_campaign(second_manifest, ledger_path)

    assert exc.value.code == "LEDGER_MANIFEST_MISMATCH"


def test_tampered_ledger_totals_are_rejected(tmp_path):
    manifest = make_manifest([entry("run-1")])
    ledger_path = tmp_path / "ledger.json"

    with open_campaign(manifest, ledger_path) as controller:
        controller.reserve("run-1")

    ledger = json.loads(ledger_path.read_bytes())
    ledger["reserved_seconds"] = 0.0
    ledger_path.write_text(json.dumps(ledger), encoding="utf-8")

    with pytest.raises(CampaignError) as exc:
        open_campaign(manifest, ledger_path)

    assert exc.value.code == "LEDGER_CORRUPTED"


def test_ledger_write_failure_preserves_state(tmp_path, monkeypatch):
    manifest = make_manifest([entry("run-1")])
    ledger_path = tmp_path / "ledger.json"

    with open_campaign(manifest, ledger_path) as controller:
        before = ledger_path.read_bytes()

        def fail_write(path, payload):
            raise OSError("falha simulada")

        monkeypatch.setattr("evobyte.campaign._write_json_atomic", fail_write)

        with pytest.raises(CampaignError) as exc:
            controller.reserve("run-1")
        assert exc.value.code == "LEDGER_WRITE_FAILED"
        assert controller.open_reservations() == ()
        assert ledger_path.read_bytes() == before

        monkeypatch.undo()
        controller.reserve("run-1")
        assert len(controller.open_reservations()) == 1


def test_invalid_reservation_and_reconciliation_arguments(tmp_path):
    manifest = make_manifest([entry("run-1")])

    with open_test_campaign(tmp_path, manifest) as controller:
        with pytest.raises(CampaignError) as exc:
            controller.reserve("run-inexistente")
        assert exc.value.code == "RUN_NOT_IN_MANIFEST"

        reservation = controller.reserve("run-1")

        with pytest.raises(CampaignError) as exc:
            controller.reconcile(reservation.reservation_id, -1, "completed")
        assert exc.value.code == "INVALID_ACTUAL_SECONDS"

        with pytest.raises(CampaignError) as exc:
            controller.reconcile(reservation.reservation_id, math.nan, "completed")
        assert exc.value.code == "INVALID_ACTUAL_SECONDS"

        with pytest.raises(CampaignError) as exc:
            controller.reconcile(reservation.reservation_id, 10, "desconhecido")
        assert exc.value.code == "INVALID_STATUS"

        with pytest.raises(CampaignError) as exc:
            controller.reconcile("run-1#99", 10, "completed")
        assert exc.value.code == "RESERVATION_NOT_FOUND"


def test_closed_controller_rejects_operations(tmp_path):
    manifest = make_manifest([entry("run-1")])
    controller = open_test_campaign(tmp_path, manifest)
    controller.close()

    with pytest.raises(CampaignError) as exc:
        controller.reserve("run-1")
    assert exc.value.code == "CAMPAIGN_CLOSED"


INVALID_MANIFEST_CASES = [
    pytest.param(
        lambda: {**make_manifest([entry("run-1")]), "is_example": True},
        "EXAMPLE_NOT_ALLOWED",
        id="example",
    ),
    pytest.param(
        lambda: make_manifest([entry("run-1")], status="PLANNED"),
        "MANIFEST_NOT_FROZEN",
        id="not-frozen",
    ),
    pytest.param(
        lambda: {**make_manifest([entry("run-1")]), "reserved_wall_s": 1.0},
        "MANIFEST_HASH_MISMATCH",
        id="hash-mismatch",
    ),
    pytest.param(
        lambda: {
            key: value
            for key, value in make_manifest([entry("run-1")]).items()
            if key != "schedule"
        },
        "MISSING_FIELD",
        id="missing-field",
    ),
    pytest.param(
        lambda: make_manifest(
            [],
            quotas={"development": 1},
            reserved_wall_s=1,
            planned_max=1,
        ),
        "INVALID_SCHEDULE",
        id="empty-schedule",
    ),
    pytest.param(
        lambda: make_manifest([entry("run-1"), entry("run-1")]),
        "DUPLICATE_RUN_ID",
        id="duplicate-run",
    ),
    pytest.param(
        lambda: make_manifest(
            [entry("run-1", stage="etapa-inexistente")],
            quotas={"development": 600},
            reserved_wall_s=600,
            planned_max=1,
        ),
        "INVALID_RUN_STAGE",
        id="unknown-run-stage",
    ),
    pytest.param(
        lambda: make_manifest(
            [entry("run-1")],
            quotas={"pilot": 600},
        ),
        "UNKNOWN_STAGE_QUOTA",
        id="missing-stage-quota",
    ),
    pytest.param(
        lambda: make_manifest([entry("run-1", wall_limit_s=601)]),
        "INVALID_RUN_LIMIT",
        id="run-limit",
    ),
    pytest.param(
        lambda: make_manifest(
            [entry("run-1", max_attempts=0)],
            quotas={"development": 1},
            reserved_wall_s=1,
            planned_max=1,
        ),
        "INVALID_ATTEMPTS",
        id="attempts",
    ),
    pytest.param(
        lambda: make_manifest(
            [entry("run-1")],
            quotas={"development": 599},
            reserved_wall_s=599,
        ),
        "MANIFEST_OVERCOMMITTED",
        id="overcommitted",
    ),
    pytest.param(
        lambda: make_manifest([entry("run-1")], absolute_cap=300001),
        "MANIFEST_CAP_EXCEEDED",
        id="cap",
    ),
    pytest.param(
        lambda: make_manifest([entry("run-1")], planned_max=517),
        "INVALID_LAUNCH_CAP",
        id="launch-cap",
    ),
    pytest.param(
        lambda: make_manifest([entry("run-1", max_attempts=2)], planned_max=1),
        "MANIFEST_LAUNCH_OVERCOMMITTED",
        id="launch-overcommitted",
    ),
    pytest.param(
        lambda: make_manifest(
            [entry("run-1")],
            quotas={"development": 1200},
            reserved_wall_s=600,
        ),
        "INVALID_QUOTAS",
        id="quota-sum",
    ),
    pytest.param(
        lambda: make_manifest(
            [entry("run-1")],
            quotas={"development": 600, "etapa-inexistente": 1},
        ),
        "UNKNOWN_STAGE",
        id="unknown-quota-stage",
    ),
    pytest.param(
        lambda: make_manifest([entry("run-1")], absolute_cap=0),
        "INVALID_CAP",
        id="invalid-cap",
    ),
    pytest.param(
        lambda: make_manifest([entry("run-1")], reserved_wall_s=300001),
        "INVALID_RESERVED_TOTAL",
        id="reserved-over-cap",
    ),
    pytest.param(
        lambda: "nao-e-dict",
        "MANIFEST_NOT_MAPPING",
        id="not-mapping",
    ),
]


@pytest.mark.parametrize("builder, expected_code", INVALID_MANIFEST_CASES)
def test_invalid_manifest_is_rejected(builder, expected_code):
    with pytest.raises(CampaignError) as exc:
        CampaignManifest.from_mapping(builder())

    assert exc.value.code == expected_code
