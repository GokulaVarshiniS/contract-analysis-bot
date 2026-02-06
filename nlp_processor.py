import spacy
import nltk
import re
from typing import List, Dict, Tuple
from collections import defaultdict

# Download required NLTK data
def download_nltk_data():
    """Download all required NLTK data"""
    packages = [
        'punkt',
        'punkt_tab', 
        'stopwords', 
        'averaged_perceptron_tagger',
        'averaged_perceptron_tagger_eng'
    ]
    for package in packages:
        try:
            nltk.data.find(f'tokenizers/{package}')
        except LookupError:
            try:
                nltk.download(package, quiet=True)
            except:
                pass
        try:
            nltk.data.find(f'corpora/{package}')
        except LookupError:
            try:
                nltk.download(package, quiet=True)
            except:
                pass
        try:
            nltk.data.find(f'taggers/{package}')
        except LookupError:
            try:
                nltk.download(package, quiet=True)
            except:
                pass

# Run download on import
download_nltk_data()

from nltk.corpus import stopwords


class NLPProcessor:
    """Handles NLP preprocessing tasks using spaCy and NLTK"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            from spacy.cli import download
            download("en_core_web_lg")
            self.nlp = spacy.load("en_core_web_lg")
        
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            nltk.download('stopwords', quiet=True)
            self.stop_words = set(stopwords.words('english'))
        
        self.clause_patterns = {
            'penalty': [r'penalty', r'penalt(y|ies)', r'fine\s', r'liquidated damages', r'late fee'],
            'indemnity': [r'indemnif(y|ication)', r'hold harmless', r'defend.*against'],
            'termination': [r'terminat(e|ion)', r'cancel(lation)?', r'end.*agreement'],
            'arbitration': [r'arbitrat(e|ion)', r'dispute resolution', r'mediation'],
            'jurisdiction': [r'jurisdiction', r'governing law', r'governed by.*law'],
            'auto_renewal': [r'auto(matic)?.*renew(al)?', r'automatically.*extend'],
            'lock_in': [r'lock(-|\s)?in', r'minimum.*period', r'committed.*term'],
            'non_compete': [r'non(-|\s)?compete', r'non(-|\s)?competition'],
            'ip_transfer': [r'intellectual property', r'ip.*transfer', r'copyright.*assign'],
            'confidentiality': [r'confidential(ity)?', r'non(-|\s)?disclosure', r'nda'],
            'liability': [r'liabilit(y|ies)', r'liable', r'limitation.*liability'],
            'force_majeure': [r'force majeure', r'act of god', r'unforeseeable']
        }
    
    def process(self, text: str) -> Dict:
        """Main processing pipeline"""
        doc = self.nlp(text)
        
        return {
            'sentences': self._extract_sentences(text),
            'clauses': self._extract_clauses(text),
            'entities': self._extract_entities(doc),
            'clause_types': self._identify_clause_types(text),
            'key_terms': self._extract_key_terms(doc),
            'obligations': self._identify_obligations(doc),
            'rights': self._identify_rights(doc),
            'prohibitions': self._identify_prohibitions(doc)
        }
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text using spaCy instead of NLTK"""
        # Use spaCy for sentence tokenization (more reliable)
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
        return sentences
    
    def _extract_clauses(self, text: str) -> List[Dict]:
        """Extract clauses and sub-clauses from contract"""
        clauses = []
        parts = re.split(r'\n(?=\d+\.|\([a-z]\)|\d+\))', text)
        
        for i, part in enumerate(parts):
            if len(part.strip()) < 20:
                continue
            
            match = re.match(r'^(\d+(?:\.\d+)*|[a-z])[.)]\s*', part.strip())
            clause_num = match.group(1) if match else str(i + 1)
            
            lines = part.strip().split('\n')
            heading = ""
            content = part.strip()
            
            if lines and len(lines[0]) < 100:
                heading = lines[0]
                content = '\n'.join(lines[1:]) if len(lines) > 1 else lines[0]
            
            clauses.append({
                'number': clause_num,
                'heading': heading,
                'content': content[:500],
                'full_text': part.strip()
            })
        
        return clauses
    
    def _extract_entities(self, doc) -> Dict[str, List]:
        """Extract named entities relevant to contracts"""
        entities = defaultdict(list)
        
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG']:
                entities['parties'].append(ent.text)
            elif ent.label_ == 'DATE':
                entities['dates'].append(ent.text)
            elif ent.label_ == 'MONEY':
                entities['amounts'].append(ent.text)
            elif ent.label_ == 'GPE':
                entities['jurisdictions'].append(ent.text)
            elif ent.label_ == 'PERCENT':
                entities['percentages'].append(ent.text)
        
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return dict(entities)
    
    def _identify_clause_types(self, text: str) -> Dict[str, List[str]]:
        """Identify different types of clauses in the contract"""
        identified_clauses = defaultdict(list)
        
        # Use spaCy for sentence splitting
        doc = self.nlp(text.lower())
        sentences = [sent.text for sent in doc.sents]
        
        for sentence in sentences:
            for clause_type, patterns in self.clause_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        identified_clauses[clause_type].append(sentence)
                        break
        
        return dict(identified_clauses)
    
    def _extract_key_terms(self, doc) -> List[str]:
        """Extract key legal terms and important nouns"""
        key_terms = []
        for chunk in doc.noun_chunks:
            if len(chunk.text) > 3 and chunk.text.lower() not in self.stop_words:
                key_terms.append(chunk.text)
        return list(set(key_terms))[:50]
    
    def _identify_obligations(self, doc) -> List[str]:
        """Identify obligations (shall, must, will, required to)"""
        obligations = []
        obligation_patterns = [r'shall\s+\w+', r'must\s+\w+', r'will\s+\w+', r'required to', r'obligat(ed|ion)']
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            for pattern in obligation_patterns:
                if re.search(pattern, sent_text):
                    obligations.append(sent.text.strip())
                    break
        return obligations
    
    def _identify_rights(self, doc) -> List[str]:
        """Identify rights (may, entitled to, right to)"""
        rights = []
        right_patterns = [r'may\s+\w+', r'entitled to', r'right to', r'has the right', r'reserves the right']
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            for pattern in right_patterns:
                if re.search(pattern, sent_text):
                    rights.append(sent.text.strip())
                    break
        return rights
    
    def _identify_prohibitions(self, doc) -> List[str]:
        """Identify prohibitions (shall not, must not, prohibited)"""
        prohibitions = []
        prohibition_patterns = [r'shall not', r'must not', r'will not', r'prohibited', r'not permitted']
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            for pattern in prohibition_patterns:
                if re.search(pattern, sent_text):
                    prohibitions.append(sent.text.strip())
                    break
        return prohibitions


class ClauseSimilarityMatcher:
    """Match clauses against standard templates"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.standard_clauses = {
            'termination': "Either party may terminate this agreement by providing 30 days written notice.",
            'indemnity': "Each party shall indemnify and hold harmless the other party from any claims.",
            'confidentiality': "Both parties agree to maintain confidentiality of all proprietary information.",
            'jurisdiction': "This agreement shall be governed by the laws of India.",
            'force_majeure': "Neither party shall be liable for failure due to circumstances beyond control."
        }
    
    def calculate_similarity(self, clause_text: str, standard_type: str) -> float:
        """Calculate similarity between a clause and standard template"""
        if standard_type not in self.standard_clauses:
            return 0.0
        clause_doc = self.nlp(clause_text)
        standard_doc = self.nlp(self.standard_clauses[standard_type])
        return round(clause_doc.similarity(standard_doc), 2)
    
    def find_best_match(self, clause_text: str) -> Tuple[str, float]:
        """Find the best matching standard clause type"""
        best_match = None
        best_score = 0.0
        for clause_type in self.standard_clauses:
            score = self.calculate_similarity(clause_text, clause_type)
            if score > best_score:
                best_score = score
                best_match = clause_type
        return best_match, best_score