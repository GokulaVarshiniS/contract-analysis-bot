# src/report_generator.py

from fpdf import FPDF
import json
from datetime import datetime
from typing import Dict, List
import os


class ContractReportPDF(FPDF):
    """Custom PDF class for contract analysis reports"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Contract Analysis Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 8)
        self.cell(0, 5, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, 0, 1, 'L', True)
        self.ln(2)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, body)
        self.ln()
    
    def add_risk_indicator(self, level, score):
        """Add colored risk indicator"""
        if level == 'HIGH':
            self.set_fill_color(255, 68, 68)
        elif level == 'MEDIUM':
            self.set_fill_color(255, 170, 0)
        else:
            self.set_fill_color(68, 170, 68)
        
        self.set_font('Arial', 'B', 12)
        self.cell(40, 8, f'Risk: {level}', 0, 0, 'L', True)
        self.cell(40, 8, f'Score: {score}%', 0, 1, 'L')
        self.ln(2)


class ReportGenerator:
    """
    Generate PDF reports for contract analysis
    """
    
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_full_report(self, analysis_data: Dict) -> str:
        """
        Generate comprehensive PDF report
        """
        pdf = ContractReportPDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # 1. Executive Summary
        pdf.chapter_title('1. Executive Summary')
        summary = analysis_data.get('summary', {})
        if isinstance(summary.get('executive_summary'), str):
            pdf.chapter_body(summary['executive_summary'])
        
        # 2. Contract Overview
        pdf.chapter_title('2. Contract Overview')
        contract_info = analysis_data.get('classification', {})
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"Contract Type: {contract_info.get('contract_type', 'Unknown')}", 0, 1)
        pdf.cell(0, 6, f"Confidence: {contract_info.get('confidence', 'N/A')}", 0, 1)
        
        metadata = analysis_data.get('metadata', {})
        pdf.cell(0, 6, f"File: {metadata.get('file_name', 'N/A')}", 0, 1)
        pdf.cell(0, 6, f"Language: {metadata.get('language', 'English')}", 0, 1)
        pdf.ln(5)
        
        # 3. Risk Assessment
        pdf.chapter_title('3. Risk Assessment')
        risk_data = analysis_data.get('risk_assessment', {})
        pdf.add_risk_indicator(
            risk_data.get('overall_level', 'MEDIUM'),
            risk_data.get('composite_score', 50)
        )
        
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, f"Recommendation: {risk_data.get('recommendation', 'Review recommended')}")
        pdf.ln(3)
        
        # Risk breakdown
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 6, 'Risk Breakdown:', 0, 1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, f"  - High Risk Clauses: {risk_data.get('high_risk_count', 0)}", 0, 1)
        pdf.cell(0, 6, f"  - Medium Risk Clauses: {risk_data.get('medium_risk_count', 0)}", 0, 1)
        pdf.cell(0, 6, f"  - Low Risk Clauses: {risk_data.get('low_risk_count', 0)}", 0, 1)
        pdf.ln(5)
        
        # 4. Key Parties and Terms
        pdf.add_page()
        pdf.chapter_title('4. Key Parties and Terms')
        
        entities = analysis_data.get('entities', {})
        if entities.get('parties'):
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, 'Parties:', 0, 1)
            pdf.set_font('Arial', '', 10)
            for party in entities.get('parties', [])[:5]:
                pdf.cell(0, 5, f"  - {party}", 0, 1)
        
        if entities.get('dates'):
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, 'Key Dates:', 0, 1)
            pdf.set_font('Arial', '', 10)
            for date in entities.get('dates', [])[:5]:
                pdf.cell(0, 5, f"  - {date}", 0, 1)
        
        if entities.get('amounts'):
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, 'Financial Amounts:', 0, 1)
            pdf.set_font('Arial', '', 10)
            for amount in entities.get('amounts', [])[:5]:
                pdf.cell(0, 5, f"  - {amount}", 0, 1)
        
        pdf.ln(5)
        
        # 5. Unfavorable Terms
        pdf.chapter_title('5. Unfavorable Terms Identified')
        unfavorable = analysis_data.get('unfavorable_terms', [])
        
        for i, term in enumerate(unfavorable[:10], 1):
            pdf.set_font('Arial', 'B', 10)
            severity = term.get('severity', 'MEDIUM')
            pdf.cell(0, 6, f"{i}. [{severity}] {term.get('term_description', 'N/A')[:80]}", 0, 1)
            pdf.set_font('Arial', '', 9)
            
            if term.get('why_unfavorable'):
                pdf.multi_cell(0, 5, f"   Why: {term['why_unfavorable'][:200]}")
            
            if term.get('suggested_alternative'):
                pdf.multi_cell(0, 5, f"   Suggested: {term['suggested_alternative'][:200]}")
            
            pdf.ln(2)
        
        # 6. Clause Analysis
        pdf.add_page()
        pdf.chapter_title('6. Clause-by-Clause Analysis')
        
        clauses = analysis_data.get('analyzed_clauses', [])
        for i, clause in enumerate(clauses[:15], 1):
            pdf.set_font('Arial', 'B', 10)
            clause_type = clause.get('clause_type', 'General')
            risk_level = clause.get('risk_level', 'MEDIUM')
            pdf.cell(0, 6, f"Clause {i}: {clause_type} [{risk_level} Risk]", 0, 1)
            
            pdf.set_font('Arial', '', 9)
            explanation = clause.get('plain_language_explanation', 'N/A')
            if explanation:
                pdf.multi_cell(0, 5, f"Explanation: {explanation[:300]}")
            
            pdf.ln(3)
        
        # 7. Compliance Check
        pdf.add_page()
        pdf.chapter_title('7. Compliance Assessment')
        
        compliance = analysis_data.get('compliance', {})
        status = compliance.get('compliance_status', 'NEEDS_REVIEW')
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 6, f"Status: {status}", 0, 1)
        pdf.ln(3)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, 'Applicable Laws:', 0, 1)
        pdf.set_font('Arial', '', 9)
        for law in compliance.get('applicable_laws', [])[:5]:
            pdf.cell(0, 5, f"  - {law.get('law_name', 'N/A')}", 0, 1)
        
        pdf.ln(3)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, 'Compliance Issues:', 0, 1)
        pdf.set_font('Arial', '', 9)
        for issue in compliance.get('compliance_issues', [])[:5]:
            pdf.multi_cell(0, 5, f"  [{issue.get('severity', 'N/A')}] {issue.get('issue', 'N/A')[:150]}")
        
        # 8. Recommendations
        pdf.add_page()
        pdf.chapter_title('8. Risk Mitigation Strategies')
        
        strategies = analysis_data.get('mitigation_strategies', [])
        for i, strategy in enumerate(strategies[:10], 1):
            pdf.set_font('Arial', 'B', 10)
            priority = strategy.get('priority', 'MEDIUM')
            pdf.cell(0, 6, f"{i}. [{priority}] {strategy.get('action', 'N/A')}", 0, 1)
            pdf.set_font('Arial', '', 9)
            pdf.multi_cell(0, 5, f"   {strategy.get('description', '')[:250]}")
            pdf.ln(2)
        
        # 9. Disclaimer
        pdf.add_page()
        pdf.chapter_title('9. Disclaimer')
        disclaimer = """
