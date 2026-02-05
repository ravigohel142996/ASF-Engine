"""
PDF Report Generation for ASF-Engine
Creates professional reports of system health and predictions
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict, Any, List
import io


class ReportGenerator:
    """Generate PDF reports for system monitoring"""
    
    def __init__(self):
        """Initialize report generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E88E5'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#424242'),
            spaceAfter=12,
            spaceBefore=12
        ))
    
    def generate_system_report(
        self,
        risk_report: Dict[str, Any],
        metrics: Dict[str, Any],
        alerts: List[Dict[str, Any]],
        output_path: str = None
    ) -> bytes:
        """
        Generate a comprehensive system health report
        
        Args:
            risk_report: Risk assessment data
            metrics: System metrics
            alerts: List of alerts
            output_path: Optional file path to save PDF
            
        Returns:
            PDF content as bytes
        """
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for PDF elements
        elements = []
        
        # Add header
        elements.extend(self._add_header())
        
        # Add executive summary
        elements.extend(self._add_executive_summary(risk_report))
        
        # Add system health section
        elements.extend(self._add_health_section(risk_report, metrics))
        
        # Add alerts section
        elements.extend(self._add_alerts_section(alerts))
        
        # Add recommendations
        elements.extend(self._add_recommendations_section(risk_report))
        
        # Add footer
        elements.extend(self._add_footer())
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def _add_header(self) -> List:
        """Add report header"""
        elements = []
        
        # Title
        title = Paragraph(
            "🤖 AI System Failure Monitoring Report",
            self.styles['CustomTitle']
        )
        elements.append(title)
        
        # Metadata
        now = datetime.now()
        metadata = Paragraph(
            f"<b>Generated:</b> {now.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"<b>Report Type:</b> System Health Assessment",
            self.styles['Normal']
        )
        elements.append(metadata)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_executive_summary(self, risk_report: Dict[str, Any]) -> List:
        """Add executive summary section"""
        elements = []
        
        # Section title
        title = Paragraph("Executive Summary", self.styles['CustomSubtitle'])
        elements.append(title)
        
        # Health score
        health_score = risk_report.get('health_score', 0)
        health_status = "Excellent" if health_score > 90 else "Good" if health_score > 70 else "Fair" if health_score > 50 else "Critical"
        
        summary_text = f"""
        <b>Overall Health Score:</b> {health_score:.1f}/100 ({health_status})<br/>
        <b>Failure Probability:</b> {risk_report['failure_probability']['overall']:.1%}<br/>
        <b>System Trend:</b> {risk_report.get('trend', 'Stable')}<br/>
        <b>Risk Level:</b> {risk_report.get('risk_level', 'Medium')}
        """
        
        summary = Paragraph(summary_text, self.styles['Normal'])
        elements.append(summary)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_health_section(self, risk_report: Dict[str, Any], metrics: Dict[str, Any]) -> List:
        """Add system health metrics section"""
        elements = []
        
        # Section title
        title = Paragraph("System Health Metrics", self.styles['CustomSubtitle'])
        elements.append(title)
        
        # Create metrics table
        data = [
            ['Metric', 'Current Value', 'Status'],
            ['Accuracy', f"{metrics.get('accuracy', 0):.2%}", '✓ Normal'],
            ['Latency', f"{metrics.get('latency_ms', 0):.1f} ms", '✓ Normal'],
            ['Error Rate', f"{metrics.get('error_rate', 0):.2%}", '✓ Normal'],
            ['CPU Usage', f"{metrics.get('cpu_usage', 0):.1%}", '✓ Normal'],
            ['Memory Usage', f"{metrics.get('memory_usage', 0):.1%}", '✓ Normal']
        ]
        
        table = Table(data, colWidths=[2*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E88E5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_alerts_section(self, alerts: List[Dict[str, Any]]) -> List:
        """Add alerts section"""
        elements = []
        
        # Section title
        title = Paragraph(f"Active Alerts ({len(alerts)})", self.styles['CustomSubtitle'])
        elements.append(title)
        
        if alerts:
            for alert in alerts[:10]:  # Limit to 10 alerts
                alert_text = f"""
                <b>{alert.get('severity', 'INFO').upper()}:</b> {alert.get('message', 'No message')}<br/>
                <i>Time: {alert.get('timestamp', 'Unknown')}</i>
                """
                alert_para = Paragraph(alert_text, self.styles['Normal'])
                elements.append(alert_para)
                elements.append(Spacer(1, 10))
        else:
            no_alerts = Paragraph("No active alerts - System operating normally", self.styles['Normal'])
            elements.append(no_alerts)
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_recommendations_section(self, risk_report: Dict[str, Any]) -> List:
        """Add recommendations section"""
        elements = []
        
        # Section title
        title = Paragraph("Recommendations", self.styles['CustomSubtitle'])
        elements.append(title)
        
        # Get recommendations from risk report
        recommendations = risk_report.get('mitigation_actions', {})
        
        # Immediate actions
        if recommendations.get('immediate_actions'):
            immediate_title = Paragraph("<b>Immediate Actions (1-4 hours):</b>", self.styles['Normal'])
            elements.append(immediate_title)
            
            for action in recommendations['immediate_actions'][:5]:
                action_text = f"• {action}"
                elements.append(Paragraph(action_text, self.styles['Normal']))
            
            elements.append(Spacer(1, 10))
        
        # Short-term actions
        if recommendations.get('short_term_actions'):
            short_term_title = Paragraph("<b>Short-term Actions (1-7 days):</b>", self.styles['Normal'])
            elements.append(short_term_title)
            
            for action in recommendations['short_term_actions'][:5]:
                action_text = f"• {action}"
                elements.append(Paragraph(action_text, self.styles['Normal']))
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _add_footer(self) -> List:
        """Add report footer"""
        elements = []
        
        footer = Paragraph(
            "<i>This report was generated automatically by ASF-Engine AI System Monitoring Platform. "
            "For more information, visit your dashboard.</i>",
            self.styles['Normal']
        )
        elements.append(footer)
        
        return elements
