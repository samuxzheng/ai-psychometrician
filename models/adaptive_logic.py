import numpy as np
import random

class AdaptiveTestLogic:
    def __init__(self, items, initial_ability=0.5):
        """
        Initialize the adaptive test logic.
        
        Args:
            items (list): List of available test items
            initial_ability (float): Initial estimate of user's ability/trait level
        """
        self.items = items
        self.current_ability = initial_ability
        self.answered_items = set()
        self.response_history = []
        
        # For a simple MVP, we'll categorize items by domain
        self.domain_items = {}
        for item in items:
            domain = item.get("domain")
            if domain:
                if domain not in self.domain_items:
                    self.domain_items[domain] = []
                self.domain_items[domain].append(item)
    
    def select_next_item(self, scorer=None):
        """
        Select the next item based on current ability estimate.
        
        Args:
            scorer (ResponseScorer, optional): Scorer for calculating current domain scores
            
        Returns:
            dict: The next test item to present
        """
        # If we have response history and a scorer, calculate domain scores
        domain_scores = {}
        if scorer and self.response_history:
            scores = scorer.calculate_overall_score(self.response_history)
            domain_scores = scores.get("domains", {})
        
        # Simple adaptive algorithm for MVP:
        # 1. Identify domains that need more assessment (low item count)
        # 2. Select an item with difficulty close to current ability estimate
        
        # Count items per domain in response history
        domain_counts = {}
        for item, _ in self.response_history:
            domain = item.get("domain")
            if domain:
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Find domains with fewest items answered
        all_domains = list(self.domain_items.keys())
        if not all_domains:
            # No domains defined, randomly select from remaining items
            remaining_items = [item for item in self.items 
                              if item["id"] not in self.answered_items]
            if not remaining_items:
                return None  # No more items
            return random.choice(remaining_items)
        
        # Select domain with fewest answers (prioritize assessment breadth)
        target_domain = min(all_domains, key=lambda d: domain_counts.get(d, 0))
        
        # Get available items in target domain
        available_items = [item for item in self.domain_items.get(target_domain, [])
                          if item["id"] not in self.answered_items]
        
        if not available_items:
            # If no items in target domain, select from any remaining item
            remaining_items = [item for item in self.items 
                              if item["id"] not in self.answered_items]
            if not remaining_items:
                return None  # No more items
            return random.choice(remaining_items)
        
        # Select item with difficulty closest to current domain ability
        domain_ability = domain_scores.get(target_domain, self.current_ability)
        
        # Find item with difficulty closest to current ability estimate
        selected_item = min(available_items, 
                           key=lambda item: abs(item.get("difficulty", 0.5) - domain_ability))
        
        return selected_item
    
    def update_ability(self, item, response, scorer):
        """
        Update ability estimate based on response to an item.
        
        Args:
            item (dict): The item that was answered
            response (str): The user's response
            scorer (ResponseScorer): Scorer for calculating the response score
        """
        # Record that this item has been answered
        self.answered_items.add(item["id"])
        
        # Add to response history
        self.response_history.append((item, response))
        
        # For MVP, we'll use a simple approach:
        # Update ability estimate based on mean scores in each domain
        scores = scorer.calculate_overall_score(self.response_history)
        self.current_ability = scores["overall"]
        
        return scores 