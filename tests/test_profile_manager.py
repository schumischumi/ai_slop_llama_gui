import unittest
import tempfile
import shutil
from pathlib import Path
from llama_gui.profile_manager import ProfileManager

class TestProfileManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.manager = ProfileManager(profiles_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_and_load(self):
        name = "test_profile"
        params = {"param1": "value1", "param2": 123, "param3": True}
        self.manager.save(name, params)
        
        loaded_params = self.manager.load(name)
        self.assertEqual(loaded_params, params)

    def test_list_profiles(self):
        self.manager.save("p1", {"a": 1})
        self.manager.save("p2", {"b": 2})
        self.manager.save("p3", {"c": 3})
        
        profiles = self.manager.list_profiles()
        self.assertEqual(profiles, ["p1", "p2", "p3"])

    def test_delete_profile(self):
        name = "to_delete"
        self.manager.save(name, {"a": 1})
        
        # Verify it exists
        self.assertTrue((self.test_dir / f"{name}.yaml").exists())
        
        # Delete it
        result = self.manager.delete(name)
        self.assertTrue(result)
        self.assertFalse((self.test_dir / f"{name}.yaml").exists())
        
        # Delete non-existent
        result_non_existent = self.manager.delete("non_existent")
        self.assertFalse(result_non_existent)

    def test_load_non_existent(self):
        with self.assertRaises(FileNotFoundError):
            self.manager.load("missing")

if __name__ == "__main__":
    unittest.main()
