import os
import json
from typing import Dict, List
from dotenv import load_dotenv
import logging
import re

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContractAnalyzer:
    """LLM-based contract analysis using Claude 3 or GPT-4 (with fallback demo mode)"""
    
    def __init__(self, llm_provider: str = "anthropic"):
        self.llm_provider = llm_provider
        self.client = None
        self.demo_mode = False
        
        # Try to initialize API client
        if llm_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key and api_key != "your_anthropic_api_key_here":
                try:
                    from anthropic import Anthropic
                    self.client = Anthropic(api_key=api_key)
                    self.model = "claude-3-sonnet-20240229"
                except Exception as e:
                    logger.warning(f"Could not initialize Anthropic client: {e}")
                    self.demo_mode = True
            else:
                self.demo_mode = True
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key != "your_openai_api_key_here":
                try:
                    import openai
                    openai.api_key = api_key
                    self.model = "gpt-4-turbo-preview"
                except Exception as e:
                    logger.warning(f"Could not initialize OpenAI client: {e}")
                    self.demo_mode = True
            else:
                self.demo_mode = True
        
        if self.demo_mode:
            logger.info("Running in DEMO MODE - Using simulated AI responses")
        
        self.contract_types = [
            "Employment Agreement", "Vendor Contract", "Lease Agreement",
            "Partnership Deed", "Service Contract", "Non-Disclosure Agreement",
            "Licensing Agreement", "Consulting Agreement", "Other"
        ]
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Make API call to LLM or return demo response"""
        if self.demo_mode:
            return self._get_demo_response(prompt)
        
        try:
            if self.llm_provider == "anthropic" and self.client:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=system_prompt or "You are a legal contract analysis expert.",
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
            elif self.llm_provider == "openai":
                import openai
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt or "You are a legal contract analysis expert."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=4096
                )
                return response.choices[0].message.content
            else:
                return self._get_demo_response(prompt)
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return self._get_demo_response(prompt)
    
    def _get_demo_response(self, prompt: str) -> str:
        """Generate demo responses for testing without API key"""
        if "classify" in prompt.lower():
            return json.dumps({
                "contract_type": "Employment Agreement",
                "confidence": "high",
                "reasoning": "Document contains employment terms, salary, termination clauses typical of employment contracts."
            })
        elif "analyze" in prompt.lower() and "clause" in prompt.lower():
            return json.dumps({
                "plain_language_explanation": "This clause defines the terms and conditions that both parties must follow.",
                "clause_type": "General Terms",
                "risk_level": "MEDIUM",
                "risk_factors": ["May contain binding obligations", "Should review carefully"],
                "is_favorable": True,
                "unfavorable_aspects": [],
                "suggested_modifications": ["Consider adding more specific terms"],
                "compliance_issues": []
            })
        elif "summary" in prompt.lower():
            return json.dumps({
                "executive_summary": "This is a standard business contract that establishes the terms of engagement between two parties. It includes provisions for compensation, termination, confidentiality, and dispute resolution. The contract appears to follow standard legal practices but contains some clauses that may require negotiation.",
                "key_parties": ["Party A - The Employer/Client", "Party B - The Employee/Vendor"],
                "contract_duration": "As specified in the contract terms",
                "key_obligations": {
                    "party_1": ["Provide compensation", "Maintain workplace"],
                    "party_2": ["Perform duties", "Maintain confidentiality"]
                },
                "financial_terms": {
                    "amounts": ["As specified in contract"],
                    "payment_terms": "Monthly/As per agreement"
                },
                "important_dates": ["Contract start date", "Review periods"],
                "termination_conditions": ["Notice period required", "Cause-based termination"],
                "key_risks_for_sme": [
                    "Non-compete clause may restrict future business",
                    "Indemnity clause could create liability",
                    "Penalty clauses need careful review"
                ],
                "recommended_actions": [
                    "Review all financial obligations",
                    "Consult legal counsel for high-risk clauses",
                    "Negotiate unfavorable terms before signing"
                ]
            })
        elif "unfavorable" in prompt.lower():
            return json.dumps({
                "unfavorable_terms": [
                    {
                        "term_description": "Non-compete clause restricting business activities for 12 months",
                        "risk_category": "legal",
                        "severity": "HIGH",
                        "why_unfavorable": "May restrict your ability to work in the same industry",
                        "potential_consequences": "Legal action if violated, loss of business opportunities",
                        "suggested_alternative": "Reduce non-compete period to 6 months or limit geographic scope",
                        "negotiation_tip": "Request specific geographic limitations and shorter duration"
                    },
                    {
                        "term_description": "Unlimited indemnification clause",
                        "risk_category": "financial",
                        "severity": "HIGH",
                        "why_unfavorable": "Could expose you to unlimited financial liability",
                        "potential_consequences": "May have to pay for damages beyond contract value",
                        "suggested_alternative": "Cap indemnity at contract value or specific amount",
                        "negotiation_tip": "Propose mutual indemnification with caps"
                    },
                    {
                        "term_description": "Unilateral termination rights",
                        "risk_category": "operational",
                        "severity": "MEDIUM",
                        "why_unfavorable": "Other party can terminate without cause",
                        "potential_consequences": "Sudden loss of contract, business disruption",
                        "suggested_alternative": "Require mutual termination rights with notice period",
                        "negotiation_tip": "Request minimum 30-60 days notice for termination"
                    },
                    {
                        "term_description": "Automatic renewal clause",
                        "risk_category": "operational",
                        "severity": "MEDIUM",
                        "why_unfavorable": "Contract renews automatically without explicit consent",
                        "potential_consequences": "Locked into unfavorable terms",
                        "suggested_alternative": "Require written consent for renewal",
                        "negotiation_tip": "Add clause requiring 30 days notice before auto-renewal"
                    }
                ]
            })
        elif "compliance" in prompt.lower():
            return json.dumps({
                "applicable_laws": [
                    {"law_name": "Indian Contract Act, 1872", "relevance": "Governs contract validity and enforcement"},
                    {"law_name": "Information Technology Act, 2000", "relevance": "Applicable for digital contracts"},
                    {"law_name": "Labour Laws", "relevance": "Applicable for employment contracts"}
                ],
                "compliance_status": "PARTIALLY_COMPLIANT",
                "compliance_issues": [
                    {"issue": "Stamp duty may be required", "severity": "MEDIUM", "recommendation": "Verify stamp duty requirements for your state"},
                    {"issue": "Registration may be needed for certain contract types", "severity": "LOW", "recommendation": "Check if registration is required"}
                ],
                "missing_mandatory_clauses": ["Force Majeure clause recommended", "Data protection clause may be needed"],
                "general_recommendations": ["Have the contract reviewed by a legal professional", "Ensure proper execution with witnesses"]
            })
        elif "ambiguit" in prompt.lower():
            return json.dumps({
                "ambiguities": [
                    {
                        "ambiguous_text": "reasonable time",
                        "why_ambiguous": "Does not specify exact duration",
                        "possible_interpretations": ["Could mean days, weeks, or months", "Subject to interpretation"],
                        "suggested_clarification": "Specify exact number of days (e.g., '15 business days')"
                    },
                    {
                        "ambiguous_text": "best efforts",
                        "why_ambiguous": "Subjective standard without measurable criteria",
                        "possible_interpretations": ["Could mean any effort", "Could mean maximum possible effort"],
                        "suggested_clarification": "Define specific actions or metrics that constitute 'best efforts'"
                    }
                ],
                "overall_clarity_score": "7"
            })
        else:
            return json.dumps({"message": "Analysis completed", "status": "success"})
    
    def classify_contract(self, text: str) -> Dict:
        """Classify the type of contract"""
        # Simple keyword-based classification for demo mode
        text_lower = text.lower()
        
        if self.demo_mode:
            if "employment" in text_lower or "employee" in text_lower or "salary" in text_lower:
                contract_type = "Employment Agreement"
            elif "vendor" in text_lower or "supplier" in text_lower or "supply" in text_lower:
                contract_type = "Vendor Contract"
            elif "lease" in text_lower or "rent" in text_lower or "premises" in text_lower:
                contract_type = "Lease Agreement"
            elif "partner" in text_lower or "partnership" in text_lower:
                contract_type = "Partnership Deed"
            elif "service" in text_lower or "services" in text_lower:
                contract_type = "Service Contract"
            elif "confidential" in text_lower or "nda" in text_lower or "disclosure" in text_lower:
                contract_type = "Non-Disclosure Agreement"
            else:
                contract_type = "Service Contract"
            
            return {
                "contract_type": contract_type,
                "confidence": "high",
                "reasoning": f"Identified based on key terms found in the document. [DEMO MODE]"
            }
        
        prompt = f"""Analyze the following contract text and classify it into one of these categories:
{', '.join(self.contract_types)}

