# Calculateur d'Impôt Progressif (Progressive Tax Calculator)

## Overview

This is a comprehensive French progressive tax calculator web application built with Streamlit. The application calculates income tax based on different tax brackets for multiple years (2022-2025), visualizes the tax breakdown, and generates PDF reports. 

**Key Features:**
- **Simple Calculator**: Calculate taxes with deductions and credits, view breakdowns, download PDF reports
- **Comparison Mode**: Compare tax impacts across 2-3 different income scenarios side-by-side
- **Historical Analysis**: Compare how taxes change for the same income across different years (2022-2025)
- **PDF Reports**: Generate professional tax summary reports with detailed breakdowns
- **Interactive Visualizations**: Pie charts, bar charts, and tables showing tax distribution

Users can input their income, deductions, and credits to see detailed tax calculations including effective tax rates, marginal rates, and visual representations of how their income is taxed across different brackets.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for rapid development of data-driven web applications with minimal frontend code
- **Visualization**: Plotly - provides interactive charts for displaying tax breakdowns across income brackets
- **Layout**: Wide layout configuration to maximize screen real estate for charts and tables

### Report Generation
- **PDF Generation**: ReportLab library handles PDF creation
  - Rationale: Industry-standard Python library for programmatic PDF generation
  - Supports tables, paragraphs, custom styling, and precise layout control
  - Alternative considered: WeasyPrint (HTML-to-PDF) - ReportLab chosen for more direct control over document structure

### Data Model
- **Tax Brackets**: Dictionary-based storage with year as key
  - Each year contains an array of bracket objects with min/max income thresholds and tax rates
  - Uses `float('inf')` for the highest bracket's maximum to represent unlimited upper bound
  - Hardcoded configuration approach chosen for simplicity and data stability
  - Alternative considered: Database storage - rejected due to small, infrequently-changing dataset

### Calculation Engine
- **Progressive Tax Logic**: Fully implemented `calculate_tax()` function with bracket-by-bracket calculation
  - Takes income and year as parameters (supports 2022-2025)
  - Iterates through applicable tax brackets for the selected year
  - Calculates tax owed at each marginal rate
  - Returns total tax amount
  - Supports deductions (reduce taxable income) and credits (reduce final tax)
- **Breakdown Function**: `get_bracket_breakdown()` provides detailed per-bracket analysis
  - Shows how much income falls in each bracket
  - Calculates tax at each rate
  - Formats data for display in tables and charts

### Application Structure
- **Three-tab interface**: All functionality contained in `app.py`
  - **Tab 1 - Simple Calculator**: Income input with deductions/credits, metrics, visualizations, PDF download
  - **Tab 2 - Comparison Mode**: Side-by-side comparison of 2-3 scenarios with adjustable parameters
  - **Tab 3 - Historical Analysis**: Year-over-year comparison (2022-2025) for same income level
- **Single file architecture**: Simplifies deployment and maintenance
- **Entry point**: `main.py` is a placeholder/template file not actively used

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework for the UI
- **plotly**: Interactive visualization library for tax breakdown charts
- **pandas**: Data manipulation and tabular data display
- **reportlab**: PDF generation for downloadable tax reports
- **datetime**: Standard library for timestamp generation in reports

### No External Services
- No database connections
- No third-party APIs
- No authentication systems
- No cloud storage integrations
- Fully self-contained application running locally