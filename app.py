import streamlit as st
import json
import os
import pandas as pd
import time
from models.item_generator import ItemGenerator
from models.scorer import ResponseScorer
from models.adaptive_logic import AdaptiveTestLogic

# App title and configuration
st.set_page_config(page_title="AI Psychometrician", layout="wide")

# Initialize session state variables if not exists
if 'test_items' not in st.session_state:
    try:
        # Load sample items from JSON file
        with open('data/sample_items.json', 'r') as f:
            data = json.load(f)
            if 'items' in data:
                st.session_state.test_items = data['items']
            else:
                st.session_state.test_items = []
                st.error("JSON file doesn't have 'items' key")
    except Exception as e:
        st.error(f"Error loading items: {e}")
        st.session_state.test_items = []

if 'current_item' not in st.session_state:
    st.session_state.current_item = None
    
if 'test_in_progress' not in st.session_state:
    st.session_state.test_in_progress = False
    
if 'test_complete' not in st.session_state:
    st.session_state.test_complete = False
    
if 'adaptive_logic' not in st.session_state:
    st.session_state.adaptive_logic = None
    
if 'scorer' not in st.session_state:
    st.session_state.scorer = ResponseScorer()
    
if 'generator' not in st.session_state:
    # Initialize the item generator (lazy loading to save resources)
    st.session_state.generator = None
    
if 'scores' not in st.session_state:
    st.session_state.scores = None

# Helper functions
def start_test():
    """Start a new psychological assessment test."""
    st.session_state.test_in_progress = True
    st.session_state.test_complete = False
    st.session_state.adaptive_logic = AdaptiveTestLogic(st.session_state.test_items)
    st.session_state.current_item = st.session_state.adaptive_logic.select_next_item()
    st.session_state.scores = None

def process_response(response):
    """Process a user's response to the current item."""
    if st.session_state.current_item and response:
        # Update ability estimate
        st.session_state.scores = st.session_state.adaptive_logic.update_ability(
            st.session_state.current_item, response, st.session_state.scorer
        )
        
        # Select next item
        st.session_state.current_item = st.session_state.adaptive_logic.select_next_item(
            st.session_state.scorer
        )
        
        # Check if test is complete
        if (st.session_state.current_item is None or 
            len(st.session_state.adaptive_logic.response_history) >= 10):  # Limit to 10 items for MVP
            st.session_state.test_in_progress = False
            st.session_state.test_complete = True

def generate_new_item():
    """Generate a new psychometric item using the LLM."""
    if st.session_state.generator is None:
        # Lazy load the generator to save resources
        with st.spinner("Loading language model..."):
            st.session_state.generator = ItemGenerator()
    
    # Generate a new item
    with st.spinner("Generating new test item..."):
        new_item = st.session_state.generator.generate_item()
        st.session_state.test_items.append(new_item)
        st.success(f"Generated new item for domain: {new_item['domain']}")

# Main app UI
st.title("AI Psychometrician MVP")

# Sidebar for controls
with st.sidebar:
    st.header("Controls")
    
    if not st.session_state.test_in_progress and not st.session_state.test_complete:
        if st.button("Start Assessment", key="start_btn"):
            start_test()
    
    if st.session_state.test_complete:
        if st.button("Start New Assessment", key="new_test_btn"):
            start_test()
    
    st.header("Item Generation")
    if st.button("Generate New Item", key="generate_btn"):
        generate_new_item()
    
    st.header("Test Item Bank")
    st.write(f"Total Items: {len(st.session_state.test_items)}")
    
    # Display domains and counts
    domains = {}
    for item in st.session_state.test_items:
        domain = item.get("domain")
        if domain:
            domains[domain] = domains.get(domain, 0) + 1
    
    for domain, count in domains.items():
        st.write(f"- {domain}: {count} items")

# Main content area
if st.session_state.test_in_progress and st.session_state.current_item:
    # Display current item
    st.header("Assessment in Progress")
    
    item = st.session_state.current_item
    st.subheader(f"Question {len(st.session_state.adaptive_logic.response_history) + 1}")
    st.write(item["text"])
    
    # Display response options based on item type
    if item["type"] == "likert_5":
        response = st.radio(
            "Your response:",
            options=["1", "2", "3", "4", "5"],
            format_func=lambda x: {
                "1": "Strongly Disagree",
                "2": "Disagree", 
                "3": "Neutral",
                "4": "Agree",
                "5": "Strongly Agree"
            }[x],
            key=f"response_{item['id']}"
        )
        
        if st.button("Submit Response", key="submit_btn"):
            process_response(response)
    
    # Display progress
    st.progress(len(st.session_state.adaptive_logic.response_history) / 10)  # Max 10 items
    
elif st.session_state.test_complete and st.session_state.scores:
    # Display test results
    st.header("Assessment Results")
    
    scores = st.session_state.scores
    
    # Overall score
    st.subheader("Overall Score")
    st.write(f"{scores['overall']:.2f}")
    st.progress(scores['overall'])
    
    # Domain scores
    st.subheader("Domain Scores")
    
    for domain, score in scores.get("domains", {}).items():
        interpretation = scores.get("interpretations", {}).get(domain, "moderate")
        
        # Format domain name for display
        display_domain = domain.replace("_", " ").title()
        
        # Display domain score with interpretation
        st.write(f"**{display_domain}**: {score:.2f} - {interpretation.title()} level")
        
        # Color-code the progress bar
        color = {
            "low": "green",
            "moderate": "blue",
            "high": "red"
        }.get(interpretation, "blue")
        
        # Simpler approach - remove the delta lines
        if interpretation == "low":
            st.progress(score, text=f"{display_domain}")
        elif interpretation == "high":
            st.progress(score, text=f"{display_domain}")
        else:
            st.progress(score, text=f"{display_domain}")
    
    # Response history
    st.subheader("Your Responses")
    
    # Create a dataframe for responses
    responses_data = []
    for item, response in st.session_state.adaptive_logic.response_history:
        responses_data.append({
            "Question": item["text"],
            "Domain": item["domain"].replace("_", " ").title(),
            "Your Response": {
                "1": "Strongly Disagree",
                "2": "Disagree", 
                "3": "Neutral",
                "4": "Agree",
                "5": "Strongly Agree"
            }.get(response, response)
        })
    
    if responses_data:
        st.dataframe(pd.DataFrame(responses_data), use_container_width=True)
        
else:
    # Welcome screen
    st.header("Welcome to AI Psychometrician")
    
    st.write("""
    This is a Minimum Viable Product (MVP) demonstrating:
    
    1. **AI-Generated Test Items** - Using an open-source language model
    2. **Adaptive Testing** - Questions adapt based on your responses
    3. **Automated Scoring** - Instant calculation of psychological metrics
    
    Click "Start Assessment" in the sidebar to begin.
    """)
    
    # Example items
    st.subheader("Sample Test Items")
    for item in st.session_state.test_items[:3]:
        st.info(item["text"]) 