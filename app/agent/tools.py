"""Tool definitions and execution for the Production Analyst agent."""
from typing import Any, Dict
import pandas as pd
import json

from analysis.production import (
    analyze_failure_rates,
    identify_risk_factors,
    get_high_risk_machines,
    analyze_failure_types
)
from analysis.visualizations import (
    create_failure_rate_by_type_chart,
    create_risk_factors_chart,
    create_failure_distribution_chart,
    create_machine_comparison_chart
)


# Tool definitions for Ollama function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "analyze_data",
            "description": "Run statistical analysis on the production dataset. Use this to get failure rates, identify risk factors, find high-risk machines, or analyze failure types.",
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "enum": ["failure_rates", "risk_factors", "high_risk_machines", "failure_types", "all"],
                        "description": "Type of analysis to run. Use 'all' for comprehensive analysis."
                    }
                },
                "required": ["analysis_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_chart",
            "description": "Generate a visualization chart. Use this to create visual representations of the data analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "enum": ["failure_by_type", "risk_factors", "failure_distribution", "machine_comparison"],
                        "description": "Type of chart to generate"
                    }
                },
                "required": ["chart_type"]
            }
        }
    }
]


def execute_tool(
    tool_name: str,
    tool_args: Dict[str, Any],
    df: pd.DataFrame,
    analysis_cache: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a tool and return the result.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments for the tool
        df: The DataFrame to analyze
        analysis_cache: Cache for storing analysis results

    Returns:
        Dict with 'type' and either 'data', 'image', or 'error'
    """
    try:
        if tool_name == "analyze_data":
            analysis_type = tool_args.get("analysis_type", "all")

            if analysis_type == "all":
                result = {
                    "failure_rates": analyze_failure_rates(df),
                    "risk_factors": identify_risk_factors(df),
                    "high_risk_machines": get_high_risk_machines(df),
                    "failure_types": analyze_failure_types(df)
                }
                # Cache all results
                analysis_cache.update(result)
            elif analysis_type == "failure_rates":
                result = analyze_failure_rates(df)
                analysis_cache["failure_rates"] = result
            elif analysis_type == "risk_factors":
                result = identify_risk_factors(df)
                analysis_cache["risk_factors"] = result
            elif analysis_type == "high_risk_machines":
                result = get_high_risk_machines(df)
                analysis_cache["high_risk_machines"] = result
            elif analysis_type == "failure_types":
                result = analyze_failure_types(df)
                analysis_cache["failure_types"] = result
            else:
                return {"type": "error", "message": f"Unknown analysis type: {analysis_type}"}

            return {"type": "analysis", "data": result}

        elif tool_name == "create_chart":
            chart_type = tool_args.get("chart_type")
            chart = None

            if chart_type == "failure_by_type":
                chart = create_failure_rate_by_type_chart(df)
            elif chart_type == "risk_factors":
                # Use cached risk factors if available
                risk_factors = analysis_cache.get("risk_factors") or identify_risk_factors(df)
                chart = create_risk_factors_chart(risk_factors)
            elif chart_type == "failure_distribution":
                chart = create_failure_distribution_chart(df)
            elif chart_type == "machine_comparison":
                chart = create_machine_comparison_chart(df)
            else:
                return {"type": "error", "message": f"Unknown chart type: {chart_type}"}

            if chart is None:
                return {"type": "error", "message": f"Could not generate {chart_type} chart - required columns not found"}

            return {"type": "chart", "image": chart, "chart_type": chart_type}

        else:
            return {"type": "error", "message": f"Unknown tool: {tool_name}"}

    except Exception as e:
        return {"type": "error", "message": f"Tool execution error: {str(e)}"}