Contract Text (first 2000 characters):
{text[:2000]}

Respond in JSON format:
{{"contract_type": "type name", "confidence": "high/medium/low", "reasoning": "brief explanation"}}"""
        
        response = self._call_llm(prompt)
        try:
            json_match = response[response.find('{'):response.rfind('}')+1]
            return json.loads(json_match)
        except:
            return {"contract_type": "Unknown", "confidence": "low", "reasoning": response}
    
    def analyze_clauses(self, clauses: List[Dict]) -> List[Dict]:
        """Analyze each clause for risks and provide explanations"""
        analyzed_clauses = []
        
        risk_keywords = {
            'HIGH': ['indemnify', 'unlimited', 'waive', 'irrevocable', 'perpetual', 'sole discretion'],
            'MEDIUM': ['penalty', 'terminate', 'liability', 'damages', 'non-compete', 'confidential'],
            'LOW': ['notice', 'mutual', 'reasonable', 'agree', 'consent']
        }
        
        for clause in clauses[:20]:
            clause_text = clause.get('full_text', clause.get('content', '')).lower()
            
            # Determine risk level based on keywords
            risk_level = 'LOW'
            risk_factors = []
            
            for level, keywords in risk_keywords.items():
                for keyword in keywords:
                    if keyword in clause_text:
                        if level == 'HIGH':
                            risk_level = 'HIGH'
                            risk_factors.append(f"Contains '{keyword}' - high risk indicator")
                        elif level == 'MEDIUM' and risk_level != 'HIGH':
                            risk_level = 'MEDIUM'
                            risk_factors.append(f"Contains '{keyword}' - medium risk indicator")
            
            # Determine clause type
            clause_type = 'General'
            if 'terminat' in clause_text:
                clause_type = 'Termination'
            elif 'payment' in clause_text or 'salary' in clause_text or 'compensation' in clause_text:
                clause_type = 'Payment/Compensation'
            elif 'confidential' in clause_text:
                clause_type = 'Confidentiality'
            elif 'indemnif' in clause_text:
                clause_type = 'Indemnification'
            elif 'non-compete' in clause_text or 'non compete' in clause_text:
                clause_type = 'Non-Compete'
            elif 'intellectual property' in clause_text or 'ip' in clause_text:
                clause_type = 'Intellectual Property'
            elif 'dispute' in clause_text or 'arbitrat' in clause_text:
                clause_type = 'Dispute Resolution'
            elif 'jurisdiction' in clause_text or 'governing law' in clause_text:
                clause_type = 'Jurisdiction'
            
            analysis = {
                'original_clause': clause,
                'plain_language_explanation': f"This {clause_type.lower()} clause defines specific terms and conditions. Review carefully for any obligations.",
                'clause_type': clause_type,
                'risk_level': risk_level,
                'risk_factors': risk_factors if risk_factors else ['Standard clause with typical terms'],
                'is_favorable': risk_level == 'LOW',
                'unfavorable_aspects': risk_factors if risk_level == 'HIGH' else [],
                'suggested_modifications': ['Review with legal counsel'] if risk_level == 'HIGH' else [],
                'compliance_issues': []
            }
            
            analyzed_clauses.append(analysis)
        
        return analyzed_clauses
    
    def generate_summary(self, text: str, entities: Dict, clause_types: Dict) -> Dict:
        """Generate a comprehensive contract summary"""
        prompt = f"""Generate a comprehensive summary of this contract for an Indian SME owner:

