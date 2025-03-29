from datetime import datetime
from pathlib import Path
import json

class Job:
    def __init__(self):
        self.client_name = ""
        self.contract_number = ""
        self.contract_date = None
        self.audit_period = ""
        self.industry = ""
        self.job_path = None
        self.status = "new"  # new, in_progress, review, completed
        
    def create_job_structure(self, base_path: Path):
        """Tạo cấu trúc thư mục cho job mới"""
        year = datetime.now().year
        self.job_path = base_path / str(year) / self.client_name
        
        # Tạo các thư mục con
        folders = ["MauBieu", "DuLieu", "BangChung"]
        for folder in folders:
            (self.job_path / folder).mkdir(parents=True, exist_ok=True)
            
    def save_metadata(self):
        """Lưu thông tin metadata của job"""
        metadata = {
            "client_name": self.client_name,
            "contract_number": self.contract_number,
            "contract_date": self.contract_date.isoformat() if self.contract_date else None,
            "audit_period": self.audit_period,
            "industry": self.industry,
            "status": self.status,
            "created_at": datetime.now().isoformat()
        }
        
        metadata_file = self.job_path / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2) 