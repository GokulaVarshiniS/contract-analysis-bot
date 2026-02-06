# src/template_manager.py

import json
import os
from typing import Dict, List


class TemplateManager:
    """
    Manage standardized contract templates for SMEs
    """
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
        os.makedirs(template_dir, exist_ok=True)
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Create default templates if they don't exist"""
        
        templates = {
            'employment_agreement': {
                'name': 'Employment Agreement',
                'description': 'Standard employment contract for hiring employees',
                'suitable_for': 'Hiring full-time or part-time employees',
                'key_clauses': [
                    {
                        'name': 'Position and Duties',
                        'template': 'The Employee shall serve as [POSITION] and shall perform duties as assigned by the Employer, including but not limited to [PRIMARY DUTIES].'
                    },
                    {
                        'name': 'Compensation',
                        'template': 'The Employee shall receive a monthly salary of INR [AMOUNT], payable on the [DAY] of each month, subject to applicable tax deductions.'
                    },
                    {
                        'name': 'Working Hours',
                        'template': 'The Employee shall work [NUMBER] hours per week, from [START TIME] to [END TIME], Monday through Friday, with reasonable flexibility as required.'
                    },
                    {
                        'name': 'Leave Policy',
                        'template': 'The Employee shall be entitled to [NUMBER] days of paid leave per year, in addition to public holidays as per the company policy.'
                    },
                    {
                        'name': 'Termination',
                        'template': 'Either party may terminate this agreement by providing [NUMBER] days written notice. The Employer may terminate immediately for cause, including misconduct or breach of contract.'
                    },
                    {
                        'name': 'Confidentiality',
                        'template': 'The Employee agrees to maintain confidentiality of all proprietary information during and after employment for a period of [NUMBER] years.'
                    }
                ],
                'indian_compliance_notes': [
                    'Must comply with applicable labor laws',
                    'PF and ESI contributions as applicable',
                    'Gratuity provisions for employees with 5+ years',
                    'Minimum wage requirements per state'
                ]
            },
            'vendor_contract': {
                'name': 'Vendor/Supplier Agreement',
                'description': 'Standard contract for engaging vendors or suppliers',
                'suitable_for': 'Purchasing goods or services from vendors',
                'key_clauses': [
                    {
                        'name': 'Scope of Work',
                        'template': 'The Vendor shall supply [GOODS/SERVICES] as per the specifications mentioned in Annexure A, meeting the quality standards agreed upon.'
                    },
                    {
                        'name': 'Pricing and Payment',
                        'template': 'The total contract value is INR [AMOUNT]. Payment shall be made within [NUMBER] days of receipt of invoice and satisfactory delivery.'
                    },
                    {
                        'name': 'Delivery Terms',
                        'template': 'Delivery shall be made to [LOCATION] within [NUMBER] days of order placement. The Vendor shall bear the risk until delivery is completed.'
                    },
                    {
                        'name': 'Quality Assurance',
                        'template': 'All goods/services must meet the quality standards as specified. The Buyer reserves the right to reject non-conforming deliveries.'
                    },
                    {
                        'name': 'Warranties',
                        'template': 'The Vendor warrants that all goods/services shall be free from defects for a period of [NUMBER] months from delivery.'
                    },
                    {
                        'name': 'Liability Cap',
                        'template': 'The total liability of either party under this agreement shall not exceed the total contract value or INR [AMOUNT], whichever is lower.'
                    }
                ],
                'indian_compliance_notes': [
                    'GST registration and invoicing requirements',
                    'TDS deduction obligations',
                    'Contract Act 1872 provisions'
                ]
            },
            'lease_agreement': {
                'name': 'Commercial Lease Agreement',
                'description': 'Standard lease for commercial property rental',
                'suitable_for': 'Renting office space, shops, or warehouses',
                'key_clauses': [
                    {
                        'name': 'Premises Description',
                        'template': 'The Lessor hereby leases to the Lessee the premises located at [ADDRESS], comprising [AREA] square feet, for commercial use.'
                    },
                    {
                        'name': 'Lease Term',
                        'template': 'The lease term shall be [NUMBER] years, commencing from [DATE] and ending on [DATE], with an option to renew upon mutual agreement.'
                    },
                    {
                        'name': 'Rent and Security Deposit',
                        'template': 'Monthly rent shall be INR [AMOUNT], payable by the [DAY] of each month. A security deposit of INR [AMOUNT] (equivalent to [NUMBER] months rent) shall be paid upon signing.'
                    },
                    {
                        'name': 'Rent Escalation',
                        'template': 'Rent shall increase by [PERCENTAGE]% annually or as mutually agreed, with [NUMBER] months prior notice.'
                    },
                    {
                        'name': 'Maintenance',
                        'template': 'The Lessee shall maintain the premises in good condition. Major structural repairs shall be the responsibility of the Lessor.'
                    },
                    {
                        'name': 'Termination',
                        'template': 'Either party may terminate with [NUMBER] months written notice. Early termination by Lessee may result in forfeiture of [AMOUNT/MONTHS] security deposit.'
                    }
                ],
                'indian_compliance_notes': [
                    'Registration required for leases over 11 months',
                    'Stamp duty as per state regulations',
                    'Rent Control Act provisions (varies by state)'
                ]
            },
            'service_contract': {
                'name': 'Service Agreement',
                'description': 'Standard contract for professional services',
                'suitable_for': 'Engaging consultants, agencies, or service providers',
                'key_clauses': [
                    {
                        'name': 'Services',
                        'template': 'The Service Provider shall provide [DESCRIPTION OF SERVICES] as detailed in Annexure A, meeting the deliverables and timelines specified.'
                    },
                    {
                        'name': 'Service Fees',
                        'template': 'The Client shall pay INR [AMOUNT] for the services. Payment terms: [PERCENTAGE]% upon signing, [PERCENTAGE]% upon completion, or as per milestone schedule.'
                    },
                    {
                        'name': 'Performance Standards',
                        'template': 'Services shall be performed in a professional manner, meeting industry standards. The Service Provider shall maintain qualified personnel for the engagement.'
                    },
                    {
                        'name': 'Intellectual Property',
                        'template': 'All deliverables created under this agreement shall be owned by the Client upon full payment. The Service Provider retains rights to pre-existing intellectual property.'
                    },
                    {
                        'name': 'Confidentiality',
                        'template': 'Both parties agree to maintain confidentiality of proprietary information shared during the engagement for [NUMBER] years after termination.'
                    },
                    {
                        'name': 'Limitation of Liability',
                        'template': 'Neither party shall be liable for indirect or consequential damages. Total liability shall not exceed the fees paid under this agreement.'
                    }
                ],
                'indian_compliance_notes': [
                    'GST applicability on services',
                    'TDS under Section 194J for professional services',
                    'IT Act compliance for digital services'
                ]
            },
            'partnership_deed': {
                'name': 'Partnership Deed',
                'description': 'Agreement for forming a business partnership',
                'suitable_for': 'Starting a partnership firm with co-founders',
                'key_clauses': [
                    {
                        'name': 'Partnership Details',
                        'template': 'The Partners hereby agree to carry on business in partnership under the name [FIRM NAME] with effect from [DATE].'
                    },
                    {
                        'name': 'Capital Contribution',
                        'template': 'Partner A shall contribute INR [AMOUNT] ([PERCENTAGE]%), Partner B shall contribute INR [AMOUNT] ([PERCENTAGE]%) as initial capital.'
                    },
                    {
                        'name': 'Profit/Loss Sharing',
                        'template': 'Profits and losses shall be shared among partners in the ratio of [RATIO], calculated after deducting interest on capital and partner salaries.'
                    },
                    {
                        'name': 'Management',
                        'template': 'All partners shall have equal rights in the management of the firm. Major decisions require unanimous consent of all partners.'
                    },
                    {
                        'name': 'Partner Duties',
                        'template': 'Each partner shall devote full time and attention to the business, act in good faith, and not engage in competing businesses.'
                    },
                    {
                        'name': 'Dissolution',
                        'template': 'The partnership may be dissolved by mutual consent or by [NUMBER] months notice from any partner. Upon dissolution, assets shall be distributed as per the Partnership Act.'
                    }
                ],
                'indian_compliance_notes': [
                    'Registration under Partnership Act 1932 recommended',
                    'PAN in the name of the firm',
                    'GST registration if applicable',
                    'Partners personal liability for firm debts'
                ]
            }
        }
        
        for template_name, template_data in templates.items():
            filepath = os.path.join(self.template_dir, f"{template_name}.json")
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump(template_data, f, indent=2)
    
    def get_template(self, template_name: str) -> Dict:
        """Get a specific template"""
        filepath = os.path.join(self.template_dir, f"{template_name}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}
    
    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        templates = []
        for filename in os.listdir(self.template_dir):
            if filename.endswith('.json'):
                template = self.get_template(filename.replace('.json', ''))
                templates.append({
                    'id': filename.replace('.json', ''),
                    'name': template.get('name', 'Unknown'),
                    'description': template.get('description', '')
                })
        return templates
    
    def generate_template_document(self, template_name: str, variables: Dict) -> str:
        """
        Generate a contract document from template with filled variables
        """
        template = self.get_template(template_name)
        if not template:
            return "Template not found"
        
        document = f"# {template['name']}\n\n"
        document += f"*{template['description']}*\n\n"
        document += "---\n\n"
        
        for i, clause in enumerate(template.get('key_clauses', []), 1):
            clause_text = clause['template']
            
            # Replace variables
            for key, value in variables.items():
                clause_text = clause_text.replace(f'[{key.upper()}]', str(value))
            
            document += f"## {i}. {clause['name']}\n\n"
            document += f"{clause_text}\n\n"
        
        document += "---\n\n"
        document += "## Compliance Notes for Indian SMEs\n\n"
        for note in template.get('indian_compliance_notes', []):
            document += f"- {note}\n"
        
        return document