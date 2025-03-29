from pathlib import Path

class FileUtils:
    @staticmethod
    def get_base_path() -> Path:
        """Lấy đường dẫn gốc cho các job"""
        # Có thể lấy từ config hoặc environment variable
        return Path.home() / "AuditJobs"
        
    @staticmethod
    def ensure_dir(path: Path):
        """Đảm bảo thư mục tồn tại"""
        path.mkdir(parents=True, exist_ok=True) 