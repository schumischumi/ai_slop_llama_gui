import yaml
from pathlib import Path
from datetime import datetime

class ProfileManager:
    def __init__(self, profiles_dir: Path | None = None):
        if profiles_dir:
            self.profiles_dir = Path(profiles_dir)
        else:
            self.profiles_dir = Path.home() / ".config" / "llama-gui" / "profiles"
        
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def save(self, name: str, params: dict[str, str | int | bool]) -> Path:
        """Save profile. Returns path to saved file.
        Creates profiles_dir if missing.
        Overwrites existing profile with same name.
        """
        file_path = self.profiles_dir / f"{name}.yaml"
        data = {
            "name": name,
            "created": datetime.now().isoformat(),
            "params": params
        }
        with open(file_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
        return file_path

    def load(self, name: str) -> dict[str, str | int | bool]:
        """Load profile. Returns params dict.
        Raises FileNotFoundError if not found.
        """
        file_path = self.profiles_dir / f"{name}.yaml"
        if not file_path.exists():
            raise FileNotFoundError(f"Profile '{name}' not found at {file_path}")
        
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        
        return data["params"]

    def list_profiles(self) -> list[str]:
        """List profile names (without .yaml extension).
        Returns sorted list.
        """
        profiles = []
        for file in self.profiles_dir.glob("*.yaml"):
            profiles.append(file.stem)
        return sorted(profiles)

    def delete(self, name: str) -> bool:
        """Delete profile. Returns True if deleted, False if not found."""
        file_path = self.profiles_dir / f"{name}.yaml"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
