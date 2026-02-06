import streamlit as st
import os
import re
import json
import tempfile
from datetime import datetime, timedelta
from collections import defaultdict
import random

# ============== PAGE CONFIG ==============
st.set_page_config(
    page_title="ContractShield AI - Smart Contract Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== SESSION STATE ==============
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None
if 'contract_text' not in st.session_state:
    st.session_state.contract_text = None

# ============== THEME CSS ==============
def get_theme_css():
    if st.session_state.theme == 'dark':
        return """
        <style>
            .stApp {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: #eee;
            }
            .main-header {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 3rem;
                font-weight: 800;
                text-align: center;
                padding: 20px;
                animation: glow 2s ease-in-out infinite alternate;
            }
            @keyframes glow {
                from { text-shadow: 0 0 5px #667eea; }
                to { text-shadow: 0 0 20px #764ba2; }
            }
            .glass-card {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 25px;
                border: 1px solid rgba(255,255,255,0.2);
                margin: 15px 0;
            }
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                color: white;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            }
            .risk-high {
                background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
                padding: 20px;
                border-radius: 15px;
                margin: 10px 0;
                animation: pulse-red 2s infinite;
            }
            @keyframes pulse-red {
                0%, 100% { box-shadow: 0 0 0 0 rgba(255, 65, 108, 0.7); }
                50% { box-shadow: 0 0 0 15px rgba(255, 65, 108, 0); }
            }
            .risk-medium {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 20px;
                border-radius: 15px;
                margin: 10px 0;
            }
            .risk-low {
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                padding: 20px;
                border-radius: 15px;
                margin: 10px 0;
            }
            .health-score {
                font-size: 5rem;
                font-weight: 900;
                text-align: center;
            }
            .grade-A { color: #38ef7d; }
            .grade-B { color: #11998e; }
            .grade-C { color: #f5af19; }
            .grade-D { color: #f093fb; }
            .grade-F { color: #ff416c; }
        </style>
        """
    else:
        return """
        <style>
            .stApp {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }
            .main-header {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 3rem;
                font-weight: 800;
                text-align: center;
                padding: 20px;
            }
            .glass-card {
                background: rgba(255,255,255,0.8);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 25px;
                border: 1px solid rgba(0,0,0,0.1);
                margin: 15px 0;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                color: white;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            }
            .risk-high {
                background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
                color: white;
                padding: 20px;
                border-radius: 15px;
                margin: 10px 0;
                animation: pulse-red 2s infinite;
            }
            @keyframes pulse-red {
                0%, 100% { box-shadow: 0 0 0 0 rgba(255, 65, 108, 0.7); }
                50% { box-shadow: 0 0 0 15px rgba(255, 65, 108, 0); }
            }
            .risk-medium {
                background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
                color: white;
                padding: 20px;
                border-radius: 15px;
                margin: 10px 0;
            }
            .risk-low {
                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                color: white;
                padding: 20px;
                border-radius: 15px;
                margin: 10px 0;
            }
            .health-score {
                font-size: 5rem;
                font-weight: 900;
                text-align: center;
            }
            .grade-A { color: #38ef7d; }
            .grade-B { color: #11998e; }
            .grade-C { color: #f5af19; }
            .grade-D { color: #f093fb; }
            .grade-F { color: #ff416c; }
            .timeline-item {
                background: white;
                padding: 15px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 4px solid #667eea;
            }
            .balance-bar {
                height: 30px;
                border-radius: 15px;
                background: linear-gradient(90deg, #38ef7d 0%, #f5af19 50%, #ff416c 100%);
            }
            .stButton>button {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 1.1rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .stButton>button:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            }
        </style>
        """

st.markdown(get_theme_css(), unsafe_allow_html=True)

# ============== HELPER FUNCTIONS ==============

def read_file(uploaded_file):
    """Read uploaded file content"""
    try:
        if uploaded_file.name.endswith('.txt'):
            return uploaded_file.read().decode('utf-8')
        elif uploaded_file.name.endswith('.pdf'):
            try:
                import pdfplumber
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                text = ""
                with pdfplumber.open(tmp_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                os.unlink(tmp_path)
                return text
            except:
                return uploaded_file.read().decode('utf-8', errors='ignore')
        elif uploaded_file.name.endswith('.docx'):
            try:
                from docx import Document
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                doc = Document(tmp_path)
                text = "\n".join([para.text for para in doc.paragraphs])
                os.unlink(tmp_path)
                return text
            except:
                return "Error reading DOCX file"
        else:
            return uploaded_file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f"Error: {e}"


def classify_contract(text):
    """Classify contract type with confidence"""
    text_lower = text.lower()
    
    scores = {
        'Employment Agreement': 0,
        'Vendor Contract': 0,
        'Service Agreement': 0,
        'Lease Agreement': 0,
        'Partnership Deed': 0,
        'NDA': 0
    }
    
    # Employment
    for word in ['employee', 'employer', 'salary', 'employment', 'probation', 'designation', 'appraisal']:
        if word in text_lower:
            scores['Employment Agreement'] += 1
    
    # Vendor
    for word in ['vendor', 'supplier', 'supply', 'purchase order', 'delivery', 'goods']:
        if word in text_lower:
            scores['Vendor Contract'] += 1
    
    # Service
    for word in ['service', 'services', 'consultant', 'consulting', 'deliverables', 'milestone']:
        if word in text_lower:
            scores['Service Agreement'] += 1
    
    # Lease
    for word in ['lease', 'rent', 'tenant', 'landlord', 'premises', 'property']:
        if word in text_lower:
            scores['Lease Agreement'] += 1
    
    # Partnership
    for word in ['partner', 'partnership', 'profit sharing', 'capital contribution']:
        if word in text_lower:
            scores['Partnership Deed'] += 1
    
    # NDA
    for word in ['confidential', 'non-disclosure', 'nda', 'proprietary', 'trade secret']:
        if word in text_lower:
            scores['NDA'] += 1
    
    best_match = max(scores, key=scores.get)
    confidence = min(100, scores[best_match] * 15)
    
    return best_match, confidence


def extract_entities(text):
    """Extract key entities"""
    entities = {'parties': [], 'dates': [], 'amounts': [], 'durations': []}
    
    # Dates
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities['dates'].extend(matches[:5])
    
    # Amounts
    amount_patterns = [
        r'(?:INR|Rs\.?|₹)\s*[\d,]+(?:\.\d{2})?',
        r'[\d,]+(?:\.\d{2})?\s*(?:rupees|lakhs?|crores?)',
    ]
    for pattern in amount_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities['amounts'].extend(matches[:5])
    
    # Durations
    duration_patterns = [
        r'\d+\s*(?:days?|weeks?|months?|years?)',
    ]
    for pattern in duration_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities['durations'].extend(matches[:5])
    
    return entities


def analyze_clauses_with_grades(text):
    """Analyze clauses and assign grades"""
    clauses = []
    
    clause_definitions = {
        'Termination': {
            'keywords': ['terminat', 'cancel', 'end of agreement'],
            'good_indicators': ['mutual', 'notice period', '30 days', '60 days'],
            'bad_indicators': ['immediate', 'without cause', 'sole discretion']
        },
        'Payment': {
            'keywords': ['payment', 'salary', 'compensation', 'fee', 'amount'],
            'good_indicators': ['within 30 days', 'on time', 'interest on delay'],
            'bad_indicators': ['delayed', 'at discretion', 'no interest']
        },
        'Confidentiality': {
            'keywords': ['confidential', 'non-disclosure', 'proprietary'],
            'good_indicators': ['mutual', 'reasonable', 'limited period'],
            'bad_indicators': ['perpetual', 'unlimited', 'all information']
        },
        'Indemnification': {
            'keywords': ['indemnif', 'hold harmless'],
            'good_indicators': ['mutual', 'capped', 'limited'],
            'bad_indicators': ['unlimited', 'sole', 'all claims']
        },
        'Non-Compete': {
            'keywords': ['non-compete', 'non compete', 'not engage', 'competitive'],
            'good_indicators': ['6 months', 'limited area', 'specific industry'],
            'bad_indicators': ['perpetual', '2 years', 'worldwide', '12 months']
        },
        'Intellectual Property': {
            'keywords': ['intellectual property', 'ip', 'copyright', 'patent'],
            'good_indicators': ['license', 'limited', 'specific work'],
            'bad_indicators': ['all rights', 'perpetual', 'irrevocable', 'assign']
        },
        'Dispute Resolution': {
            'keywords': ['dispute', 'arbitrat', 'mediat', 'jurisdiction'],
            'good_indicators': ['mediation first', 'neutral', 'mutual'],
            'bad_indicators': ['sole jurisdiction', 'binding', 'their choice']
        },
        'Liability': {
            'keywords': ['liability', 'liable', 'damages'],
            'good_indicators': ['limited', 'capped', 'mutual'],
            'bad_indicators': ['unlimited', 'consequential', 'all damages']
        }
    }
    
    sections = re.split(r'\n\s*\d+[\.\)]\s+', text)
    
    for i, section in enumerate(sections):
        if len(section.strip()) < 30:
            continue
        
        section_lower = section.lower()
        
        # Find clause type
        clause_type = 'General'
        for ctype, info in clause_definitions.items():
            for keyword in info['keywords']:
                if keyword in section_lower:
                    clause_type = ctype
                    break
            if clause_type != 'General':
                break
        
        # Calculate grade
        good_score = 0
        bad_score = 0
        
        if clause_type in clause_definitions:
            for indicator in clause_definitions[clause_type]['good_indicators']:
                if indicator in section_lower:
                    good_score += 1
            for indicator in clause_definitions[clause_type]['bad_indicators']:
                if indicator in section_lower:
                    bad_score += 1
        
        # Assign grade
        net_score = good_score - bad_score
        if net_score >= 2:
            grade = 'A'
            risk_level = 'LOW'
        elif net_score >= 1:
            grade = 'B'
            risk_level = 'LOW'
        elif net_score >= 0:
            grade = 'C'
            risk_level = 'MEDIUM'
        elif net_score >= -1:
            grade = 'D'
            risk_level = 'MEDIUM'
        else:
            grade = 'F'
            risk_level = 'HIGH'
        
        clauses.append({
            'number': i,
            'type': clause_type,
            'text': section[:400],
            'grade': grade,
            'risk_level': risk_level,
            'good_points': good_score,
            'bad_points': bad_score
        })
    
    return clauses[:15]


def calculate_health_score(clauses, unfavorable_terms):
    """Calculate contract health score like credit score"""
    base_score = 750  # Start with good score
    
    # Deduct for bad grades
    for clause in clauses:
        if clause['grade'] == 'F':
            base_score -= 50
        elif clause['grade'] == 'D':
            base_score -= 30
        elif clause['grade'] == 'C':
            base_score -= 10
    
    # Deduct for unfavorable terms
    for term in unfavorable_terms:
        if term['severity'] == 'HIGH':
            base_score -= 40
        elif term['severity'] == 'MEDIUM':
            base_score -= 20
    
    # Normalize to 300-850 range
    score = max(300, min(850, base_score))
    
    if score >= 750:
        rating = 'Excellent'
        color = '#38ef7d'
    elif score >= 650:
        rating = 'Good'
        color = '#11998e'
    elif score >= 550:
        rating = 'Fair'
        color = '#f5af19'
    elif score >= 450:
        rating = 'Poor'
        color = '#f093fb'
    else:
        rating = 'Very Poor'
        color = '#ff416c'
    
    return score, rating, color


def calculate_balance_score(text):
    """Calculate how balanced the contract is between parties"""
    text_lower = text.lower()
    
    # Indicators favoring other party
    other_party_favor = 0
    your_favor = 0
    
    # Check for one-sided terms
    if 'sole discretion' in text_lower:
        other_party_favor += 2
    if 'unilateral' in text_lower:
        other_party_favor += 2
    if 'at any time' in text_lower and 'terminat' in text_lower:
        other_party_favor += 1
    if 'waive' in text_lower:
        other_party_favor += 1
    if 'unlimited liability' in text_lower:
        other_party_favor += 2
    if 'indemnify' in text_lower and 'hold harmless' in text_lower:
        other_party_favor += 1
    
    # Check for balanced/favorable terms
    if 'mutual' in text_lower:
        your_favor += 2
    if 'reasonable' in text_lower:
        your_favor += 1
    if 'consent' in text_lower:
        your_favor += 1
    if 'limitation of liability' in text_lower:
        your_favor += 1
    if 'notice period' in text_lower:
        your_favor += 1
    
    total = other_party_favor + your_favor + 1
    balance = 50 + ((your_favor - other_party_favor) / total) * 50
    balance = max(0, min(100, balance))
    
    return balance


def get_unfavorable_terms(text):
    """Identify unfavorable terms with negotiation scripts"""
    text_lower = text.lower()
    unfavorable = []
    
    checks = [
        {
            'pattern': 'non-compete',
            'title': '🚫 Non-Compete Clause',
            'severity': 'HIGH',
            'why': 'Restricts your future employment/business opportunities',
            'suggestion': 'Negotiate shorter duration (6 months max) and limited geography',
            'negotiation_script': '"I understand the need to protect business interests, but a 12-month non-compete is quite restrictive. Could we reduce this to 6 months and limit it to direct competitors in the same city?"'
        },
        {
            'pattern': 'indemnif',
            'title': '⚠️ Indemnification Clause',
            'severity': 'HIGH',
            'why': 'May require you to pay for damages beyond your control',
            'suggestion': 'Request mutual indemnification with a cap',
            'negotiation_script': '"I\'m comfortable with reasonable indemnification, but I\'d like it to be mutual and capped at the contract value. This protects both parties equally."'
        },
        {
            'pattern': 'sole discretion',
            'title': '🎯 Sole Discretion Rights',
            'severity': 'HIGH',
            'why': 'Other party can make decisions without your consent',
            'suggestion': 'Replace with "mutual agreement" or add objective criteria',
            'negotiation_script': '"The \'sole discretion\' language concerns me. Can we change this to \'mutual agreement\' or at least add specific criteria for decision-making?"'
        },
        {
            'pattern': 'automatic renewal',
            'title': '🔄 Automatic Renewal',
            'severity': 'MEDIUM',
            'why': 'Contract renews without explicit consent',
            'suggestion': 'Add requirement for written confirmation before renewal',
            'negotiation_script': '"I\'d prefer if renewal required written confirmation from both parties. This ensures we both actively want to continue."'
        },
        {
            'pattern': 'penalty',
            'title': '💰 Penalty Clause',
            'severity': 'MEDIUM',
            'why': 'Financial penalties for non-performance',
            'suggestion': 'Ensure penalties are proportional to actual damages',
            'negotiation_script': '"The penalty amount seems high. Can we tie it to actual damages incurred, with a reasonable cap?"'
        },
        {
            'pattern': 'unlimited liability',
            'title': '💸 Unlimited Liability',
            'severity': 'HIGH',
            'why': 'No cap on damages you may have to pay',
            'suggestion': 'Add liability cap equal to contract value',
            'negotiation_script': '"Unlimited liability is a significant risk. Industry standard is to cap liability at the contract value. Can we add that limit?"'
        },
        {
            'pattern': 'waive',
            'title': '📝 Waiver of Rights',
            'severity': 'HIGH',
            'why': 'You may be giving up important legal rights',
            'suggestion': 'Remove or limit scope of waiver',
            'negotiation_script': '"I\'m not comfortable waiving all rights. Can we be specific about what\'s being waived and why?"'
        },
        {
            'pattern': 'perpetual',
            'title': '♾️ Perpetual Terms',
            'severity': 'HIGH',
            'why': 'Creates permanent, never-ending obligations',
            'suggestion': 'Request fixed term with renewal options',
            'negotiation_script': '"Perpetual obligations are concerning. Can we change this to a fixed term, say 5 years, with the option to renew?"'
        },
        {
            'pattern': 'immediate termination',
            'title': '⚡ Immediate Termination',
            'severity': 'MEDIUM',
            'why': 'Contract can be ended without notice',
            'suggestion': 'Add minimum notice period even for cause',
            'negotiation_script': '"Even in case of breach, a short notice period helps transition smoothly. Can we add at least 15 days notice?"'
        },
        {
            'pattern': 'arbitration',
            'title': '⚖️ Mandatory Arbitration',
            'severity': 'MEDIUM',
            'why': 'Limits your legal options in disputes',
            'suggestion': 'Ensure neutral arbitrator selection process',
            'negotiation_script': '"I\'m okay with arbitration, but can we ensure the arbitrator is mutually agreed upon and the venue is convenient for both parties?"'
        }
    ]
    
    for check in checks:
        if check['pattern'] in text_lower:
            unfavorable.append(check)
    
    return unfavorable


def generate_timeline(entities, text):
    """Generate timeline of important dates"""
    timeline = []
    
    # Contract start (assumed)
    timeline.append({
        'date': 'Contract Execution',
        'event': 'Agreement signed by both parties',
        'icon': '📝'
    })
    
    # Check for specific periods
    text_lower = text.lower()
    
    if 'probation' in text_lower:
        match = re.search(r'probation.*?(\d+)\s*(?:month|day|week)', text_lower)
        if match:
            timeline.append({
                'date': f'{match.group(1)} months/days',
                'event': 'Probation period ends',
                'icon': '✅'
            })
    
    if 'notice' in text_lower:
        match = re.search(r'(\d+)\s*(?:days?|months?)\s*(?:written\s*)?notice', text_lower)
        if match:
            timeline.append({
                'date': f'{match.group(1)} days notice required',
                'event': 'For termination',
                'icon': '⏰'
            })
    
    if 'renew' in text_lower:
        timeline.append({
            'date': 'Before contract end',
            'event': 'Renewal decision needed',
            'icon': '🔄'
        })
    
    # Add any extracted dates
    for date in entities.get('dates', [])[:3]:
        timeline.append({
            'date': date,
            'event': 'Important date mentioned',
            'icon': '📅'
        })
    
    return timeline


def translate_to_hindi(text):
    """Simple translation of key terms to Hindi"""
    translations = {
        'agreement': 'समझौता',
        'contract': 'अनुबंध',
        'party': 'पक्ष',
        'employer': 'नियोक्ता',
        'employee': 'कर्मचारी',
        'salary': 'वेतन',
        'termination': 'समाप्ति',
        'confidential': 'गोपनीय',
        'liability': 'दायित्व',
        'payment': 'भुगतान',
        'risk': 'जोखिम',
        'high': 'उच्च',
        'medium': 'मध्यम',
        'low': 'कम',
        'penalty': 'जुर्माना',
        'notice': 'सूचना',
        'days': 'दिन',
        'months': 'महीने',
        'years': 'वर्ष'
    }
    
    result = text
    for eng, hindi in translations.items():
        result = re.sub(rf'\b{eng}\b', f'{eng} ({hindi})', result, flags=re.IGNORECASE)
    
    return result


def get_industry_benchmark(contract_type):
    """Get industry standard benchmarks"""
    benchmarks = {
        'Employment Agreement': {
            'notice_period': '30-90 days',
            'probation': '3-6 months',
            'non_compete': '6-12 months',
            'confidentiality': '2-5 years after exit'
        },
        'Vendor Contract': {
            'payment_terms': '30-45 days',
            'warranty': '12-24 months',
            'liability_cap': '100% of contract value',
            'termination_notice': '30 days'
        },
        'Service Agreement': {
            'payment_terms': '15-30 days',
            'liability_cap': '100-200% of fees',
            'ip_ownership': 'Client owns deliverables',
            'termination_notice': '30 days'
        },
        'Lease Agreement': {
            'lock_in': '11-24 months',
            'notice_period': '1-3 months',
            'security_deposit': '2-6 months rent',
            'rent_escalation': '5-10% annually'
        }
    }
    
    return benchmarks.get(contract_type, benchmarks['Service Agreement'])


# ============== MAIN APP ==============

def main():
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Theme toggle
        theme_col1, theme_col2 = st.columns(2)
        with theme_col1:
            if st.button("☀️ Light", use_container_width=True):
                st.session_state.theme = 'light'
                st.rerun()
        with theme_col2:
            if st.button("🌙 Dark", use_container_width=True):
                st.session_state.theme = 'dark'
                st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 🏆 Features")
        st.markdown("""
        - 🎯 Health Score (Like Credit Score)
        - 📊 Risk Heatmap
        - 🔴 Red Flag Alerts
        - 📅 Timeline Visualizer
        - ⚖️ Balance Meter
        - 🏆 Clause Grading (A-F)
        - 💬 Negotiation Scripts
        - 🇮🇳 Hindi Translation
        - 📈 Industry Benchmarks
        """)
        
        st.markdown("---")
        st.markdown("### 🆓 100% FREE")
        st.markdown("No API keys needed!")
    
    # Header
    st.markdown('<h1 class="main-header">🛡️ ContractShield AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.3rem; color: #667eea;">Smart Contract Analysis for Indian SMEs</p>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Upload & Analyze", 
        "📊 Dashboard", 
        "💬 Negotiation Helper",
        "📋 Templates",
        "❓ Help"
    ])
    
    # ============== TAB 1: Upload ==============
    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📁 Upload Your Contract")
            uploaded_file = st.file_uploader(
                "Drag and drop or click to upload",
                type=['txt', 'pdf', 'docx'],
                help="Supported formats: TXT, PDF, DOCX (Max 10MB)"
            )
        
        with col2:
            st.markdown("### 📋 Supported")
            st.markdown("""
            - 📄 PDF files
            - 📝 DOCX files
            - 📃 TXT files
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file:
            st.success(f"✅ **{uploaded_file.name}** uploaded successfully!")
            
            if st.button("🔍 Analyze Contract", type="primary", use_container_width=True):
                
                with st.spinner("🔍 Analyzing your contract..."):
                    progress = st.progress(0)
                    
                    # Read file
                    progress.progress(10, "📄 Reading document...")
                    text = read_file(uploaded_file)
                    st.session_state.contract_text = text
                    
                    if text.startswith("Error"):
                        st.error(text)
                        return
                    
                    # Classify
                    progress.progress(25, "📋 Classifying contract...")
                    contract_type, confidence = classify_contract(text)
                    
                    # Entities
                    progress.progress(40, "🔍 Extracting information...")
                    entities = extract_entities(text)
                    
                    # Clauses
                    progress.progress(55, "📝 Grading clauses...")
                    clauses = analyze_clauses_with_grades(text)
                    
                    # Unfavorable terms
                    progress.progress(70, "⚠️ Finding risks...")
                    unfavorable = get_unfavorable_terms(text)
                    
                    # Health Score
                    progress.progress(85, "🎯 Calculating health score...")
                    health_score, health_rating, health_color = calculate_health_score(clauses, unfavorable)
                    
                    # Balance Score
                    progress.progress(90, "⚖️ Checking balance...")
                    balance_score = calculate_balance_score(text)
                    
                    # Timeline
                    progress.progress(95, "📅 Creating timeline...")
                    timeline = generate_timeline(entities, text)
                    
                    # Benchmarks
                    benchmarks = get_industry_benchmark(contract_type)
                    
                    progress.progress(100, "✅ Complete!")
                    
                    # Store results
                    st.session_state.analysis_data = {
                        'contract_type': contract_type,
                        'confidence': confidence,
                        'entities': entities,
                        'clauses': clauses,
                        'unfavorable': unfavorable,
                        'health_score': health_score,
                        'health_rating': health_rating,
                        'health_color': health_color,
                        'balance_score': balance_score,
                        'timeline': timeline,
                        'benchmarks': benchmarks,
                        'file_name': uploaded_file.name
                    }
                    st.session_state.analysis_done = True
                
                st.balloons()
                st.success("✅ Analysis complete! Check the **Dashboard** tab for results.")
    
    # ============== TAB 2: Dashboard ==============
    with tab2:
        if not st.session_state.analysis_done:
            st.info("👆 Please upload and analyze a contract first!")
        else:
            data = st.session_state.analysis_data
            
            # Health Score Card - Unique Feature!
            st.markdown("### 🎯 Contract Health Score")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown(f"""
                <div class="glass-card" style="text-align: center;">
                    <h2 style="color: {data['health_color']}; font-size: 6rem; margin: 0;">{data['health_score']}</h2>
                    <h3 style="color: {data['health_color']};">{data['health_rating']}</h3>
                    <p>Like a credit score for your contract! (300-850)</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📋 Type</h3>
                    <h2>{data['contract_type']}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                high_risk = len([c for c in data['clauses'] if c['risk_level'] == 'HIGH'])
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🔴 High Risk</h3>
                    <h2>{high_risk}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>⚠️ Red Flags</h3>
                    <h2>{len(data['unfavorable'])}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                avg_grade_score = sum([ord('F') - ord(c['grade']) for c in data['clauses']]) / max(len(data['clauses']), 1)
                avg_grade = chr(ord('F') - int(avg_grade_score))
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📊 Avg Grade</h3>
                    <h2>{avg_grade}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Balance Meter - Unique Feature!
            st.markdown("### ⚖️ Contract Balance Meter")
            st.markdown("*Shows if the contract favors you or the other party*")
            
            balance = data['balance_score']
            
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.markdown("**Other Party**")
            with col2:
                st.progress(balance / 100)
                if balance < 35:
                    st.error(f"⚠️ Contract heavily favors the other party ({balance:.0f}%)")
                elif balance < 50:
                    st.warning(f"🟡 Slightly favors other party ({balance:.0f}%)")
                elif balance < 65:
                    st.success(f"✅ Fairly balanced ({balance:.0f}%)")
                else:
                    st.success(f"🎉 Favorable to you ({balance:.0f}%)")
            with col3:
                st.markdown("**You**")
            
            st.markdown("---")
            
            # Timeline - Unique Feature!
            st.markdown("### 📅 Contract Timeline")
            
            for item in data['timeline']:
                st.markdown(f"""
                <div class="timeline-item">
                    <strong>{item['icon']} {item['date']}</strong><br>
                    {item['event']}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Red Flag Alerts - Unique Feature!
            if data['unfavorable']:
                st.markdown("### 🚨 Red Flag Alerts")
                
                for term in data['unfavorable']:
                    severity_class = 'risk-high' if term['severity'] == 'HIGH' else 'risk-medium'
                    st.markdown(f"""
                    <div class="{severity_class}">
                        <strong>{term['title']}</strong><br>
                        ⚠️ {term['why']}<br>
                        💡 <em>{term['suggestion']}</em>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Clause Grades - Unique Feature!
            st.markdown("### 🏆 Clause Report Card")
            
            for clause in data['clauses']:
                grade = clause['grade']
                grade_class = f"grade-{grade}"
                
                with st.expander(f"{clause['type']} - Grade: {grade}"):
                    col1, col2, col3 = st.columns([1, 1, 2])
                    
                    with col1:
                        st.markdown(f"<h1 class='{grade_class}'>{grade}</h1>", unsafe_allow_html=True)
                    
                    with col2:
                        st.metric("Good Points", clause['good_points'])
                        st.metric("Bad Points", clause['bad_points'])
                    
                    with col3:
                        st.markdown("**Preview:**")
                        st.text(clause['text'][:200] + "...")
            
            st.markdown("---")
            
            # Industry Benchmarks - Unique Feature!
            st.markdown("### 📈 Industry Benchmarks")
            st.markdown(f"*Standard terms for {data['contract_type']}*")
            
            for key, value in data['benchmarks'].items():
                st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
            
            st.markdown("---")
            
            # Hindi Translation Toggle - Unique Feature!
            st.markdown("### 🇮🇳 Hindi Summary")
            
            if st.button("🔄 Show Hindi Translation", use_container_width=True):
                summary = f"""
                Contract Type: {data['contract_type']}
                Health Score: {data['health_score']} ({data['health_rating']})
                Risk Flags: {len(data['unfavorable'])}
                Balance: {data['balance_score']:.0f}%
                """
                hindi_summary = translate_to_hindi(summary)
                st.markdown(f"""
                <div class="glass-card">
                    <h4>🇮🇳 हिंदी सारांश (Hindi Summary)</h4>
                    <pre>{hindi_summary}</pre>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Download Report
            st.markdown("### 📥 Download Report")
            
            report = {
                'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'file_name': data['file_name'],
                'contract_type': data['contract_type'],
                'health_score': data['health_score'],
                'health_rating': data['health_rating'],
                'balance_score': data['balance_score'],
                'red_flags': len(data['unfavorable']),
                'clauses_analyzed': len(data['clauses']),
                'unfavorable_terms': [t['title'] for t in data['unfavorable']],
                'benchmarks': data['benchmarks']
            }
            
            st.download_button(
                "📥 Download Full Report (JSON)",
                json.dumps(report, indent=2),
                file_name=f"contract_report_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    # ============== TAB 3: Negotiation Helper ==============
    with tab3:
        st.markdown("### 💬 Negotiation Script Generator")
        st.markdown("*Ready-to-use scripts to negotiate better terms*")
        
        if st.session_state.analysis_done and st.session_state.analysis_data['unfavorable']:
            for term in st.session_state.analysis_data['unfavorable']:
                with st.expander(f"🎯 {term['title']}"):
                    st.markdown("**The Issue:**")
                    st.warning(term['why'])
                    
                    st.markdown("**What to Say:**")
                    st.success(term['negotiation_script'])
                    
                    st.markdown("**Expected Outcome:**")
                    st.info(term['suggestion'])
        else:
            st.info("👆 Analyze a contract first to get personalized negotiation scripts!")
            
            # Show sample scripts
            st.markdown("### 📚 Sample Negotiation Scripts")
            
            samples = [
                {
                    'issue': 'Non-Compete Clause',
                    'script': '"I appreciate the need to protect your business, but a 12-month non-compete covering all industries seems broad. Could we limit this to 6 months for direct competitors in the same city?"'
                },
                {
                    'issue': 'Payment Terms',
                    'script': '"Net 60 payment terms create cash flow challenges for us. Would you consider Net 30, or perhaps 50% upfront with the balance on completion?"'
                },
                {
                    'issue': 'Liability Cap',
                    'script': '"Unlimited liability exposure is a significant risk for a small business like ours. Industry standard is to cap liability at the contract value. Can we add that protection?"'
                }
            ]
            
            for sample in samples:
                with st.expander(f"💬 {sample['issue']}"):
                    st.success(sample['script'])
    
    # ============== TAB 4: Templates ==============
    with tab4:
        st.markdown("### 📋 SME-Friendly Contract Templates")
        
        templates = {
            "✍️ Employment Agreement": """
EMPLOYMENT AGREEMENT

Date: [DATE]
Between: [COMPANY NAME] ("Employer")
And: [EMPLOYEE NAME] ("Employee")

1. POSITION: [JOB TITLE]
2. START DATE: [DATE]
3. COMPENSATION: INR [AMOUNT] per month
4. WORKING HOURS: [X] hours per week
5. PROBATION: [X] months
6. NOTICE PERIOD: [X] days (mutual)
7. CONFIDENTIALITY: During employment and 2 years after
8. GOVERNING LAW: Laws of India, Courts of [CITY]

Signed by both parties.
            """,
            "🤝 Service Agreement": """
SERVICE AGREEMENT

Date: [DATE]
Between: [CLIENT NAME] ("Client")
And: [PROVIDER NAME] ("Provider")

1. SERVICES: [DESCRIPTION]
2. DURATION: [START] to [END]
3. FEES: INR [AMOUNT]
4. PAYMENT: Within 30 days of invoice
5. DELIVERABLES: As per Annexure A
6. IP RIGHTS: Client owns all deliverables upon payment
7. TERMINATION: 30 days written notice by either party
8. LIABILITY CAP: Limited to fees paid

Signed by both parties.
            """,
            "📦 Vendor Contract": """
VENDOR AGREEMENT

Date: [DATE]
Between: [BUYER] ("Buyer")
And: [VENDOR] ("Vendor")

1. GOODS/SERVICES: [DESCRIPTION]
2. QUANTITY: [AMOUNT]
3. PRICE: INR [AMOUNT] + GST
4. DELIVERY: Within [X] days
5. PAYMENT: Within 30 days of delivery
6. WARRANTY: [X] months
7. QUALITY: As per specifications in Annexure
8. RETURNS: Defective goods replaced within 15 days

Signed by both parties.
            """
        }
        
        for name, content in templates.items():
            with st.expander(name):
                st.code(content, language="text")
                st.download_button(
                    f"📥 Download Template",
                    content,
                    file_name=f"{name.split()[1].lower()}_template.txt",
                    mime="text/plain",
                    key=name
                )
    
    # ============== TAB 5: Help ==============
    with tab5:
        st.markdown("### ❓ How to Use ContractShield AI")
        
        st.markdown("""
        #### 🚀 Quick Start
        
        1. **Upload** your contract (PDF, DOCX, or TXT)
        2. Click **Analyze Contract**
        3. Check your **Health Score** in Dashboard
        4. Review **Red Flags** and **Clause Grades**
        5. Use **Negotiation Scripts** to improve terms
        
        ---
        
        #### 🎯 Understanding Health Score
        
        | Score | Rating | Meaning |
        |-------|--------|---------|
        | 750+ | Excellent | Safe to sign |
        | 650-749 | Good | Minor concerns |
        | 550-649 | Fair | Review needed |
        | 450-549 | Poor | Negotiate terms |
        | Below 450 | Very Poor | Legal review required |
        
        ---
        
        #### 🏆 Understanding Clause Grades
        
        | Grade | Meaning |
        |-------|---------|
        | A | Excellent - Very favorable |
        | B | Good - Favorable terms |
        | C | Average - Standard terms |
        | D | Below Average - Some concerns |
        | F | Failing - Unfavorable, needs change |
        
        ---
        
        #### ⚖️ Understanding Balance Meter
        
        - **0-35%**: Heavily favors other party ⚠️
        - **35-50%**: Slightly unfavorable
        - **50-65%**: Fairly balanced ✅
        - **65-100%**: Favorable to you 🎉
        
        ---
        
        #### ⚠️ Disclaimer
        
        This tool provides automated analysis for **informational purposes only**.
        It is **NOT legal advice**. Always consult a qualified lawyer for important contracts.
        """)


# ============== RUN ==============
if __name__ == "__main__":
    main()