Contract Text (first 3000 characters):
{text[:3000]}

Identified Entities:
- Parties: {entities.get('parties', [])}
- Dates: {entities.get('dates', [])}
- Amounts: {entities.get('amounts', [])}

Provide summary in JSON format:
{{
    "executive_summary": "2-3 paragraph summary in simple language",
    "key_parties": ["list of parties with their roles"],
    "contract_duration": "duration details",
    "key_obligations": {{"party_1": ["obligations"], "party_2": ["obligations"]}},
    "financial_terms": {{"amounts": ["financial details"], "payment_terms": "payment schedule"}},
    "important_dates": ["list of critical dates"],
    "termination_conditions": ["how contract can be ended"],
    "key_risks_for_sme": ["top risks for small business"],
    "recommended_actions": ["what the SME owner should do before signing"]
}}"""
        
        response = self._call_llm(prompt)
        try:
            json_match = response[response.find('{'):response.rfind('}')+1]
            return json.loads(json_match)
        except:
            return {"executive_summary": response, "error": "Could not parse structured summary"}
    
    def identify_unfavorable_terms(self, text: str) -> List[Dict]:
        """Identify terms that are unfavorable to SMEs"""
        prompt = f"""Analyze this contract from the perspective of a small/medium business owner in India.
Identify ALL terms that could be unfavorable or risky.

