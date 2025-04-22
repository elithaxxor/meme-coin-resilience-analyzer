# Meme Coin Resilience Analyzer - Architecture Diagram

This diagram visualizes the integration and data flow of the main modules and shared utilities in the project.

To view the diagram, use a PlantUML renderer (e.g., VSCode PlantUML extension, or https://www.plantuml.com/plantuml/uml/).

@startuml
!theme spacelab

package "main.py" {
  [fetch_coin_history] --> [compute_correlation_matrix]
  [fetch_coin_history] --> [Backtesting]
  [fetch_coin_history] --> [AdvancedCharts]
  [fetch_coin_history] --> [CorrelationTools]
  [fetch_coin_history] --> [VolumeLiquidity]
  [fetch_live_meme_coins] --> [Tokenomics]
  [black_scholes_price] --> [DerivativesCalculator]
  [binomial_tree_price] --> [DerivativesCalculator]
  [monte_carlo_option_price] --> [DerivativesCalculator]
  [kelly_criterion] --> [DerivativesCalculator]
  [black_scholes_greeks] --> [DerivativesCalculator]
}

package "utils/ui.py" {
  [mobile_container] --> [All Pages]
  [mobile_spacer] --> [All Pages]
}

[Education] ..> [All Pages] : "Help/Docs"
[main.py] ..> [utils/ui.py] : "Imports"

@enduml

---

## How to update this diagram
- Add new modules or functions as needed.
- Use the same naming as in the codebase for clarity.
- Regenerate the diagram after major refactoring or new feature integration.
