# MSVA - Multi-Agent Startup Validation Assistant

## Usage Guide

This guide provides detailed instructions on how to use the Multi-Agent Startup Validation Assistant (MSVA) to validate your startup ideas with AI agents.

### Table of Contents

1. [System Requirements](#system-requirements)
2. [Initial Setup](#initial-setup)
3. [Configuring Your Environment](#configuring-your-environment)
4. [Running a Validation](#running-a-validation)
5. [Understanding the Results](#understanding-the-results)
6. [Available Workflows](#available-workflows)
7. [Customizing the System](#customizing-the-system)
8. [Troubleshooting](#troubleshooting)

## System Requirements

- Python 3.8+ installed
- Pip package manager
- Internet connection (for API calls and search operations)
- API keys for search services (optional but recommended)

## Initial Setup

1. **Clone or download the repository**:
   ```
   git clone https://github.com/JbellMD/msva.git
   cd msva
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Create your environment file**:
   ```
   cp .env.example .env
   ```

4. **Edit the .env file** with your API keys and preferences.

## Configuring Your Environment

The `.env` file contains important configuration settings:

```
# OpenAI API Key (required for LLM functionality)
OPENAI_API_KEY=your-openai-key-here

# Search API Keys (at least one is recommended)
SERPER_API_KEY=your-serper-api-key-here
SERPAPI_API_KEY=your-serpapi-key-here

# Optional Google Trends API credentials
GOOGLE_TRENDS_TZ=360
GOOGLE_TRENDS_QUER=US

# Vector Database Settings
VECTOR_DB_PERSISTENCE_DIR=./data/vector_db

# Debug Mode
DEBUG=False
```

- **API Keys**: You'll need an OpenAI API key. For search functionality, either a Serper or SerpAPI key is recommended.
- **Vector Database**: This specifies where vector embeddings are stored. Default is fine for most users.
- **Debug Mode**: Set to `True` to enable detailed logging.

## Running a Validation

### Basic Usage

Run a validation with the example startup idea:

```
python app.py
```

### Using a Custom Startup Idea

1. Create a JSON file with your startup idea details (see `examples/custom_startup.json` for format)
2. Run the validation with your custom idea:

```
python app.py --input-file your_idea.json
```

### Command Line Options

- `--input-file`: Path to your custom startup idea JSON file
- `--output-dir`: Directory to save results (default: `./outputs`)
- `--workflow`: Workflow to run (`full_validation`, `market_only`, or `mvp_only`)
- `--debug`: Enable debug mode for detailed logs
- `--interactive`: Enable human-in-the-loop mode for approvals and feedback

Examples:

```
# Run with debug logging
python app.py --debug

# Run market research only
python app.py --workflow market_only

# Run with human-in-the-loop mode
python app.py --interactive

# Specify custom output directory
python app.py --output-dir ./my_validations
```

## Understanding the Results

After running a validation, you'll get:

1. **Console Output**: A summary of the validation results
2. **Validation Report**: A detailed JSON report in your output directory

### Validation Score

The validation score (0-100) indicates the overall potential of your startup idea:

- **80-100**: Highly Promising - Strong market potential with few obstacles
- **60-79**: Promising - Good potential but with some challenges
- **40-59**: Moderate Potential - Significant challenges but still viable
- **0-39**: Challenging - Major obstacles to success identified

### Report Structure

The full validation report includes:

- **Idea**: Your startup idea details
- **Market Analysis**: Market trends, size, and growth potential
- **Competitor Analysis**: Existing competitors and market gaps
- **Customer Personas**: Detailed profiles of target customers
- **MVP Plan**: Features, timeline, costs, and tech stack recommendations
- **Recommendations**: Actionable insights for moving forward
- **Validation Score**: Numerical assessment of potential

## Available Workflows

MSVA offers three distinct workflows:

1. **full_validation**: Complete end-to-end validation (all 4 agents)
   - Market research
   - Competitor analysis
   - Customer persona generation
   - MVP planning

2. **market_only**: Quick market validation (Market Researcher Agent only)
   - Market trends analysis
   - Market size estimation
   - Growth assessment

3. **mvp_only**: MVP planning with provided market data (MVP Planner Agent only)
   - Feature prioritization
   - Tech stack recommendations
   - Cost and timeline estimates

## Customizing the System

### Adding New Agents

1. Create a new agent class that inherits from `BaseAgent` in the `agents` directory
2. Implement the required `process` method
3. Register the agent in `app.py`

### Adding New Tools

1. Create a new tool class that inherits from `BaseTool` in the `tools` directory
2. Implement the required `run` method
3. Register the tool in `app.py`

### Creating Custom Workflows

1. Add a new workflow method in `startup_validator.py`
2. Register the workflow in the `__init__` method
3. Update the workflow choices in `app.py`

## Troubleshooting

### API Key Issues

If you see errors related to API calls:
- Check that your API keys are correctly entered in the `.env` file
- Verify that your API keys are active and have sufficient credits

### Dependency Issues

If you encounter dependency-related errors:
- Ensure you have Python 3.8 or newer
- Try reinstalling dependencies: `pip install -r requirements.txt --force-reinstall`
- Check for conflicting packages in your environment

### Search or Scraping Problems

If web search or scraping fails:
- Check your internet connection
- Verify your API keys
- Some websites may block scraping; try different URLs

### Performance Issues

For slow performance:
- Enable simpler workflows (e.g., `market_only` instead of `full_validation`)
- Check if you have conflicting processes using system resources
- Consider running with reduced debug output
