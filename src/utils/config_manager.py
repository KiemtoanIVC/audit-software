import json
from pathlib import Path

class ConfigManager:
    CONFIG_FILE = Path.home() / ".audit_software" / "config.json"

    @classmethod
    def save_last_job(cls, job_path: str):
        """Lưu đường dẫn của job cuối cùng"""
        cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        config = cls.load_config()
        config['last_job_path'] = job_path
        
        with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    @classmethod
    def get_last_job_path(cls) -> str:
        """Lấy đường dẫn của job cuối cùng"""
        config = cls.load_config()
        return config.get('last_job_path')

    @classmethod
    def load_config(cls) -> dict:
        """Load config từ file"""
        if cls.CONFIG_FILE.exists():
            with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {} 