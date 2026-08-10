import unittest

from llama_gui.command_parser import parse_command
from llama_gui.parser import Param, ParamGroup


class TestCommandParser(unittest.TestCase):
    def setUp(self):
        self.groups = [
            ParamGroup(name="group1", params=[
                Param(long_name="threads", short_flags=["t"], description="desc", param_type="int", default="8", choices=None, has_value=True, is_no_variant=False),
                Param(long_name="model", short_flags=["m"], description="desc", param_type="string", default="llama", choices=None, has_value=True, is_no_variant=False),
                Param(long_name="cpu-strict", short_flags=["cpu-strict"], description="desc", param_type="bool", default=False, choices=None, has_value=False, is_no_variant=False),
            ])
        ]

    def test_parse_command_basic(self):
        cmd = "llama-server -t 16 --model mistral"
        parsed = parse_command(cmd, self.groups)
        self.assertEqual(parsed.get("threads"), 16)
        self.assertEqual(parsed.get("model"), "mistral")

    def test_parse_command_short_flags(self):
        cmd = "llama-server -t 16 -m mistral"
        parsed = parse_command(cmd, self.groups)
        self.assertEqual(parsed.get("threads"), 16)
        self.assertEqual(parsed.get("model"), "mistral")

    def test_parse_command_bool_flag(self):
        cmd = "llama-server --cpu-strict"
        parsed = parse_command(cmd, self.groups)
        self.assertTrue(parsed.get("cpu-strict"))

if __name__ == "__main__":
    unittest.main()
