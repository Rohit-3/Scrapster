# keyword_validator.py - Intelligent Keyword Relevance Validator
import re
from typing import List, Dict, Tuple

class KeywordRelevanceValidator:
    """Validates if a profile is actually related to the keywords"""
    
    # Common irrelevant terms (product sellers, not professionals)
    IRRELEVANT_TERMS = [
        'shop', 'store', 'buy', 'sell', 'purchase', 'price', 'deal', 'discount',
        'product', 'products', 'equipment', 'device', 'scanner', 'reader',
        'handbag', 'wallet', 'blocking', 'protection', 'card holder',
        'amazon', 'ebay', 'aliexpress', 'wholesale', 'retail',
        'shipping', 'delivery', 'order', 'cart', 'checkout'
    ]
    
    # Professional indicators (good signs)
    PROFESSIONAL_TERMS = [
        'engineer', 'developer', 'architect', 'specialist', 'consultant',
        'manager', 'director', 'lead', 'senior', 'principal', 'staff',
        'researcher', 'analyst', 'scientist', 'expert', 'professional',
        'experience', 'years', 'skills', 'certification', 'degree',
        'university', 'college', 'education', 'project', 'team'
    ]
    
    def __init__(self, keywords: List[str]):
        self.keywords = [k.lower().strip() for k in keywords if k.strip()]
        self.keyword_terms = self._extract_keyword_terms()
    
    def _extract_keyword_terms(self) -> List[str]:
        """Extract meaningful terms from keywords"""
        terms = []
        for keyword in self.keywords:
            # Split by common separators
            parts = re.split(r'[\s,.-]+', keyword.lower())
            # Filter out common words and keep meaningful terms
            meaningful = [p for p in parts if len(p) > 2 and p not in ['the', 'and', 'or', 'for', 'with', 'from']]
            terms.extend(meaningful)
        return list(set(terms))  # Remove duplicates
    
    def calculate_relevance_score(self, profile_text: str, title: str = "", job_title: str = "", company: str = "") -> Tuple[float, str]:
        """
        Calculate relevance score (0-1) and reason
        
        Returns:
            (score, reason) - score between 0 and 1, reason for the score
        """
        if not profile_text:
            return (0.0, "No profile text available")
        
        combined_text = f"{title} {job_title} {company} {profile_text}".lower()
        
        # Check for irrelevant terms (strong negative signal)
        irrelevant_count = sum(1 for term in self.IRRELEVANT_TERMS if term in combined_text)
        if irrelevant_count >= 2:
            return (0.0, f"Profile appears to be selling products (found {irrelevant_count} irrelevant terms)")
        
        # Check for keyword matches (strong positive signal)
        keyword_matches = sum(1 for term in self.keyword_terms if term in combined_text)
        
        # Check for professional indicators (positive signal)
        professional_count = sum(1 for term in self.PROFESSIONAL_TERMS if term in combined_text)
        
        # Check if it's a product listing (bad)
        product_indicators = ['shop', 'buy', 'sell', 'price', 'add to cart', 'checkout']
        is_product = any(indicator in combined_text for indicator in product_indicators)
        if is_product:
            return (0.0, "Profile appears to be a product listing, not a professional")
        
        # Check if it's a company page (bad if we want individuals)
        company_page_indicators = ['about us', 'our company', 'our team', 'contact us', 'careers']
        is_company_page = sum(1 for ind in company_page_indicators if ind in combined_text) >= 2
        if is_company_page:
            return (0.0, "Profile appears to be a company page, not an individual")
        
        # Calculate base score
        base_score = 0.0
        
        # Keyword matches are most important (40% weight)
        if keyword_matches > 0:
            keyword_score = min(keyword_matches / len(self.keyword_terms), 1.0) * 0.4
            base_score += keyword_score
        
        # Professional indicators help (30% weight)
        if professional_count > 0:
            professional_score = min(professional_count / 5, 1.0) * 0.3
            base_score += professional_score
        
        # Job title matching (20% weight)
        if job_title:
            job_match = any(term in job_title.lower() for term in self.keyword_terms)
            if job_match:
                base_score += 0.2
        
        # Company relevance (10% weight)
        if company:
            company_match = any(term in company.lower() for term in self.keyword_terms)
            if company_match:
                base_score += 0.1
        
        # Penalize if no keyword matches at all
        if keyword_matches == 0:
            base_score *= 0.3  # Reduce score significantly
        
        # Build reason
        reasons = []
        if keyword_matches > 0:
            reasons.append(f"Found {keyword_matches} keyword match(es)")
        if professional_count > 0:
            reasons.append(f"Found {professional_count} professional indicator(s)")
        if job_title and any(term in job_title.lower() for term in self.keyword_terms):
            reasons.append("Job title matches keywords")
        if not reasons:
            reasons.append("No clear keyword relevance")
        
        reason = "; ".join(reasons) if reasons else "Low relevance"
        
        return (min(base_score, 1.0), reason)
    
    def is_relevant(self, profile_text: str, title: str = "", job_title: str = "", company: str = "", min_score: float = 0.3) -> Tuple[bool, float, str]:
        """
        Check if profile is relevant to keywords
        
        Returns:
            (is_relevant, score, reason)
        """
        score, reason = self.calculate_relevance_score(profile_text, title, job_title, company)
        return (score >= min_score, score, reason)
    
    def validate_profile(self, name: str, profile_text: str, title: str = "", job_title: str = "", company: str = "", url: str = "") -> Dict:
        """
        Comprehensive profile validation
        
        Returns:
            dict with 'is_valid', 'score', 'reason', 'confidence'
        """
        score, reason = self.calculate_relevance_score(profile_text, title, job_title, company)
        
        # Additional checks
        checks = {
            'has_name': bool(name and name != "Unknown" and len(name) > 2),
            'has_keyword_match': any(term in profile_text.lower() for term in self.keyword_terms),
            'is_professional': any(term in profile_text.lower() for term in self.PROFESSIONAL_TERMS),
            'not_product': not any(term in profile_text.lower() for term in self.IRRELEVANT_TERMS[:5]),
            'not_company_page': not any(ind in profile_text.lower() for ind in ['about us', 'our company', 'contact us'])
        }
        
        # Calculate confidence
        checks_passed = sum(checks.values())
        confidence = checks_passed / len(checks)
        
        # Final validation (must pass key checks)
        is_valid = (
            score >= 0.3 and  # Minimum relevance score
            checks['has_name'] and  # Must have a name
            checks['has_keyword_match'] and  # Must match keywords
            checks['not_product']  # Must not be a product listing
        )
        
        return {
            'is_valid': is_valid,
            'score': score,
            'reason': reason,
            'confidence': confidence,
            'checks': checks
        }

