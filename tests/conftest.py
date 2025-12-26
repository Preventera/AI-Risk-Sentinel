"""Pytest configuration for AI Risk Sentinel tests."""

import pytest


@pytest.fixture
def gap_detector():
    """Provide a configured GapDetector instance."""
    from ai_risk_sentinel.core.gap_detector import GapDetector

    return GapDetector(use_reference_data=True)


@pytest.fixture
def compliance_checker():
    """Provide a configured ComplianceChecker instance."""
    from ai_risk_sentinel.core.compliance_checker import ComplianceChecker

    return ComplianceChecker()
