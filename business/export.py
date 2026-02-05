"""
Data Export functionality for ASF-Engine
Export metrics, alerts, and logs to various formats
"""
import pandas as pd
import json
import csv
from typing import Dict, Any, List
from datetime import datetime
import io


class DataExporter:
    """Export data to various formats"""
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str = None) -> bytes:
        """
        Export data to CSV format
        
        Args:
            data: List of dictionaries to export
            filename: Optional filename
            
        Returns:
            CSV content as bytes
        """
        if not data:
            return b""
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Export to CSV
        if filename:
            df.to_csv(filename, index=False)
            with open(filename, 'rb') as f:
                return f.read()
        else:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            return csv_buffer.getvalue().encode('utf-8')
    
    def export_to_json(self, data: Any, filename: str = None, pretty: bool = True) -> bytes:
        """
        Export data to JSON format
        
        Args:
            data: Data to export
            filename: Optional filename
            pretty: Whether to pretty-print JSON
            
        Returns:
            JSON content as bytes
        """
        json_str = json.dumps(data, indent=2 if pretty else None, default=str)
        json_bytes = json_str.encode('utf-8')
        
        if filename:
            with open(filename, 'wb') as f:
                f.write(json_bytes)
        
        return json_bytes
    
    def export_to_excel(self, data: List[Dict[str, Any]], filename: str = None) -> bytes:
        """
        Export data to Excel format
        
        Args:
            data: List of dictionaries to export
            filename: Optional filename
            
        Returns:
            Excel content as bytes
        """
        if not data:
            return b""
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Export to Excel
        if filename:
            df.to_excel(filename, index=False, engine='openpyxl')
            with open(filename, 'rb') as f:
                return f.read()
        else:
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            return excel_buffer.getvalue()
    
    def export_metrics(
        self,
        metrics_data: List[Dict[str, Any]],
        format: str = "csv",
        filename: str = None
    ) -> bytes:
        """
        Export metrics data
        
        Args:
            metrics_data: List of metric records
            format: Export format (csv, json, excel)
            filename: Optional filename
            
        Returns:
            Exported data as bytes
        """
        if format.lower() == "csv":
            return self.export_to_csv(metrics_data, filename)
        elif format.lower() == "json":
            return self.export_to_json(metrics_data, filename)
        elif format.lower() == "excel":
            return self.export_to_excel(metrics_data, filename)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_alerts(
        self,
        alerts_data: List[Dict[str, Any]],
        format: str = "csv",
        filename: str = None
    ) -> bytes:
        """
        Export alerts data
        
        Args:
            alerts_data: List of alert records
            format: Export format (csv, json, excel)
            filename: Optional filename
            
        Returns:
            Exported data as bytes
        """
        return self.export_metrics(alerts_data, format, filename)
    
    def create_export_bundle(
        self,
        metrics: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
        logs: List[Dict[str, Any]],
        format: str = "json"
    ) -> bytes:
        """
        Create a complete export bundle with all data
        
        Args:
            metrics: Metrics data
            alerts: Alerts data
            logs: Logs data
            format: Export format
            
        Returns:
            Export bundle as bytes
        """
        bundle = {
            "export_date": datetime.now().isoformat(),
            "metrics": metrics,
            "alerts": alerts,
            "logs": logs,
            "summary": {
                "total_metrics": len(metrics),
                "total_alerts": len(alerts),
                "total_logs": len(logs)
            }
        }
        
        return self.export_to_json(bundle, pretty=True)
