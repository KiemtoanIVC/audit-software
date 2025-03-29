from pathlib import Path
from datetime import datetime
from ..models.job import Job
from ..utils.file_utils import FileUtils
import json

class JobController:
    def __init__(self):
        self.base_path = FileUtils.get_base_path()
        
    def create_job(self, job_data: dict) -> Job:
        """Tạo job mới"""
        job = Job()
        job.client_name = job_data.get('client_name')
        job.contract_number = job_data.get('contract_number')
        job.contract_date = job_data.get('contract_date')
        job.audit_period = job_data.get('audit_period')
        job.industry = job_data.get('industry')
        
        # Tạo cấu trúc thư mục
        job.create_job_structure(self.base_path)
        job.save_metadata()
        
        return job
        
    def open_job(self, job_path: str) -> Job:
        """Mở job đã tồn tại"""
        path = Path(job_path)
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy job tại {job_path}")
            
        metadata_file = path / "metadata.json"
        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            
        job = Job()
        job.job_path = path
        job.client_name = metadata.get("client_name")
        # ... load các thông tin khác
        
        return job