Contract Text:
{text[:4000]}

For each unfavorable term, provide:
{{
    "unfavorable_terms": [
        {{
            "term_description": "what the problematic term says",
            "risk_category": "financial/legal/operational/reputational",
            "severity": "HIGH/MEDIUM/LOW",
            "why_unfavorable": "explanation for SME owner",
            "potential_consequences": "what could go wrong",
            "suggested_alternative": "better language to propose",
            "negotiation_tip": "how to discuss with the other party"
        }}
    ]
}}"""
        
        response = self._call_llm(prompt)
        try:
            json_match = response[response.find('{'):response.rfind('}')+1]
            return json.loads(json_match).get('unfavorable_terms', [])
        except:
            return [{"term_description": "Analysis completed", "severity": "MEDIUM", "why_unfavorable": "Review recommended"}]
    
    def check_compliance(self, text: str, contract_type: str) -> Dict:
        """Check compliance with Indian laws"""
        prompt = f"""Analyze this {contract_type} for compliance with Indian laws.

Contract Text:
{text[:3000]}

Provide compliance analysis in JSON format:
{{
    "applicable_laws": [{{"law_name": "Name of Indian law", "relevance": "Why this law applies"}}],
    "compliance_status": "COMPLIANT/PARTIALLY_COMPLIANT/NON_COMPLIANT/NEEDS_REVIEW",
    "compliance_issues": [{{"issue": "Description", "severity": "HIGH/MEDIUM/LOW", "recommendation": "How to fix"}}],
    "missing_mandatory_clauses": ["List of clauses that might be legally required"],
    "general_recommendations": ["Overall compliance recommendations"]
}}"""
        
        response = self._call_llm(prompt)
        try:
            json_match = response[response.find('{'):response.rfind('}')+1]
            return json.loads(json_match)
        except:
            return {"compliance_status": "NEEDS_REVIEW", "details": response}
    
    def detect_ambiguities(self, text: str) -> Dict:
        """Detect ambiguous language in the contract"""
        prompt = f"""Identify any ambiguous language or unclear terms in this contract:

Contract Text:
{text[:3000]}

Provide analysis in JSON format:
{{
    "ambiguities": [
        {{
            "ambiguous_text": "the unclear phrase",
            "why_ambiguous": "explanation",
            "possible_interpretations": ["interpretation 1", "interpretation 2"],
            "suggested_clarification": "how to make it clearer"
        }}
    ],
    "overall_clarity_score": "1-10 score"
}}"""
        
        response = self._call_llm(prompt)
        try:
            json_match = response[response.find('{'):response.rfind('}')+1]
            return json.loads(json_match)
        except:
            return {"ambiguities": [], "overall_clarity_score": "5"}