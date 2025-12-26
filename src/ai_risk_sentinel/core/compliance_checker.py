"""
Compliance Checker
==================

Component for checking AI model compliance against regulatory frameworks.

Part of the N4 (Recommendation) level in AgenticX5 architecture.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog

from ai_risk_sentinel.models.risk import MITCategory, Risk
from ai_risk_sentinel.models.metrics import CoverageReport

logger = structlog.get_logger(__name__)


class ComplianceChecker:
    """
    Checks AI model risk documentation against compliance frameworks.
    
    Supported frameworks:
    - EU AI Act (Annexe III - High Risk Systems)
    - NIST AI Risk Management Framework
    - ISO 45001 (extended for AI in OSH)
    
    Example:
        >>> checker = ComplianceChecker()
        >>> report = checker.check_model("meta-llama/Llama-3.1-8B")
        >>> print(f"EU AI Act Compliant: {report.eu_ai_act_compliant}")
        >>> checker.export_evidence_pack(report, "./evidence/")
    """
    
    # EU AI Act Annexe III High-Risk Categories
    EU_AI_ACT_REQUIRED_CATEGORIES = [
        MITCategory.DISCRIMINATION_TOXICITY,
        MITCategory.AI_SYSTEM_SAFETY,
        MITCategory.PRIVACY_SECURITY,
        MITCategory.HUMAN_COMPUTER_INTERACTION,
    ]
    
    # NIST AI RMF Core Functions mapping
    NIST_REQUIREMENTS = {
        "GOVERN": [MITCategory.SOCIOECONOMIC_ENVIRONMENTAL],
        "MAP": [MITCategory.AI_SYSTEM_SAFETY, MITCategory.HUMAN_COMPUTER_INTERACTION],
        "MEASURE": [MITCategory.DISCRIMINATION_TOXICITY, MITCategory.MISINFORMATION],
        "MANAGE": [MITCategory.MALICIOUS_ACTORS, MITCategory.PRIVACY_SECURITY],
    }
    
    # Minimum coverage thresholds
    EU_AI_ACT_THRESHOLD = 0.75  # 75% of required categories
    NIST_THRESHOLD = 0.60  # 60% of functions covered
    
    def __init__(self):
        """Initialize the Compliance Checker."""
        self._risk_catalog: dict[str, list[Risk]] = {}
    
    def load_model_risks(self, model_id: str, risks: list[Risk]) -> None:
        """
        Load risks associated with a specific model.
        
        Args:
            model_id: Hugging Face model ID
            risks: List of Risk objects for this model
        """
        self._risk_catalog[model_id] = risks
        logger.info("Loaded risks for model", model_id=model_id, risk_count=len(risks))
    
    def check_model(
        self,
        model_id: str,
        frameworks: Optional[list[str]] = None
    ) -> CoverageReport:
        """
        Check a model's risk documentation against compliance frameworks.
        
        Args:
            model_id: Hugging Face model ID
            frameworks: List of frameworks to check (default: all)
            
        Returns:
            CoverageReport with compliance status and recommendations
        """
        frameworks = frameworks or ["EU_AI_ACT", "NIST_AI_RMF"]
        
        logger.info(
            "Checking compliance",
            model_id=model_id,
            frameworks=frameworks
        )
        
        # Get risks for this model
        risks = self._risk_catalog.get(model_id, [])
        
        # Determine model type from ID
        model_type = self._infer_model_type(model_id)
        
        # Get covered categories
        covered_categories = set()
        for risk in risks:
            covered_categories.add(risk.mit_category)
        
        # Calculate missing categories
        all_categories = set(MITCategory)
        missing_categories = all_categories - covered_categories
        
        # Check EU AI Act compliance
        eu_compliant = self._check_eu_ai_act(covered_categories)
        
        # Check NIST AI RMF compliance
        nist_compliant = self._check_nist_rmf(covered_categories)
        
        # Generate priority gaps
        priority_gaps = self._generate_priority_gaps(
            model_id,
            model_type,
            list(missing_categories)
        )
        
        # Calculate coverage ratio
        coverage_ratio = len(covered_categories) / len(all_categories)
        
        report = CoverageReport(
            model_id=model_id,
            model_type=model_type,
            categories_covered=list(covered_categories),
            categories_missing=list(missing_categories),
            coverage_ratio=round(coverage_ratio, 2),
            priority_gaps=priority_gaps,
            eu_ai_act_compliant=eu_compliant,
            nist_ai_rmf_compliant=nist_compliant,
        )
        
        logger.info(
            "Compliance check complete",
            model_id=model_id,
            coverage=f"{coverage_ratio:.0%}",
            eu_compliant=eu_compliant,
            nist_compliant=nist_compliant
        )
        
        return report
    
    def _check_eu_ai_act(self, covered: set[MITCategory]) -> bool:
        """Check compliance with EU AI Act requirements."""
        required = set(self.EU_AI_ACT_REQUIRED_CATEGORIES)
        covered_required = covered & required
        coverage = len(covered_required) / len(required)
        return coverage >= self.EU_AI_ACT_THRESHOLD
    
    def _check_nist_rmf(self, covered: set[MITCategory]) -> bool:
        """Check compliance with NIST AI RMF requirements."""
        functions_covered = 0
        
        for function_name, required_categories in self.NIST_REQUIREMENTS.items():
            required_set = set(required_categories)
            if covered & required_set:
                functions_covered += 1
        
        coverage = functions_covered / len(self.NIST_REQUIREMENTS)
        return coverage >= self.NIST_THRESHOLD
    
    def _infer_model_type(self, model_id: str) -> str:
        """Infer model type from model ID."""
        model_id_lower = model_id.lower()
        
        if any(x in model_id_lower for x in ["llama", "gpt", "mistral", "phi", "qwen"]):
            return "LLM"
        elif any(x in model_id_lower for x in ["clip", "vit", "resnet", "yolo"]):
            return "Vision"
        elif any(x in model_id_lower for x in ["whisper", "wav2vec"]):
            return "Audio"
        elif any(x in model_id_lower for x in ["bert", "roberta", "t5"]):
            return "Encoder"
        else:
            return "Unknown"
    
    def _generate_priority_gaps(
        self,
        model_id: str,
        model_type: str,
        missing: list[MITCategory]
    ) -> list[dict]:
        """Generate prioritized list of gaps to address."""
        # Priority based on BSI data and regulatory requirements
        priority_order = {
            MITCategory.MALICIOUS_ACTORS: 1,
            MITCategory.PRIVACY_SECURITY: 2,
            MITCategory.MISINFORMATION: 3,
            MITCategory.DISCRIMINATION_TOXICITY: 4,
            MITCategory.AI_SYSTEM_SAFETY: 5,
            MITCategory.HUMAN_COMPUTER_INTERACTION: 6,
            MITCategory.SOCIOECONOMIC_ENVIRONMENTAL: 7,
        }
        
        gaps = []
        for category in missing:
            priority = priority_order.get(category, 99)
            priority_label = "HIGH" if priority <= 2 else "MEDIUM" if priority <= 4 else "LOW"
            
            gaps.append({
                "category": category.value,
                "priority": priority_label,
                "reason": self._get_gap_reason(category, model_type),
                "suggested_risks": self._get_suggested_risks(category, model_type),
                "regulatory_impact": self._get_regulatory_impact(category)
            })
        
        # Sort by priority
        gaps.sort(key=lambda x: ["HIGH", "MEDIUM", "LOW"].index(x["priority"]))
        
        return gaps
    
    def _get_gap_reason(self, category: MITCategory, model_type: str) -> str:
        """Get reason why this gap is important."""
        reasons = {
            MITCategory.MALICIOUS_ACTORS: (
                f"High BSI (0.82) - {model_type} models are increasingly used for fraud and manipulation"
            ),
            MITCategory.PRIVACY_SECURITY: (
                "Required for EU AI Act compliance and data protection regulations"
            ),
            MITCategory.MISINFORMATION: (
                f"{model_type} models can generate convincing false information"
            ),
            MITCategory.DISCRIMINATION_TOXICITY: (
                "Core requirement for responsible AI deployment"
            ),
            MITCategory.AI_SYSTEM_SAFETY: (
                "Fundamental for understanding model limitations"
            ),
            MITCategory.HUMAN_COMPUTER_INTERACTION: (
                "Critical for preventing overreliance in high-stakes contexts"
            ),
            MITCategory.SOCIOECONOMIC_ENVIRONMENTAL: (
                "Increasingly required for sustainability reporting"
            ),
        }
        return reasons.get(category, f"Missing documentation for {category.value}")
    
    def _get_suggested_risks(self, category: MITCategory, model_type: str) -> list[str]:
        """Get suggested risks to document for a category."""
        suggestions = {
            MITCategory.MALICIOUS_ACTORS: [
                "Enables generation of deceptive content for fraud",
                "Facilitates social engineering attacks through realistic outputs",
                "May be used to impersonate individuals without consent",
            ],
            MITCategory.PRIVACY_SECURITY: [
                "May memorize and leak training data",
                "Could expose sensitive information in outputs",
                "Vulnerable to prompt injection attacks",
            ],
            MITCategory.MISINFORMATION: [
                "Generates factually incorrect information",
                "Produces plausible-sounding but false statements",
                "May spread misleading information at scale",
            ],
            MITCategory.DISCRIMINATION_TOXICITY: [
                "Perpetuates biases present in training data",
                "May generate toxic or offensive content",
                "Shows unequal performance across demographic groups",
            ],
            MITCategory.AI_SYSTEM_SAFETY: [
                "Has known limitations on out-of-distribution inputs",
                "Performance degrades under adversarial conditions",
                "Lacks robustness to input perturbations",
            ],
            MITCategory.HUMAN_COMPUTER_INTERACTION: [
                "Increases risk of overreliance in decision-making",
                "Should not replace professional judgment in critical domains",
                "May reduce human agency if used without oversight",
            ],
            MITCategory.SOCIOECONOMIC_ENVIRONMENTAL: [
                "Requires significant computational resources",
                "May contribute to job displacement in certain sectors",
                "Training has substantial environmental footprint",
            ],
        }
        return suggestions.get(category, [f"Document risks related to {category.value}"])
    
    def _get_regulatory_impact(self, category: MITCategory) -> list[str]:
        """Get regulatory frameworks impacted by this gap."""
        impacts = {
            MITCategory.MALICIOUS_ACTORS: ["NIST AI RMF - MANAGE"],
            MITCategory.PRIVACY_SECURITY: ["EU AI Act", "GDPR", "NIST AI RMF - MANAGE"],
            MITCategory.MISINFORMATION: ["EU AI Act", "NIST AI RMF - MEASURE"],
            MITCategory.DISCRIMINATION_TOXICITY: ["EU AI Act", "NIST AI RMF - MEASURE"],
            MITCategory.AI_SYSTEM_SAFETY: ["EU AI Act", "NIST AI RMF - MAP"],
            MITCategory.HUMAN_COMPUTER_INTERACTION: ["EU AI Act", "NIST AI RMF - MAP"],
            MITCategory.SOCIOECONOMIC_ENVIRONMENTAL: ["NIST AI RMF - GOVERN", "CSRD"],
        }
        return impacts.get(category, [])
    
    def export_evidence_pack(
        self,
        report: CoverageReport,
        output_dir: str | Path
    ) -> Path:
        """
        Export an evidence pack for audit purposes.
        
        Args:
            report: CoverageReport to export
            output_dir: Directory to save evidence pack
            
        Returns:
            Path to the exported evidence pack
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        model_slug = report.model_id.replace("/", "_") if report.model_id else "unknown"
        
        pack_dir = output_path / f"evidence_pack_{model_slug}_{timestamp}"
        pack_dir.mkdir(exist_ok=True)
        
        # Export report as JSON
        report_path = pack_dir / "compliance_report.json"
        report_path.write_text(report.model_dump_json(indent=2))
        
        # Export summary as markdown
        summary_path = pack_dir / "summary.md"
        summary_content = self._generate_summary_md(report)
        summary_path.write_text(summary_content)
        
        logger.info(
            "Evidence pack exported",
            path=str(pack_dir),
            model_id=report.model_id
        )
        
        return pack_dir
    
    def _generate_summary_md(self, report: CoverageReport) -> str:
        """Generate markdown summary of compliance report."""
        covered = ", ".join(c.value for c in report.categories_covered) or "None"
        missing = ", ".join(c.value for c in report.categories_missing) or "None"
        
        return f"""# Compliance Report

## Model Information
- **Model ID**: {report.model_id or 'Not specified'}
- **Model Type**: {report.model_type}
- **Analysis Date**: {report.analysis_date.isoformat()}

## Coverage Summary
- **Coverage Ratio**: {report.coverage_ratio:.0%}
- **Categories Covered**: {covered}
- **Categories Missing**: {missing}

## Compliance Status
| Framework | Status |
|-----------|--------|
| EU AI Act | {'✅ Compliant' if report.eu_ai_act_compliant else '❌ Non-Compliant'} |
| NIST AI RMF | {'✅ Compliant' if report.nist_ai_rmf_compliant else '❌ Non-Compliant'} |

## Priority Gaps

{''.join(self._format_gap_md(gap) for gap in report.priority_gaps)}

---
*Generated by AI Risk Sentinel*
"""
    
    def _format_gap_md(self, gap: dict) -> str:
        """Format a single gap as markdown."""
        suggestions = "\n".join(f"  - {s}" for s in gap.get("suggested_risks", []))
        return f"""
### {gap['category']} ({gap['priority']} Priority)

**Reason**: {gap['reason']}

**Suggested Risks to Document**:
{suggestions}

**Regulatory Impact**: {', '.join(gap.get('regulatory_impact', []))}

"""
