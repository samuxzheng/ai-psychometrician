# AI Psychometrician

## Project Summary

The AI Psychometrician is a minimum viable product (MVP) that demonstrates how artificial intelligence can be used to create, administer, and score psychological assessments. This project combines natural language processing, psychometric principles, and adaptive testing to create a personalized assessment experience.

## Key Components

1. Item Generation: Uses an open-source language model (GPT-2, replaceable with Qwen, DeepSeek, or LLaMA) to create new psychometric test items on demand.

2. Automated Scoring: Implements a scoring system for Likert-scale responses, with domain-specific interpretations.

3. Adaptive Testing: Selects questions based on previous responses to maximize assessment efficiency, prioritizing domains with fewer answers and matching question difficulty to estimated ability level.

4. Web Interface: A clean, interactive Streamlit application for test administration and results visualization.

## Project Structure

```
ai_psychometrician/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Project dependencies
├── data/
│   └── sample_items.json  # Initial test item bank
└── models/
    ├── item_generator.py  # LLM-based item generation
    ├── scorer.py          # Response scoring logic
    └── adaptive_logic.py  # Adaptive test selection
```

## Installation and Setup

1. Clone the repository:
   git clone https://github.com/yourusername/ai_psychometrician.git
   cd ai_psychometrician

2. Create a virtual environment:
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
   python3 -m pip install -r requirements.txt

4. Run the application:
   python3 -m streamlit run app.py

## Usage

### Taking an Assessment

1. Click "Start Assessment" in the sidebar
2. Answer each question by selecting from the Likert scale options (Strongly Disagree to Strongly Agree)
3. Click "Submit Response" after each answer
4. After completing 10 questions, you'll see your results with domain-specific scores and interpretations

### Generating New Items

1. Click "Generate New Item" in the sidebar
2. The system will use the language model to create a new psychometric test item
3. The new item will be added to the test item bank and available for future assessments

### Viewing Results

After completing an assessment, you'll see:
- Overall score with visual progress indicator
- Domain-specific scores with interpretations (low, moderate, high)
- A table of all your responses for review

## Technical Implementation

### Item Generation
The ItemGenerator class uses the Hugging Face Transformers library to generate new test items based on domain examples. It formats prompts with existing items as examples and extracts clean, well-formed questions from the model output.

### Response Scoring
The ResponseScorer class implements a simple scoring model for Likert-scale items, with domain-specific score ranges and interpretations. It handles score inversion for positively-worded items in certain domains.

### Adaptive Testing
The AdaptiveTestLogic class selects items to maximize assessment breadth and precision. It prioritizes domains with fewer responses and selects items with difficulty levels close to the current ability estimate.

### Web Application
Built with Streamlit, the web app provides an intuitive interface for test administration, results visualization, and item generation. It uses session state to maintain test progress and user responses.

## Current Status

We have successfully implemented the core functionality of the AI Psychometrician MVP:
- Created a working Streamlit application
- Implemented item generation, scoring, and adaptive logic
- Fixed initial bugs, including a variable naming conflict
- Established a solid foundation for future enhancements

## Future Enhancements

1. Advanced Item Generation: Fine-tune the LLM on real psychometric data for higher quality items
2. Item Response Theory (IRT): Implement proper IRT models for more accurate ability estimation
3. User Accounts: Add authentication and persistence for longitudinal assessment
4. Expanded Item Bank: Increase domain coverage with more diverse test items
5. Clinical Validation: Validate against established psychological assessments
6. Multilingual Support: Extend the system to support multiple languages
7. Advanced Reporting: Add visualizations and more detailed interpretations

## Dependencies

- streamlit==1.22.0: Web application framework
- transformers==4.28.1: For language model implementation
- torch==2.0.0: Backend for transformers
- numpy==1.24.3: Numerical operations
- pandas==2.0.1: Data manipulation for results
- scikit-learn==1.2.2: Machine learning utilities

## Disclaimer

This is an MVP and not intended for clinical use without further validation and development. The psychometric properties of the generated items have not been validated against established psychological assessments.

## Troubleshooting

Common issues and solutions:
- "pip: command not found": Use python3 -m pip instead or create an alias
- "streamlit: command not found": Ensure your virtual environment is activated and dependencies are installed
- TypeErrors with session state: Fixed by renaming session variables to avoid conflicts

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Created as a demonstration of AI-augmented psychological assessment 