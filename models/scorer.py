import numpy as np

class ResponseScorer:
    def __init__(self):
        """Initialize the response scorer."""
        # Define scoring weights for Likert scales
        # For our MVP, we'll use a simple scoring approach
        self.likert_weights = {
            "likert_5": {
                "1": 0.0,  # Strongly disagree
                "2": 0.25, # Disagree
                "3": 0.5,  # Neutral
                "4": 0.75, # Agree
                "5": 1.0   # Strongly agree
            }
        }
        
        # Domain score ranges
        self.domain_ranges = {
            "anxiety": {"low": 0.0, "moderate": 0.3, "high": 0.7},
            "depression": {"low": 0.0, "moderate": 0.3, "high": 0.7},
            "stress": {"low": 0.0, "moderate": 0.3, "high": 0.7},
            "attention": {"low": 0.0, "moderate": 0.3, "high": 0.7},
            "sociability": {"low": 0.0, "moderate": 0.3, "high": 0.7},
            "conscientiousness": {"low": 0.0, "moderate": 0.3, "high": 0.7},
            "fatigue": {"low": 0.0, "moderate": 0.3, "high": 0.7}
        }
    
    def score_response(self, item, response):
        """
        Score a single response to an item.
        
        Args:
            item (dict): The test item
            response (str): The user's response (e.g., "1" through "5" for Likert-5)
            
        Returns:
            float: A normalized score between 0 and 1
        """
        item_type = item.get("type", "likert_5")
        
        # For Likert scales
        if item_type.startswith("likert"):
            # Get weights for this Likert scale
            weights = self.likert_weights.get(item_type, self.likert_weights["likert_5"])
            
            # Get raw score
            raw_score = weights.get(response, 0.5)  # Default to middle if invalid
            
            # Invert scores for certain domains if needed
            # In a real system, we'd have item-level inversion flags
            if item.get("domain") in ["sociability", "conscientiousness"] and "don't" not in item["text"].lower():
                raw_score = 1.0 - raw_score
                
            return raw_score
        
        # For other item types (not implemented in MVP)
        return 0.5  # Default middle score
    
    def calculate_domain_score(self, responses, domain):
        """
        Calculate score for a specific psychological domain.
        
        Args:
            responses (list): List of (item, response) tuples
            domain (str): Psychological domain to calculate score for
            
        Returns:
            float: Domain score between 0 and 1
        """
        # Filter responses by domain
        domain_responses = [(item, resp) for item, resp in responses 
                           if item.get("domain") == domain]
        
        if not domain_responses:
            return 0.5  # Default middle score if no items for this domain
        
        # Calculate average score
        scores = [self.score_response(item, resp) for item, resp in domain_responses]
        return sum(scores) / len(scores)
    
    def calculate_overall_score(self, responses):
        """
        Calculate overall psychological assessment score.
        
        Args:
            responses (list): List of (item, response) tuples
            
        Returns:
            dict: Overall score and domain scores
        """
        # Get unique domains from responses
        domains = set(item.get("domain") for item, _ in responses if "domain" in item)
        
        # Calculate domain scores
        domain_scores = {
            domain: self.calculate_domain_score(responses, domain)
            for domain in domains
        }
        
        # Calculate overall score (weighted average of domain scores)
        if domain_scores:
            overall_score = sum(domain_scores.values()) / len(domain_scores)
        else:
            overall_score = 0.5
        
        # Add interpretations for each domain
        interpretations = {}
        for domain, score in domain_scores.items():
            if domain in self.domain_ranges:
                ranges = self.domain_ranges[domain]
                if score < ranges["moderate"]:
                    level = "low"
                elif score < ranges["high"]:
                    level = "moderate"
                else:
                    level = "high"
                interpretations[domain] = level
        
        return {
            "overall": overall_score,
            "domains": domain_scores,
            "interpretations": interpretations
        } 