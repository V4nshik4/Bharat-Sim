import unittest

from backend.app.main import PERSONAS
from worker.condition_planner import ConditionPlan, is_emulator_serial, plan_conditions


class ConditionPlannerTests(unittest.TestCase):
    def test_budget_android_planning_classifications(self):
        profile = PERSONAS["budget-android"]
        plan = plan_conditions(profile, "emulator-5554")
        self.assertTrue(plan.is_emulator)
        self.assertEqual(plan.persona_id, "budget-android")

        lat = plan.get_condition("network_latency")
        self.assertIsNotNone(lat)
        self.assertTrue(lat.requested)
        self.assertEqual(lat.classification, "supported")
        self.assertEqual(lat.target_value, 180)

        down = plan.get_condition("download_bandwidth")
        self.assertIsNotNone(down)
        self.assertTrue(down.requested)
        self.assertEqual(down.classification, "supported")
        self.assertEqual(down.target_value, 1200)

        up = plan.get_condition("upload_bandwidth")
        self.assertIsNotNone(up)
        self.assertTrue(up.requested)
        self.assertEqual(up.classification, "control_plane_verifiable")
        self.assertEqual(up.target_value, 350)

        loss = plan.get_condition("packet_loss")
        self.assertIsNotNone(loss)
        self.assertTrue(loss.requested)
        self.assertEqual(loss.classification, "unsupported")
        self.assertEqual(loss.target_value, 2.0)
        self.assertIn("does not support packet loss", loss.reason)

        bat = plan.get_condition("battery_saver")
        self.assertIsNotNone(bat)
        self.assertTrue(bat.requested)
        self.assertEqual(bat.classification, "supported")

        stor = plan.get_condition("storage_pressure")
        self.assertIsNotNone(stor)
        self.assertTrue(stor.requested)
        self.assertEqual(stor.classification, "supported")
        self.assertEqual(stor.target_value, 600)

        ram = plan.get_condition("ram_constraint")
        self.assertIsNotNone(ram)
        self.assertTrue(ram.requested)
        self.assertEqual(ram.classification, "report_only")
        self.assertIn("Dynamic RAM restriction is not supported", ram.reason)

        cpu = plan.get_condition("cpu_constraint")
        self.assertIsNotNone(cpu)
        self.assertFalse(cpu.requested)
        self.assertEqual(cpu.classification, "unsupported")

    def test_edge_village_packet_loss_marked_unsupported(self):
        profile = PERSONAS["edge-village"]
        plan = plan_conditions(profile, "emulator-5556")
        loss = plan.get_condition("packet_loss")
        self.assertIsNotNone(loss)
        self.assertTrue(loss.requested)
        self.assertEqual(loss.target_value, 8.0)
        self.assertEqual(loss.classification, "unsupported")
        self.assertIn("does not support packet loss", loss.reason)

    def test_baseline_planning(self):
        profile = PERSONAS["baseline"]
        plan = plan_conditions(profile, "emulator-5554")
        self.assertEqual(plan.persona_id, "baseline")

        loss = plan.get_condition("packet_loss")
        self.assertIsNotNone(loss)
        self.assertFalse(loss.requested)
        self.assertEqual(loss.classification, "not_requested")

        bat = plan.get_condition("battery_saver")
        self.assertIsNotNone(bat)
        self.assertFalse(bat.requested)
        self.assertEqual(bat.classification, "not_requested")

        stor = plan.get_condition("storage_pressure")
        self.assertIsNotNone(stor)
        self.assertTrue(stor.requested)
        self.assertEqual(stor.target_value, 8000)

    def test_physical_device_rejects_emulator_only_controls(self):
        profile = PERSONAS["budget-android"]
        plan = plan_conditions(profile, "R58M123ABC")
        self.assertFalse(plan.is_emulator)
        self.assertEqual(plan.target_serial, "R58M123ABC")

        for name in ("network_latency", "download_bandwidth", "upload_bandwidth", "battery_saver", "storage_pressure"):
            with self.subTest(condition=name):
                c = plan.get_condition(name)
                self.assertIsNotNone(c)
                self.assertEqual(c.classification, "unsupported")
                self.assertIn("not an Android Emulator", c.reason)

    def test_ram_and_cpu_are_never_faked_as_throttled(self):
        profile = {"id": "custom", "ram_mb": 1024}
        plan = plan_conditions(profile, "emulator-5554")

        ram = plan.get_condition("ram_constraint")
        self.assertEqual(ram.classification, "report_only")
        self.assertFalse(ram.classification == "supported")

        cpu = plan.get_condition("cpu_constraint")
        self.assertEqual(cpu.classification, "unsupported")
        self.assertFalse(cpu.classification == "supported")

    def test_empty_or_none_profile_returns_safe_plan(self):
        for empty in (None, {}):
            with self.subTest(profile=empty):
                plan = plan_conditions(empty, "emulator-5554")
                self.assertEqual(plan.persona_id, "unknown")
                self.assertTrue(plan.is_emulator)
                plan_dict = plan.to_dict()
                self.assertIsInstance(plan_dict["conditions"], list)
                self.assertEqual(len(plan_dict["conditions"]), 8)

    def test_is_emulator_serial(self):
        self.assertTrue(is_emulator_serial("emulator-5554"))
        self.assertTrue(is_emulator_serial("emulator-5556"))
        self.assertTrue(is_emulator_serial("  emulator-5584  "))
        self.assertFalse(is_emulator_serial("device-1234"))
        self.assertFalse(is_emulator_serial("R58M123ABC"))
        self.assertFalse(is_emulator_serial("localhost:5555"))
        self.assertFalse(is_emulator_serial(""))


if __name__ == "__main__":
    unittest.main()
