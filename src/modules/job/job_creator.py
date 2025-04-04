import os
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any

class JobStatus:
    PLANNING = "PLANNING"
    EXECUTION = "EXECUTION"
    REPORTING = "REPORTING"
    COMPLETED = "COMPLETED"

class JobCreator:
    def __init__(self):
        """
        Khởi tạo JobCreator không cần base_path mặc định nữa
        """
        pass

    def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tạo job mới
        Args:
            job_data: Dictionary chứa thông tin job
        Returns:
            Dictionary chứa thông tin job đã tạo
        """
        try:
            # Validate dữ liệu đầu vào
            self._validate_job_data(job_data)
            
            # Lấy base_path từ job_data
            base_path = Path(job_data.pop('base_path'))
            
            # Tạo cấu trúc thư mục
            job_path = self._create_job_folder_structure(base_path, job_data)

            # Tạo metadata cho job
            job = {
                **job_data,
                "id": self._generate_job_id(),
                "status": JobStatus.PLANNING,
                "path": str(job_path),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # Lưu metadata
            self._save_job_metadata(job_path, job)

            return job
            
        except Exception as e:
            raise Exception(f"Lỗi khi tạo job: {str(e)}")

    def _validate_job_data(self, job_data: Dict[str, Any]) -> None:
        """Kiểm tra dữ liệu đầu vào"""
        required_fields = ["client_name", "contract_number"]
        for field in required_fields:
            if not job_data.get(field):
                raise ValueError(f"Thiếu thông tin: {field}")

    def _create_job_folder_structure(self, base_path: Path, job_data: Dict[str, Any]) -> Path:
        """
        Tạo cấu trúc thư mục cho job
        Sử dụng số hợp đồng làm tên thư mục
        """
        # Tạo đường dẫn job theo số hợp đồng
        contract_number = job_data["contract_number"]
        job_path = base_path / contract_number
        
        # Tạo các thư mục con
        folders = [
            "1. Hop dong, thanh ly",
            "2. Danh gia rui ro",
            "3. Xu ly rui ro",
            "4. Tong hop, ket luan",
            "5. Du lieu kiem toan lan 1",
            "6. Bao cao phat hanh"
        ]
        
        for folder in folders:
            folder_path = job_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)

        return job_path

    def _generate_job_id(self) -> str:
        """Tạo ID cho job"""
        return f"JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _save_job_metadata(self, job_path: Path, job_data: Dict[str, Any]) -> None:
        """Lưu metadata của job"""
        metadata_file = job_path / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(job_data, f, ensure_ascii=False, indent=2)

    def open_job(self, job_path: str) -> Dict[str, Any]:
        """
        Mở job từ đường dẫn
        Args:
            job_path: Đường dẫn đến thư mục job
        Returns:
            Dictionary chứa thông tin job
        """
        try:
            path = Path(job_path)
            metadata_file = path / "metadata.json"
            
            if not metadata_file.exists():
                raise FileNotFoundError("Không tìm thấy file metadata.json")
                
            with open(metadata_file, "r", encoding="utf-8") as f:
                job_data = json.load(f)
                
            return job_data
            
        except Exception as e:
            raise Exception(f"Lỗi khi mở job: {str(e)}")

    @staticmethod
    def save_job_config(job_data):
        """Lưu thông tin cấu hình job ra file"""
        if not job_data or 'path' not in job_data:
            raise ValueError("Thông tin job không hợp lệ")
        
        job_path = job_data['path']
        config_file = os.path.join(job_path, 'job_config.json')
        
        # Cập nhật thời gian chỉnh sửa
        job_data['updated_at'] = datetime.now().isoformat()
        
        # Lưu file
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(job_data, f, ensure_ascii=False, indent=2) 