# src/risk_scorer.py

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import json


class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class RiskFactor:
    name: str
    description: str
    level: RiskLevel
    weight: float
    category: str
    mitigation: str


class RiskScorer:
    """
    Calculate risk scores at clause and contract level
    """
    
    def __init__(self):
        self.risk_weights = {
            'penalty': 0.15,
            'indemnity': 0.15,
            'termination': 0.12,
            'arbitration': 0.08,
            'jurisdiction': 0.08,
            'auto_renewal': 0.10,
            'lock_in': 0.10,
            'non_compete': 0.08,
            'ip_transfer': 0.10,
            'confidentiality': 0.04
        }
        
        # Risk indicators and their scores
        self.risk_indicators = {
            # High Risk Patterns
            'unlimited liability': {'score': 0.9, 'level': RiskLevel.CRITICAL},
            'sole discretion': {'score': 0.8, 'level': RiskLevel.HIGH},
            'unilateral termination': {'score': 0.8, 'level': RiskLevel.HIGH},
            'automatic renewal': {'score': 0.7, 'level': RiskLevel.HIGH},
            'waive all claims': {'score': 0.85, 'level': RiskLevel.CRITICAL},
            'irrevocable': {'score': 0.7, 'level': RiskLevel.HIGH},
            'perpetual': {'score': 0.75, 'level': RiskLevel.HIGH},
            
            # Medium Risk Patterns
            'may terminate': {'score': 0.5, 'level': RiskLevel.MEDIUM},
            'liquidated damages': {'score': 0.6, 'level': RiskLevel.MEDIUM},
            'penalty': {'score': 0.6, 'level': RiskLevel.MEDIUM},
            'lock-in period': {'score': 0.5, 'level': RiskLevel.MEDIUM},
            
            # Low Risk Patterns
            'mutual consent': {'score': 0.2, 'level': RiskLevel.LOW},
            'reasonable notice': {'score': 0.2, 'level': RiskLevel.LOW},
            'limited liability': {'score': 0.3, 'level': RiskLevel.LOW},
        }
        
        # Category-specific risk thresholds
        self.category_thresholds = {
            'financial': {'low': 0.3, 'medium': 0.5, 'high': 0.7},
            'legal': {'low': 0.25, 'medium': 0.45, 'high': 0.65},
            'operational': {'low': 0.35, 'medium': 0.55, 'high': 0.75},
            'reputational': {'low': 0.4, 'medium': 0.6, 'high': 0.8}
        }
    
    def calculate_clause_risk(self, clause_analysis: Dict) -> Dict:
        """
        Calculate risk score for a single clause
        """
        risk_score = 0.0
        risk_factors = []
        
        # Get LLM-determined risk level
        llm_risk = clause_analysis.get('risk_level', 'MEDIUM')
        if llm_risk == 'HIGH':
            risk_score += 0.4
        elif llm_risk == 'MEDIUM':
            risk_score += 0.2
        
        # Check for specific risk indicators in clause text
        clause_text = clause_analysis.get('original_clause', {}).get('full_text', '').lower()
        
        for indicator, risk_info in self.risk_indicators.items():
            if indicator in clause_text:
                risk_score += risk_info['score'] * 0.3
                risk_factors.append({
                    'indicator': indicator,
                    'level': risk_info['level'].name,
                    'score_contribution': risk_info['score'] * 0.3
                })
        
        # Check unfavorable aspects
        unfavorable = clause_analysis.get('unfavorable_aspects', [])
        if unfavorable:
            risk_score += len(unfavorable) * 0.05
        
        # Normalize score
        risk_score = min(1.0, risk_score)
        
        # Determine risk level
        if risk_score >= 0.7:
            level = 'HIGH'
            color = '#ff4444'
        elif risk_score >= 0.4:
            level = 'MEDIUM'
            color = '#ffaa00'
        else:
            level = 'LOW'
            color = '#44aa44'
        
        return {
            'score': round(risk_score, 2),
            'level': level,
            'color': color,
            'factors': risk_factors,
            'is_favorable': clause_analysis.get('is_favorable', True)
        }
    
    def calculate_contract_risk(self, analyzed_clauses: List[Dict], 
                                 clause_types: Dict,
                                 unfavorable_terms: List[Dict]) -> Dict:
        """
        Calculate composite risk score for entire contract
        """
        total_weighted_risk = 0.0
        total_weight = 0.0
        category_risks = {
            'financial': [],
            'legal': [],
            'operational': [],
            'reputational': []
        }
        
        # Calculate risk from analyzed clauses
        clause_risks = []
        for clause in analyzed_clauses:
            clause_risk = self.calculate_clause_risk(clause)
            clause_risks.append(clause_risk)
            
            clause_type = clause.get('clause_type', '').lower()
            weight = self.risk_weights.get(clause_type, 0.05)
            
            total_weighted_risk += clause_risk['score'] * weight
            total_weight += weight
        
        # Factor in unfavorable terms
        for term in unfavorable_terms:
            severity = term.get('severity', 'MEDIUM')
            category = term.get('risk_category', 'legal').lower()
            
            if category in category_risks:
                if severity == 'HIGH':
                    category_risks[category].append(0.8)
                elif severity == 'MEDIUM':
                    category_risks[category].append(0.5)
                else:
                    category_risks[category].append(0.2)
        
        # Factor in presence of risky clause types
        risky_clause_penalty = 0.0
        if 'penalty' in clause_types:
            risky_clause_penalty += 0.1
        if 'indemnity' in clause_types:
            risky_clause_penalty += 0.1
        if 'auto_renewal' in clause_types:
            risky_clause_penalty += 0.08
        if 'lock_in' in clause_types:
            risky_clause_penalty += 0.08
        if 'non_compete' in clause_types:
            risky_clause_penalty += 0.08
        
        # Calculate final composite score
        if total_weight > 0:
            composite_score = (total_weighted_risk / total_weight) + risky_clause_penalty
        else:
            composite_score = 0.3 + risky_clause_penalty  # Default medium risk
        
        composite_score = min(1.0, composite_score)
        
        # Calculate category-wise risks
        category_scores = {}
        for category, risks in category_risks.items():
            if risks:
                avg_risk = sum(risks) / len(risks)
                category_scores[category] = {
                    'score': round(avg_risk, 2),
                    'level': self._get_category_level(category, avg_risk),
                    'issue_count': len(risks)
                }
            else:
                category_scores[category] = {
                    'score': 0.0,
                    'level': 'LOW',
                    'issue_count': 0
                }
        
        # Determine overall risk level
        if composite_score >= 0.7:
            overall_level = 'HIGH'
            recommendation = 'High Risk - Strongly recommend legal review before signing'
            color = '#ff4444'
        elif composite_score >= 0.4:
            overall_level = 'MEDIUM'
            recommendation = 'Medium Risk - Review highlighted concerns and consider negotiation'
            color = '#ffaa00'
        else:
            overall_level = 'LOW'
            recommendation = 'Low Risk - Generally favorable terms, minor review suggested'
            color = '#44aa44'
        
        return {
            'composite_score': round(composite_score * 100, 1),  # As percentage
            'overall_level': overall_level,
            'color': color,
            'recommendation': recommendation,
            'clause_risks': clause_risks,
            'category_scores': category_scores,
            'high_risk_count': len([c for c in clause_risks if c['level'] == 'HIGH']),
            'medium_risk_count': len([c for c in clause_risks if c['level'] == 'MEDIUM']),
            'low_risk_count': len([c for c in clause_risks if c['level'] == 'LOW']),
            'risk_breakdown': {
                'clause_based': round(total_weighted_risk / max(total_weight, 0.1), 2),
                'clause_type_penalty': round(risky_clause_penalty, 2),
                'unfavorable_terms_impact': len(unfavorable_terms)
            }
        }
    
    def _get_category_level(self, category: str, score: float) -> str:
        """Determine risk level based on category thresholds"""
        thresholds = self.category_thresholds.get(category, 
                                                   {'low': 0.3, 'medium': 0.5, 'high': 0.7})
        
        if score >= thresholds['high']:
            return 'HIGH'
        elif score >= thresholds['medium']:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def generate_risk_mitigation_strategies(self, contract_risk: Dict, 
                                            unfavorable_terms: List[Dict]) -> List[Dict]:
        """
        Generate risk mitigation strategies
        """
        strategies = []
        
        # Based on overall risk level
        if contract_risk['overall_level'] == 'HIGH':
            strategies.append({
                'priority': 'CRITICAL',
                'action': 'Engage Legal Counsel',
                'description': 'Given the high-risk nature of this contract, it is strongly recommended to consult with a qualified legal professional before signing.',
                'timeline': 'Before signing'
            })
        
        # Based on category risks
        for category, data in contract_risk['category_scores'].items():
            if data['level'] == 'HIGH':
                if category == 'financial':
                    strategies.append({
                        'priority': 'HIGH',
                        'action': 'Review Financial Terms',
                        'description': 'Carefully review all financial obligations, payment terms, penalties, and liability caps. Consider negotiating limits on financial exposure.',
                        'timeline': 'Before signing'
                    })
                elif category == 'legal':
                    strategies.append({
                        'priority': 'HIGH',
                        'action': 'Legal Review Required',
                        'description': 'Multiple legal risk factors identified. Review jurisdiction, dispute resolution, and compliance clauses carefully.',
                        'timeline': 'Before signing'
                    })
                elif category == 'operational':
                    strategies.append({
                        'priority': 'MEDIUM',
                        'action': 'Operational Impact Assessment',
                        'description': 'Assess how contract terms will affect your daily operations, deliverables, and resource allocation.',
                        'timeline': 'Before signing'
                    })
        
        # Based on specific unfavorable terms
        for term in unfavorable_terms[:5]:  # Top 5 issues
            strategies.append({
                'priority': term.get('severity', 'MEDIUM'),
                'action': f"Address: {term.get('term_description', 'Unfavorable term')[:50]}...",
                'description': term.get('negotiation_tip', 'Consider negotiating this term'),
                'suggested_alternative': term.get('suggested_alternative', 'N/A'),
                'timeline': 'During negotiation'
            })
        
        return strategies