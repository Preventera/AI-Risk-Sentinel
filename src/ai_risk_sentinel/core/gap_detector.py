"""
Gap Detector
============

Core component for analyzing blind spots between documented risks and real-world incidents.

This is the heart of the N3 (Analysis) level in AgenticX5 architecture.
"""

from datetime import datetime
from typing import Optional

import structlog

from ai_risk_sentinel.models.risk import MITCategory, Risk
from ai_risk_sentinel.models.metrics import BlindSpotIndex, CategoryMetrics

logger = structlog.get_logger(__name__)


class GapDetector:
    """
    Analyzes gaps between documented AI risks and real-world incidents.
    
    The Gap Detector calculates the Blind Spot Index (BSI) which measures
    how well documented risks align with actual harms observed in the field.
    
    A high BSI indicates that a risk category is under-documented relative
    to its frequency in real-world incidents.
    
    Example:
        >>> detector = GapDetector()
        >>> report = detector.analyze(model_type="vision")
        >>> print(f"Global BSI: {report.global_bsi}")
        >>> for cat in report.high_risk_categories:
        ...     print(f"High risk: {cat}")
    """
    
    # Reference data from AI Model Risk Catalog (Rao et al., 2025)
    # Based on analysis of 460,000 model cards and 869 incidents
    REFERENCE_DOCUMENTED = {
        MITCategory.DISCRIMINATION_TOXICITY: 44.5,
        MITCategory.AI_SYSTEM_SAFETY: 37.3,
        MITCategory.MISINFORMATION: 10.2,
        MITCategory.MALICIOUS_ACTORS: 4.0,
        MITCategory.PRIVACY_SECURITY: 2.9,
        MITCategory.HUMAN_COMPUTER_INTERACTION: 0.6,
        MITCategory.SOCIOECONOMIC_ENVIRONMENTAL: 0.5,
    }
    
    REFERENCE_INCIDENTS = {
        MITCategory.DISCRIMINATION_TOXICITY: 27.5,
        MITCategory.AI_SYSTEM_SAFETY: 23.9,
        MITCategory.MISINFORMATION: 12.9,
        MITCategory.MALICIOUS_ACTORS: 22.4,
        MITCategory.PRIVACY_SECURITY: 8.2,
        MITCategory.HUMAN_COMPUTER_INTERACTION: 1.5,
        MITCategory.SOCIOECONOMIC_ENVIRONMENTAL: 3.6,
    }
    
    DEFAULT_BSI_THRESHOLD = 0.15
    
    def __init__(
        self,
        bsi_threshold: float = DEFAULT_BSI_THRESHOLD,
        use_reference_data: bool = True
    ):
        """
        Initialize the Gap Detector.
        
        Args:
            bsi_threshold: Threshold above which a category is considered high-risk
            use_reference_data: Use reference data from the original study as baseline
        """
        self.bsi_threshold = bsi_threshold
        self.use_reference_data = use_reference_data
        self._catalog_data: dict[MITCategory, float] = {}
        self._incident_data: dict[MITCategory, float] = {}
        
        if use_reference_data:
            self._catalog_data = self.REFERENCE_DOCUMENTED.copy()
            self._incident_data = self.REFERENCE_INCIDENTS.copy()
    
    def load_catalog_data(self, risks: list[Risk]) -> None:
        """
        Load risk distribution from catalog data.
        
        Args:
            risks: List of Risk objects from the catalog
        """
        if not risks:
            logger.warning("No risks provided to load_catalog_data")
            return
        
        # Count risks per category
        category_counts: dict[MITCategory, int] = {cat: 0 for cat in MITCategory}
        for risk in risks:
            category_counts[risk.mit_category] += 1
        
        # Convert to percentages
        total = len(risks)
        self._catalog_data = {
            cat: (count / total) * 100
            for cat, count in category_counts.items()
        }
        
        logger.info(
            "Loaded catalog data",
            total_risks=total,
            categories=len(category_counts)
        )
    
    def load_incident_data(self, incidents: list[dict]) -> None:
        """
        Load incident distribution from AI Incident Database.
        
        Args:
            incidents: List of incident records with 'mit_category' field
        """
        if not incidents:
            logger.warning("No incidents provided to load_incident_data")
            return
        
        # Count incidents per category
        category_counts: dict[MITCategory, int] = {cat: 0 for cat in MITCategory}
        for incident in incidents:
            if "mit_category" in incident:
                try:
                    cat = MITCategory(incident["mit_category"])
                    category_counts[cat] += 1
                except ValueError:
                    continue
        
        # Convert to percentages
        total = len(incidents)
        self._incident_data = {
            cat: (count / total) * 100
            for cat, count in category_counts.items()
        }
        
        logger.info(
            "Loaded incident data",
            total_incidents=total,
            categories=len(category_counts)
        )
    
    def calculate_bsi(self, documented: float, incidents: float) -> float:
        """
        Calculate Blind Spot Index for a category.
        
        BSI = |documented% - incidents%| / max(documented%, incidents%)
        
        A BSI of 0 means perfect alignment.
        A BSI close to 1 means severe misalignment (blind spot).
        
        Args:
            documented: Percentage of documented risks in this category
            incidents: Percentage of real-world incidents in this category
            
        Returns:
            Blind Spot Index between 0 and 1
        """
        if documented == 0 and incidents == 0:
            return 0.0
        
        gap = abs(documented - incidents)
        max_value = max(documented, incidents)
        
        return gap / max_value if max_value > 0 else 0.0
    
    def analyze(
        self,
        model_type: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> BlindSpotIndex:
        """
        Perform gap analysis and generate Blind Spot Index report.
        
        Args:
            model_type: Filter by model type (e.g., "vision", "LLM")
            period_start: Start of analysis period
            period_end: End of analysis period
            
        Returns:
            BlindSpotIndex report with per-category breakdown
        """
        logger.info(
            "Starting gap analysis",
            model_type=model_type,
            period_start=period_start,
            period_end=period_end
        )
        
        category_metrics: list[CategoryMetrics] = []
        high_risk_categories: list[MITCategory] = []
        total_bsi = 0.0
        
        for category in MITCategory:
            documented = self._catalog_data.get(category, 0.0)
            incidents = self._incident_data.get(category, 0.0)
            gap = documented - incidents
            bsi = self.calculate_bsi(documented, incidents)
            
            metrics = CategoryMetrics(
                category=category,
                documented_count=int(documented * 100),  # Placeholder counts
                documented_percentage=documented,
                incident_count=int(incidents * 10),  # Placeholder counts
                incident_percentage=incidents,
                gap=gap,
                blind_spot_index=bsi
            )
            category_metrics.append(metrics)
            total_bsi += bsi
            
            # Check if this is a high-risk category
            # High risk = under-documented (incidents > documented) AND high BSI
            if bsi > self.bsi_threshold and incidents > documented:
                high_risk_categories.append(category)
                logger.warning(
                    "High-risk blind spot detected",
                    category=category.value,
                    bsi=round(bsi, 3),
                    gap=round(gap, 1)
                )
        
        # Calculate global BSI (average across categories)
        global_bsi = total_bsi / len(MITCategory)
        
        # Sort by BSI descending
        category_metrics.sort(key=lambda x: x.blind_spot_index, reverse=True)
        
        report = BlindSpotIndex(
            global_bsi=round(global_bsi, 3),
            documentation_quality_score=15.2,  # From reference data
            by_category=category_metrics,
            high_risk_categories=high_risk_categories,
            threshold=self.bsi_threshold,
            catalog_size=2863,  # Reference from paper
            incident_count=869,
            model_cards_analyzed=64116,
            period_start=period_start,
            period_end=period_end
        )
        
        logger.info(
            "Gap analysis complete",
            global_bsi=report.global_bsi,
            high_risk_count=len(high_risk_categories)
        )
        
        return report
    
    def get_priority_gaps(self, limit: int = 5) -> list[dict]:
        """
        Get the most critical gaps that need attention.
        
        Returns categories where incidents significantly exceed documentation,
        ordered by severity.
        
        Args:
            limit: Maximum number of gaps to return
            
        Returns:
            List of gap descriptions with recommendations
        """
        gaps = []
        
        for category in MITCategory:
            documented = self._catalog_data.get(category, 0.0)
            incidents = self._incident_data.get(category, 0.0)
            bsi = self.calculate_bsi(documented, incidents)
            
            # Only include under-documented categories
            if incidents > documented and bsi > self.bsi_threshold:
                gaps.append({
                    "category": category.value,
                    "blind_spot_index": round(bsi, 3),
                    "gap_points": round(incidents - documented, 1),
                    "priority": "CRITICAL" if bsi > 0.5 else "HIGH" if bsi > 0.3 else "MEDIUM",
                    "recommendation": self._get_recommendation(category, bsi)
                })
        
        # Sort by BSI descending
        gaps.sort(key=lambda x: x["blind_spot_index"], reverse=True)
        
        return gaps[:limit]
    
    def _get_recommendation(self, category: MITCategory, bsi: float) -> str:
        """Generate a recommendation based on category and BSI."""
        recommendations = {
            MITCategory.MALICIOUS_ACTORS: (
                "Document risks related to deepfakes, fraud, social engineering, "
                "and targeted manipulation. Include specific misuse scenarios."
            ),
            MITCategory.MISINFORMATION: (
                "Add explicit warnings about hallucination, false information generation, "
                "and impacts on decision-making in critical domains."
            ),
            MITCategory.PRIVACY_SECURITY: (
                "Document data leakage risks, training data memorization, "
                "and potential for privacy violations."
            ),
            MITCategory.SOCIOECONOMIC_ENVIRONMENTAL: (
                "Include environmental impact (compute resources), "
                "job displacement risks, and equity considerations."
            ),
            MITCategory.HUMAN_COMPUTER_INTERACTION: (
                "Address overreliance risks, loss of human agency, "
                "and unsafe use in high-stakes contexts."
            ),
        }
        
        return recommendations.get(
            category,
            f"Review and document risks in the {category.value} category. "
            f"Current BSI of {bsi:.2f} indicates significant blind spot."
        )
