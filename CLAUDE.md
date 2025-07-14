# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Application
```bash
# Start the Flask web server
python src/app.py

or 
# Full path with interpriter env
home/user-name/miniconda3/envs/ai-productivity/bin/python /home/lwedderburn/project/AI_Produtivity/ai-productivity-workflow-agent/src/app.py

# The application will be available at http://127.0.0.1:5000
```

### Testing
```bash
# Run all tests with comprehensive reporting
python run_tests.py --all

# Run specific test suites
python run_tests.py --unit        # Unit tests only
python run_tests.py --security    # Security tests only
python run_tests.py --functional  # Functional tests only

# Run with verbose output and save JSON report
python run_tests.py --all --verbose --save-report
```

### Environment Setup
```bash
# Create and activate conda environment
conda create -n .condaenv python=3.9
conda activate .condaenv

# Install dependencies
pip install -r requirements.txt
```

## High-Level Architecture

### Core Components

**AI Agent (`src/ai_agent.py`)**: The `EnhancedGISTicketAgent` class is the heart of the system, providing:
- XML-weighted processing with absolute maximum priority for XML JSON key values
- OpenAI integration for AI-powered ticket analysis
- Rule-based fallback analysis with sophisticated priority weighting
- Prompt export functionality for manual AI model usage

**Flask Web Application (`src/app.py`)**: Web interface providing:
- XML ticket import via `XMLTicketParser` class
- REST API endpoints for ticket analysis and bulk processing
- Action plan generation based on ticket categories
- Comprehensive ticket processing workflows

**Test Suite (`run_tests.py`)**: Comprehensive testing framework with:
- Unit tests for core functionality
- Security validation tests
- Functional workflow tests
- Automated reporting and CI/CD integration

### Key Design Patterns

**Weighted XML Processing**: The system prioritizes XML-extracted JSON key values with absolute maximum weighting (up to weight 10) over manual form inputs. This ensures data from imported XML files takes precedence in analysis.

**Category-Based Processing**: Tickets are classified into GIS-specific categories:
- `arcgis_pro`: Desktop GIS software issues
- `web_mapping`: Online/portal web mapping issues  
- `data_issues`: Spatial data and geodatabase problems
- `permissions`: Access control and authentication issues
- `geocoding`: Address matching and coordinate conversion
- `printing`: Map layout and printing issues
- `mobile`: Field data collection applications

**Multi-Modal Analysis**: The system supports both AI-powered analysis (OpenAI integration) and rule-based analysis as fallback, with configurable behavior via environment variables.

### Configuration

Environment variables in `.env`:
- `OPENAI_API_KEY`: OpenAI API key for AI analysis
- `OPENAI_MODEL`: Model to use (default: gpt-4o-mini)
- `AI_ENABLED`: Enable AI analysis (true/false)
- `FALLBACK_TO_RULES`: Use rule-based analysis as fallback (true/false)
- `EXPORT_PROMPTS`: Export prompt contexts for manual AI usage (true/false)

### Data Flow

1. **XML Import**: Tickets imported via XML files are parsed by `XMLTicketParser`
2. **Analysis**: `EnhancedGISTicketAgent` processes tickets with weighted XML priority
3. **Response Generation**: System generates contextual responses and action plans
4. **Prompt Export**: Prompts are exported to `prompts_export/` for manual AI usage

### Test Organization

Tests are organized into three main categories:
- **Unit Tests** (`tests/test_unit.py`): Core functionality testing
- **Security Tests** (`tests/test_security.py`): Security validation and vulnerability checks
- **Functional Tests** (`tests/test_functional.py`): End-to-end workflow testing

The test runner provides comprehensive reporting with success rates, security assessments, and actionable recommendations.

## Important Notes

- XML-extracted data receives absolute maximum priority weighting in all analysis
- The system exports prompts to `prompts_export/` directory for manual AI model usage
- GIS-specific categories and responses are tailored for Esri ArcGIS ecosystem
- Comprehensive test coverage ensures reliability and security compliance