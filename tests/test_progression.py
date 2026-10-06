import json
import unittest
from prototype.progression import CONTENT, MISSIONS, State, active_mission, apply_event, dumps, loads

BEFORE_CORE = ("site_discovered", "sample_experiment_completed", "tuning_lens_crafted", "site_restored")


def advance(events, state=None):
    state = State() if state is None else state
    for event in events:
        state = apply_event(state, event)
    return state


class ProgressionTests(unittest.TestCase):
    def test_fresh_save(self):
        self.assertEqual(active_mission(State()), "discover")

    def test_before_core_stops_at_awaken(self):
        state = advance(BEFORE_CORE)
        self.assertEqual(state.completed, MISSIONS[:4])
        self.assertEqual(active_mission(state), "awaken")

    def test_core_then_retune_completes(self):
        state = advance(BEFORE_CORE + ("core_awakened_observed", "site_retuned"))
        self.assertEqual(state.completed, MISSIONS)
        self.assertIsNone(active_mission(state))

    def test_already_awakened_save_does_not_skip_experiments(self):
        state = advance(("core_awakened_observed",))
        self.assertEqual(active_mission(state), "discover")
        state = advance(BEFORE_CORE, state)
        self.assertEqual(active_mission(state), "retune")

    def test_core_at_every_intermediate_step(self):
        for i in range(len(BEFORE_CORE) + 1):
            with self.subTest(core_after_actions=i):
                state = advance(BEFORE_CORE[:i] + ("core_awakened_observed",) + BEFORE_CORE[i:])
                self.assertEqual(state.completed, MISSIONS[:5])

    def test_duplicate_actions_are_idempotent(self):
        state = State()
        for event in BEFORE_CORE + ("core_awakened_observed", "site_retuned"):
            state = apply_event(state, event)
            self.assertEqual(apply_event(state, event), state)

    def test_out_of_order_actions_do_not_unlock(self):
        for event in BEFORE_CORE[1:] + ("site_retuned",):
            self.assertEqual(apply_event(State(), event), State())

    def test_retune_cannot_precede_core(self):
        state = advance(BEFORE_CORE)
        self.assertEqual(apply_event(state, "site_retuned"), state)

    def test_save_reload_at_every_step(self):
        state = State()
        self.assertEqual(loads(dumps(state)), state)
        for event in BEFORE_CORE + ("core_awakened_observed", "site_retuned"):
            state = apply_event(state, event)
            self.assertEqual(loads(dumps(state)), state)

    def test_reload_reconciles_core_latch(self):
        state = State(MISSIONS[:4], True)
        self.assertEqual(loads(dumps(state)).completed, MISSIONS[:5])

    def test_unknown_event_is_rejected(self):
        with self.assertRaises(ValueError):
            apply_event(State(), "invented_game_callback")

    def test_invalid_persistence_fails_closed(self):
        invalid = [
            {"schema_version": 2, "completed": [], "core_awakened": False},
            {"schema_version": True, "completed": [], "core_awakened": False},
            {"schema_version": 1, "completed": ["retune"], "core_awakened": True},
            {"schema_version": 1, "completed": list(MISSIONS), "core_awakened": False},
            {"schema_version": 1, "completed": [], "core_awakened": "false"},
            {"schema_version": 1, "completed": [], "core_awakened": False, "extra": 1},
            {"schema_version": 1, "completed": "discover", "core_awakened": False},
            [],
        ]
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                loads(json.dumps(payload))

    def test_definition_mission_chain_is_consistent(self):
        self.assertEqual(len(MISSIONS), len(set(MISSIONS)))
        for index, mission in enumerate(CONTENT["missions"]):
            self.assertEqual(mission["requires"], [] if index == 0 else [MISSIONS[index-1]])
        self.assertEqual(CONTENT["missions"][4]["condition"], "sylva_core_awakened")

    def test_sampling_does_not_depend_on_its_own_crafted_lens(self):
        sampling = CONTENT["sampling"]
        self.assertTrue(sampling["repeatable"])
        self.assertFalse(sampling["requires_lens"])
        self.assertFalse(sampling["requires_core_awakened"])
        self.assertTrue(sampling["available_after_core_awakened"])
        self.assertEqual(sampling["cost"], "no_resource_inputs_initial_slice")

    def test_resource_recipe_references(self):
        known = {"quartz"} | {r["id"] for r in CONTENT["resources"]}
        for item in CONTENT["resources"] + CONTENT["equipment"]:
            for entry in item.get("recipe", {}).get("inputs", []):
                self.assertIn(entry["resource"], known)
                self.assertGreater(entry["amount"], 0)


if __name__ == "__main__":
    unittest.main()