This report is generated by an AI-powered contract analysis tool and is intended for 
informational purposes only. It does not constitute legal advice.

The analysis provided should be reviewed by a qualified legal professional before making 
any decisions based on this report. The accuracy of the analysis depends on the quality 
and completeness of the input document.

For legally binding decisions, please consult with a licensed attorney who specializes 
in contract law and is familiar with Indian legal requirements.

This tool is designed to assist small and medium business owners in understanding 
contracts better, but it is not a substitute for professional legal counsel.
        """
        pdf.chapter_body(disclaimer)
        
        # Save PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contract_analysis_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        pdf.output(filepath)
        return filepath
    
    def generate_summary_report(self, analysis_data: Dict) -> str:
        """
        Generate a brief summary PDF
        """
        pdf = ContractReportPDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        # Quick Summary
        pdf.chapter_title('Contract Analysis Summary')
        
        # Risk Score
        risk_data = analysis_data.get('risk_assessment', {})
        pdf.add_risk_indicator(
            risk_data.get('overall_level', 'MEDIUM'),
            risk_data.get('composite_score', 50)
        )
        
        # Key Points
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Key Points:', 0, 1)
        
        summary = analysis_data.get('summary', {})
        if isinstance(summary.get('key_risks_for_sme'), list):
            pdf.set_font('Arial', '', 10)
            for risk in summary['key_risks_for_sme'][:5]:
                pdf.multi_cell(0, 5, f"• {risk}")
        
        pdf.ln(5)
        
        # Top Unfavorable Terms
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Top Concerns:', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        unfavorable = analysis_data.get('unfavorable_terms', [])
        for term in unfavorable[:3]:
            pdf.multi_cell(0, 5, f"• {term.get('term_description', 'N/A')[:100]}")
        
        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contract_summary_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        pdf.output(filepath)
        return filepath


class AuditLogger:
    """
    Maintain audit trail of contract analyses
    """
    
    def __init__(self, log_dir: str = "audit_logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log_analysis(self, file_name: str, analysis_data: Dict) -> str:
        """
        Log analysis details for audit purposes
        """
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            'timestamp': timestamp,
            'file_analyzed': file_name,
            'contract_type': analysis_data.get('classification', {}).get('contract_type'),
            'risk_level': analysis_data.get('risk_assessment', {}).get('overall_level'),
            'risk_score': analysis_data.get('risk_assessment', {}).get('composite_score'),
            'clauses_analyzed': len(analysis_data.get('analyzed_clauses', [])),
            'unfavorable_terms_found': len(analysis_data.get('unfavorable_terms', [])),
            'compliance_status': analysis_data.get('compliance', {}).get('compliance_status'),
            'report_generated': True
        }
        
        log_filename = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_path = os.path.join(self.log_dir, log_filename)
        
        with open(log_path, 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        return log_path