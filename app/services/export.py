import json
from typing import List, Dict
from datetime import datetime

class ExportService:
    
    def export_weather_data(self, records: List[Dict]) -> bytes:
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "total_records": len(records)
            },
            "weather_records": records
        }
        return json.dumps(export_data, indent=2, default=str).encode('utf-8')
