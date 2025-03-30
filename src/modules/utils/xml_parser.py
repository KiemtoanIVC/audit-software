import xml.etree.ElementTree as ET
from typing import Dict, Any
import csv
from pathlib import Path

class XmlParser:
    def __init__(self):
        self.namespaces = {
            'ns': 'http://kekhaithue.gdt.gov.vn/TKhaiThue'
        }
        # Load cấu trúc chỉ tiêu
        self.cdkt_indices = self._load_chi_tieu('data/Chi tieu_CDKT.csv')
        self.kqkd_indices = self._load_chi_tieu('data/Chi tieu_KQKD.csv')

    def _load_chi_tieu(self, file_path: str) -> Dict[str, str]:
        """Load cấu trúc chỉ tiêu từ file CSV"""
        indices = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader)  # Bỏ qua header
                for row in reader:
                    if len(row) >= 2:
                        chi_tieu = row[0].strip()
                        ma_chi_tieu = row[1].strip().replace('<', '').replace('>', '')
                        indices[ma_chi_tieu] = chi_tieu
        except Exception as e:
            print(f"Lỗi khi đọc file {file_path}: {str(e)}")
        return indices

    def parse_bctc(self, file_path: str) -> Dict[str, Any]:
        """Parse file BCTC XML và trả về dữ liệu dạng dictionary"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Lấy thông tin chung
            general_info = self._get_general_info(root)
            
            # Lấy số liệu từ bảng cân đối kế toán
            balance_sheet = self._get_balance_sheet(root)
            
            # Lấy số liệu từ báo cáo kết quả kinh doanh
            income_statement = self._get_income_statement(root)
            
            return {
                "thong_tin_chung": general_info,
                "bang_can_doi": balance_sheet,
                "ket_qua_kinh_doanh": income_statement
            }
            
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file XML: {str(e)}")

    def _get_general_info(self, root: ET.Element) -> Dict[str, str]:
        """Lấy thông tin chung của doanh nghiệp"""
        try:
            # Tìm phần tử NNT trong namespace
            nnt = root.find('.//ns:NNT', self.namespaces)
            if nnt is None:
                raise Exception("Không tìm thấy thông tin người nộp thuế")

            # Lấy các giá trị
            ten_nnt = nnt.find('ns:tenNNT', self.namespaces)
            mst = nnt.find('ns:mst', self.namespaces)
            
            # Tìm kỳ kê khai
            ky_khai = root.find('.//ns:KyKKhaiThue/ns:kyKKhai', self.namespaces)

            return {
                "ten_doanh_nghiep": ten_nnt.text if ten_nnt is not None else "",
                "ma_so_thue": mst.text if mst is not None else "",
                "nam_tai_chinh": ky_khai.text if ky_khai is not None else ""
            }
        except Exception as e:
            raise Exception(f"Lỗi khi đọc thông tin chung: {str(e)}")

    def _get_balance_sheet(self, root: ET.Element) -> Dict[str, float]:
        """Lấy số liệu từ bảng cân đối kế toán"""
        try:
            cdkt = root.find('.//ns:CDKT_HoatDongLienTuc', self.namespaces)
            if cdkt is None:
                raise Exception("Không tìm thấy bảng cân đối kế toán")

            so_cuoi_nam = cdkt.find('ns:SoCuoiNam', self.namespaces)
            if so_cuoi_nam is None:
                raise Exception("Không tìm thấy số cuối năm")

            # Lấy tất cả các chỉ tiêu
            result = {}
            for ma_chi_tieu in self.cdkt_indices.keys():
                value = self._get_number(so_cuoi_nam, ma_chi_tieu)
                if value != 0:  # Chỉ lấy các chỉ tiêu có giá trị
                    result[ma_chi_tieu] = value
                    
            return result
            
        except Exception as e:
            raise Exception(f"Lỗi khi đọc bảng cân đối kế toán: {str(e)}")

    def _get_income_statement(self, root: ET.Element) -> Dict[str, float]:
        """Lấy số liệu từ báo cáo kết quả kinh doanh"""
        try:
            kqkd = root.find('.//ns:PL_KQHDSXKD', self.namespaces)
            if kqkd is None:
                raise Exception("Không tìm thấy báo cáo kết quả kinh doanh")

            nam_nay = kqkd.find('ns:NamNay', self.namespaces)
            if nam_nay is None:
                raise Exception("Không tìm thấy số liệu năm nay")

            # Lấy tất cả các chỉ tiêu
            result = {}
            for ma_chi_tieu in self.kqkd_indices.keys():
                value = self._get_number(nam_nay, ma_chi_tieu)
                if value != 0:  # Chỉ lấy các chỉ tiêu có giá trị
                    result[ma_chi_tieu] = value
                    
            return result
            
        except Exception as e:
            raise Exception(f"Lỗi khi đọc báo cáo kết quả kinh doanh: {str(e)}")

    def _get_number(self, element: ET.Element, code: str) -> float:
        """Chuyển đổi giá trị từ XML sang số"""
        try:
            value = element.find(f'ns:{code}', self.namespaces)
            if value is not None and value.text:
                return float(value.text)
            return 0
        except (ValueError, TypeError):
            return 0 