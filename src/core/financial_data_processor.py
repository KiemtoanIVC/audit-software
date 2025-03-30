import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
import csv

class FinancialDataProcessor:
    def __init__(self):
        self.company_info = {}
        self.key_metrics = {}
        
        # Load chỉ tiêu từ file CSV
        self.cdkt_indices = self._load_chi_tieu('CDKT')
        self.kqkd_indices = self._load_chi_tieu('KQKD')

    def _load_chi_tieu(self, type_name):
        """Load chỉ tiêu từ file CSV"""
        try:
            file_path = Path(__file__).parent.parent / 'data' / f'Chi tieu_{type_name}.csv'
            indices = {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                next(reader)  # Bỏ qua header
                for row in reader:
                    if len(row) >= 2:
                        ma_chi_tieu = row[1].strip()  # Lấy mã chỉ tiêu (cột thứ 2)
                        indices[ma_chi_tieu] = row[0].strip()  # Lấy tên chỉ tiêu (cột thứ 1)
                        
            return indices
            
        except Exception as e:
            print(f"Lỗi khi load chỉ tiêu {type_name}: {str(e)}")
            return {}

    def load_xml_data(self, file_path):
        """Load và xử lý file XML BCTC"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Parse thông tin chung
            self._get_general_info(root)
            
            # Parse số liệu tài chính
            self._get_financial_data(root)
            
            return True
            
        except Exception as e:
            print(f"Lỗi khi xử lý file XML: {str(e)}")
            return False

    def _get_general_info(self, root):
        """Lấy thông tin chung từ XML"""
        try:
            # Namespace của XML
            ns = {'ns': 'http://kekhaithue.gdt.gov.vn/TKhaiThue'}
            
            # Lấy thông tin NNT (Người nộp thuế)
            nnt = root.find('.//ns:NNT', ns)
            if nnt is not None:
                self.company_info = {
                    'name': nnt.find('ns:tenNNT', ns).text,
                    'tax_code': nnt.find('ns:mst', ns).text,
                    'address': nnt.find('ns:dchiNNT', ns).text
                }
            
            # Lấy kỳ kê khai
            ky_kkhai = root.find('.//ns:KyKKhaiThue', ns)
            if ky_kkhai is not None:
                self.company_info.update({
                    'period_from': ky_kkhai.find('ns:kyKKhaiTuNgay', ns).text,
                    'period_to': ky_kkhai.find('ns:kyKKhaiDenNgay', ns).text
                })
                
        except Exception as e:
            print(f"Lỗi khi lấy thông tin chung: {str(e)}")

    def _get_financial_data(self, root):
        """Lấy số liệu tài chính từ XML"""
        try:
            # Namespace của XML
            ns = {'ns': 'http://kekhaithue.gdt.gov.vn/TKhaiThue'}
            
            # Lấy số liệu từ CDKT
            cdkt = root.find('.//ns:CDKT_HoatDongLienTuc', ns)
            if cdkt is not None:
                so_cuoi_nam = cdkt.find('ns:SoCuoiNam', ns)
                
                self.key_metrics = {
                    'total_assets': float(so_cuoi_nam.find('ns:ct270', ns).text or 0),
                    'equity': float(so_cuoi_nam.find('ns:ct400', ns).text or 0)
                }
            
            # Lấy số liệu từ KQKD
            kqkd = root.find('.//ns:PL_KQHDSXKD', ns)
            if kqkd is not None:
                nam_nay = kqkd.find('ns:NamNay', ns)
                
                self.key_metrics.update({
                    'revenue': float(nam_nay.find('ns:ct01', ns).text or 0),
                    'profit_before_tax': float(nam_nay.find('ns:ct50', ns).text or 0),
                    'total_expenses': float(nam_nay.find('ns:ct11', ns).text or 0)
                })
                
        except Exception as e:
            print(f"Lỗi khi lấy số liệu tài chính: {str(e)}")

    def get_key_metrics(self):
        """Trả về các chỉ tiêu tài chính chính"""
        return self.key_metrics 