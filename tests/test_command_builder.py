import unittest
import tkinter as tk
from llama_gui.parser import Param, ParamGroup
from llama_gui.command_builder import build_command

class TestCommandBuilder(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.groups = [
            ParamGroup(name="group1", params=[
                Param(long_name="threads", short_flags=["t"], description="desc", param_type="int", default="8", choices=None, has_value=True, is_no_variant=False),
                Param(long_name="model", short_flags=["m"], description="desc", param_type="string", default="llama", choices=None, has_value=True, is_no_variant=False),
                Param(long_name="cpu-strict", short_flags=["cpu-strict"], description="desc", param_type="bool", default=False, choices=None, has_value=False, is_no_variant=False),
                Param(long_name="no-cpu-strict", short_flags=["no-cpu-strict"], description="desc", param_type="bool", default=False, choices=None, has_value=False, is_no_variant=True),
            ])
        ]

    def tearDown(self):
        self.root.destroy()

    def test_build_command_basic(self):
        vars_dict = {
            "threads": tk.IntVar(value=8),
            "model": tk.StringVar(value="llama"),
            "cpu-strict": tk.BooleanVar(value=False)
        }
        # Since defaults are used, it should just be llama-server
        # But wait, if everything is default, is it just "llama-server"?
        # My implementation: command_parts = ["llama-server"]
        # If no non-defaults are found, result is "llama-server"
        cmd = build_command(vars_dict, self.groups)
        self.assertEqual(cmd, "llama-server")

    def test_build_command_with_values(self):
        vars_dict = {
            "threads": tk.IntVar(value=16),
            "model": tk.StringVar(value="mistral"),
            "cpu-strict": tk.BooleanVar(value=True)
        }
        cmd = build_command(vars_dict, self.groups)
        # Expecting: llama-server -t 16 -m mistral -cpu-strict
        self.assertIn("-t 16", cmd)
        self.assertIn("-m mistral", cmd)
        self.assertIn("-cpu-strict", cmd)

    def test_build_command_bool_negation(self):
        # If cpu-strict is False, and no-cpu-strict exists.
        # My implementation for bool (with negation) was a bit limited.
        # Let's see what it does.
        vars_dict = {
            "cpu-strict": tk.BooleanVar(value=False),
        }
        cmd = build_command(vars_dict, self.groups)
        # Since it's False, it should be skipped if it's the default.
        # My parser handles negation by removing the no- variant.
        # So build_command only sees the positive one.
        # If positive is False, it skips.
        self.assertEqual(cmd, "llama-server")

if __name__ == "__main__":
    unittest.main()
