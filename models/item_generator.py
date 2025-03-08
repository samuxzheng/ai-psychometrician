from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import json
import os

class ItemGenerator:
    def __init__(self, model_name="gpt2"):
        """
        Initialize the item generator with a pretrained model.
        
        Args:
            model_name (str): Name of the pretrained model to use
                              Can be replaced with Qwen, DeepSeek, or LLaMA
        """
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        
        # Load existing items to use as examples
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                "data", "sample_items.json")
        with open(data_path, 'r') as f:
            self.existing_items = json.load(f)['items']
        
        # Define domains for psychometric assessment
        self.domains = ["anxiety", "depression", "stress", "attention", 
                       "sociability", "conscientiousness", "fatigue"]
    
    def generate_item(self, domain=None, difficulty=None):
        """
        Generate a new psychometric test item.
        
        Args:
            domain (str, optional): Specific psychological domain for the item
            difficulty (float, optional): Difficulty level from 0.0 to 1.0
        
        Returns:
            dict: A new psychometric test item
        """
        # Select random domain if not specified
        if domain is None:
            import random
            domain = random.choice(self.domains)
            
        # Set default difficulty if not specified
        if difficulty is None:
            import random
            difficulty = round(random.uniform(0.1, 0.9), 1)
        
        # Find example items in the same domain
        domain_examples = [item for item in self.existing_items 
                          if item["domain"] == domain]
        
        # Use transformation prompt technique for a simple MVP
        # In a real system, we'd fine-tune the model or use more sophisticated prompting
        prompt = self._create_generation_prompt(domain, domain_examples)
        
        # Generate text
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
        
        # Generate item text (with simple parameters for MVP)
        output = self.model.generate(
            input_ids,
            max_length=100,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Extract the item text from the generated output
        item_text = self._extract_item_text(generated_text, prompt)
        
        # Create a new item dictionary
        new_item = {
            "id": max(item["id"] for item in self.existing_items) + 1,
            "text": item_text,
            "type": "likert_5",
            "domain": domain,
            "difficulty": difficulty
        }
        
        return new_item
    
    def _create_generation_prompt(self, domain, examples):
        """Create a prompt for generating a new item in the specified domain."""
        prompt = f"Generate a new psychological assessment question about {domain}.\n\n"
        
        # Add examples
        if examples:
            prompt += "Here are some examples:\n"
            for example in examples[:2]:  # Limit to 2 examples
                prompt += f"- {example['text']}\n"
        
        prompt += f"\nNew {domain} assessment question: "
        return prompt
    
    def _extract_item_text(self, generated_text, prompt):
        """Extract the actual item text from the generated output."""
        # For the MVP, we'll take a simplified approach to extract the text
        item_text = generated_text[len(prompt):].strip()
        
        # Clean up the text (remove quotes, limit to first sentence, etc.)
        if '"' in item_text:
            item_text = item_text.split('"')[1]
        elif '.' in item_text:
            item_text = item_text.split('.')[0] + '.'
            
        return item_text 