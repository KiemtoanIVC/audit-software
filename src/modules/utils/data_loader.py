import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any

class DataLoader:
    def load_xml_data(self, file_path: str) -> Dict[str, Any]:
        """
        Đọc và parse file XML
        Args:
            file_path: Đường dẫn đến file XML
        Returns:
            Dict chứa dữ liệu đã parse
        """
        try:
            # Đọc file XML
            xml_data = self._read_xml_file(file_path)
            
            # Transform data
            transformed_data = self._transform_data(xml_data)
            
            return transformed_data
            
        except Exception as e:
            raise Exception(f"Lỗi khi đọc file XML: {str(e)}")

    def _read_xml_file(self, file_path: str) -> ET.Element:
        """
        Đọc file XML và trả về root element
        """
        try:
            tree = ET.parse(file_path)
            return tree.getroot()
        except ET.ParseError as e:
            raise Exception(f"File XML không hợp lệ: {str(e)}")
        except FileNotFoundError:
            raise Exception(f"Không tìm thấy file: {file_path}")

    def _transform_data(self, xml_root: ET.Element) -> Dict[str, Any]:
        """
        Chuyển đổi dữ liệu XML thành dict
        """
        data = {}
        
        # TODO: Implement logic chuyển đổi dữ liệu tùy theo cấu trúc XML
        # Ví dụ:
        for child in xml_root:
            data[child.tag] = child.text
            
        return data 