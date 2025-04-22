# Changelog

## [Unreleased] - 2025-04-22
### Added
- Visual architecture diagram (`architecture.puml`) and documentation (`architecture.puml.README.md`).
- Extensive code comments and docstrings for shared utilities in `main.py`.
- Inline comments in `pages/CorrelationTools.py` for data flow and integration.
- Unified asset selection (autocomplete dropdown) and price history caching across all major analytics and calculator tools.
- Created `utils/coin_utils.py` for shared asset/price utilities.
- Improved error handling, tooltips, and user feedback for asset selection in AdvancedCharts, Backtesting, Portfolio, DerivativesCalculator, and CorrelationTools.

### Changed
- Refactored shared data fetching and analytics functions in `main.py` for clarity and maintainability.
- Refactored all relevant pages to use shared utilities for asset selection and price history, replacing free-text with dropdowns.

### Fixed
- Ensured all analytics modules use shared utilities for consistent data and logic.
- Typos and inconsistencies in asset entry across tools.

---

## [Earlier versions]
- See project commit history for previous changes.
