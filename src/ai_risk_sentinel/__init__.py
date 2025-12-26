"""
AI Risk Sentinel
================

Multi-Agent System for Proactive AI Risk Documentation Analysis and Correction.

Based on the AI Model Risk Catalog (Rao et al., AAAI 2025) and AgenticX5 architecture.

Example usage:
    >>> from ai_risk_sentinel import GapDetector, ComplianceChecker
    >>> 
    >>> # Analyze blind spots for vision models
    >>> detector = GapDetector()
    >>> report = detector.analyze(model_type="vision")
    >>> print(f"Blind Spot Index: {report.blind_spot_index}")
    >>>
    >>> # Check compliance for a specific model
    >>> checker = ComplianceChecker()
    >>> compliance = checker.check_model("meta-llama/Llama-3.1-8B")

For more information, see: https://github.com/Preventera/AI-Risk-Sentinel
"""

from ai_risk_sentinel.core.gap_detector import GapDetector
from ai_risk_sentinel.core.compliance_checker import ComplianceChecker
from ai_risk_sentinel.core.risk_catalog import RiskCatalog
from ai_risk_sentinel.models.risk import Risk, RiskCategory, RiskSource
from ai_risk_sentinel.models.metrics import BlindSpotIndex, CoverageReport

__version__ = "0.1.0"
__author__ = "GenAISafety Team"
__email__ = "team@genaisafety.com"

__all__ = [
    # Core components
    "GapDetector",
    "ComplianceChecker", 
    "RiskCatalog",
    # Models
    "Risk",
    "RiskCategory",
    "RiskSource",
    "BlindSpotIndex",
    "CoverageReport",
    # Version
    "__version__",
]
