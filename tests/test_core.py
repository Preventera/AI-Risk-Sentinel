"""
Tests for AI Risk Sentinel core components.
"""

import pytest
from ai_risk_sentinel.core.gap_detector import GapDetector
from ai_risk_sentinel.models.risk import MITCategory, Risk, RiskSource, SeverityLevel


class TestGapDetector:
    """Tests for GapDetector component."""
    
    def test_init_with_reference_data(self):
        """Test initialization with reference data."""
        detector = GapDetector(use_reference_data=True)
        assert len(detector._catalog_data) == 7
        assert len(detector._incident_data) == 7
    
    def test_init_without_reference_data(self):
        """Test initialization without reference data."""
        detector = GapDetector(use_reference_data=False)
        assert len(detector._catalog_data) == 0
        assert len(detector._incident_data) == 0
    
    def test_calculate_bsi_perfect_alignment(self):
        """Test BSI calculation with perfect alignment."""
        detector = GapDetector()
        bsi = detector.calculate_bsi(documented=30.0, incidents=30.0)
        assert bsi == 0.0
    
    def test_calculate_bsi_complete_misalignment(self):
        """Test BSI calculation with complete misalignment."""
        detector = GapDetector()
        bsi = detector.calculate_bsi(documented=0.0, incidents=100.0)
        assert bsi == 1.0
    
    def test_calculate_bsi_partial_gap(self):
        """Test BSI calculation with partial gap."""
        detector = GapDetector()
        bsi = detector.calculate_bsi(documented=4.0, incidents=22.4)
        # BSI = |4 - 22.4| / max(4, 22.4) = 18.4 / 22.4 ≈ 0.82
        assert 0.8 < bsi < 0.85
    
    def test_calculate_bsi_zero_both(self):
        """Test BSI calculation when both are zero."""
        detector = GapDetector()
        bsi = detector.calculate_bsi(documented=0.0, incidents=0.0)
        assert bsi == 0.0
    
    def test_analyze_returns_report(self):
        """Test that analyze returns a valid BlindSpotIndex report."""
        detector = GapDetector()
        report = detector.analyze()
        
        assert report is not None
        assert 0 <= report.global_bsi <= 1
        assert len(report.by_category) == 7
        assert report.catalog_size > 0
        assert report.incident_count > 0
    
    def test_analyze_identifies_high_risk_categories(self):
        """Test that high-risk categories are correctly identified."""
        detector = GapDetector(bsi_threshold=0.15)
        report = detector.analyze()
        
        # Malicious actors should be high risk based on reference data
        assert MITCategory.MALICIOUS_ACTORS in report.high_risk_categories
    
    def test_get_priority_gaps(self):
        """Test priority gap identification."""
        detector = GapDetector()
        gaps = detector.get_priority_gaps(limit=3)
        
        assert len(gaps) <= 3
        assert all("category" in gap for gap in gaps)
        assert all("blind_spot_index" in gap for gap in gaps)
        assert all("priority" in gap for gap in gaps)
    
    def test_load_catalog_data(self):
        """Test loading custom catalog data."""
        detector = GapDetector(use_reference_data=False)
        
        risks = [
            Risk(
                title="Test risk one",
                source=RiskSource.HF_CATALOG,
                mit_category=MITCategory.DISCRIMINATION_TOXICITY,
                severity_potential=SeverityLevel.MODERATE
            ),
            Risk(
                title="Test risk two",
                source=RiskSource.HF_CATALOG,
                mit_category=MITCategory.DISCRIMINATION_TOXICITY,
                severity_potential=SeverityLevel.MODERATE
            ),
            Risk(
                title="Test risk three",
                source=RiskSource.HF_CATALOG,
                mit_category=MITCategory.MALICIOUS_ACTORS,
                severity_potential=SeverityLevel.HIGH
            ),
        ]
        
        detector.load_catalog_data(risks)
        
        # 2 out of 3 are discrimination, 1 is malicious
        assert detector._catalog_data[MITCategory.DISCRIMINATION_TOXICITY] == pytest.approx(66.67, rel=0.01)
        assert detector._catalog_data[MITCategory.MALICIOUS_ACTORS] == pytest.approx(33.33, rel=0.01)


class TestRiskModel:
    """Tests for Risk model."""
    
    def test_risk_creation_minimal(self):
        """Test creating a risk with minimal fields."""
        risk = Risk(
            title="Generates incorrect information",
            source=RiskSource.HF_CATALOG,
            mit_category=MITCategory.MISINFORMATION
        )
        
        assert risk.risk_id is not None
        assert risk.title == "Generates incorrect information"
        assert risk.source == RiskSource.HF_CATALOG
        assert risk.mit_category == MITCategory.MISINFORMATION
        assert risk.validation_status == "pending"
    
    def test_risk_creation_full(self):
        """Test creating a risk with all fields."""
        risk = Risk(
            title="Perpetuates biases in training data",
            description="Model reproduces demographic biases from training corpus",
            source=RiskSource.MIT_REPOSITORY,
            source_id="meta-llama/Llama-3.1-8B",
            model_type="LLM",
            mit_category=MITCategory.DISCRIMINATION_TOXICITY,
            severity_potential=SeverityLevel.HIGH,
            sst_relevance_score=0.8,
            mitigation_exists=True,
            mitigation_description="Apply debiasing techniques"
        )
        
        assert risk.severity_potential == SeverityLevel.HIGH
        assert risk.sst_relevance_score == 0.8
        assert risk.mitigation_exists is True
    
    def test_risk_title_validation_too_short(self):
        """Test that short titles are rejected."""
        with pytest.raises(ValueError):
            Risk(
                title="Test",  # Too short
                source=RiskSource.HF_CATALOG,
                mit_category=MITCategory.MISINFORMATION
            )
    
    def test_risk_sst_relevance_bounds(self):
        """Test SST relevance score bounds."""
        with pytest.raises(ValueError):
            Risk(
                title="Test risk with invalid score",
                source=RiskSource.HF_CATALOG,
                mit_category=MITCategory.MISINFORMATION,
                sst_relevance_score=1.5  # Out of bounds
            )


class TestMITCategories:
    """Tests for MIT category enumeration."""
    
    def test_all_categories_present(self):
        """Test that all 7 MIT categories are defined."""
        categories = list(MITCategory)
        assert len(categories) == 7
    
    def test_category_values(self):
        """Test category string values."""
        assert MITCategory.DISCRIMINATION_TOXICITY.value == "discrimination_toxicity"
        assert MITCategory.MALICIOUS_ACTORS.value == "malicious_actors"
        assert MITCategory.AI_SYSTEM_SAFETY.value == "ai_system_safety"


# Run with: pytest tests/test_core.py -v
