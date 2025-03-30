import json
from pathlib import Path
from datetime import datetime

class ConfigManager:
    CONFIG_FILE = Path.home() / ".audit_app_config.json"

    @classmethod
    def save_last_job(cls, job_path: str):
        """Lưu đường dẫn job cuối cùng"""
        config = cls._load_config()
        config['last_job_path'] = job_path
        config['last_accessed'] = str(datetime.now())
        cls._save_config(config)

    @classmethod
    def get_last_job_path(cls) -> str:
        """Lấy đường dẫn job cuối cùng"""
        config = cls._load_config()
        return config.get('last_job_path')

    @classmethod
    def _load_config(cls) -> dict:
        """Load config từ file"""
        try:
            if cls.CONFIG_FILE.exists():
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Lỗi khi đọc config: {str(e)}")
        return {}

    @classmethod
    def _save_config(cls, config: dict):
        """Lưu config vào file"""
        try:
            # Đảm bảo thư mục cha tồn tại
            cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi khi lưu config: {str(e)}")

    @classmethod
    def load_config(cls) -> dict:
        """Load config từ file"""
        if cls.CONFIG_FILE.exists():
            with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {} 