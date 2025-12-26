"""
Risk Catalog
============

Core component for managing the AI risk catalog.

Provides:
- Loading and saving risks
- Searching and filtering
- Vector similarity search
"""

from typing import Optional
from uuid import UUID

import structlog

from ai_risk_sentinel.models import Risk, MITCategory, RiskSource

logger = structlog.get_logger(__name__)


class RiskCatalog:
    """
    Manages the AI risk catalog.
    
    In production, this interfaces with PostgreSQL + pgvector.
    For development/testing, can use in-memory storage.
    
    Example:
        >>> catalog = RiskCatalog()
        >>> risks = catalog.search("deepfake fraud")
        >>> print(f"Found {len(risks)} related risks")
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the risk catalog.
        
        Args:
            database_url: PostgreSQL connection string (optional)
        """
        self._database_url = database_url
        self._in_memory: dict[UUID, Risk] = {}
        
        logger.info(
            "Risk catalog initialized",
            mode="database" if database_url else "in-memory"
        )
    
    def add(self, risk: Risk) -> Risk:
        """
        Add a new risk to the catalog.
        
        Args:
            risk: Risk object to add
            
        Returns:
            The added risk with any generated fields
        """
        self._in_memory[risk.risk_id] = risk
        logger.info("Risk added", risk_id=str(risk.risk_id), title=risk.title)
        return risk
    
    def get(self, risk_id: UUID) -> Optional[Risk]:
        """
        Get a risk by ID.
        
        Args:
            risk_id: UUID of the risk
            
        Returns:
            Risk object if found, None otherwise
        """
        return self._in_memory.get(risk_id)
    
    def search(
        self,
        query: Optional[str] = None,
        category: Optional[MITCategory] = None,
        source: Optional[RiskSource] = None,
        limit: int = 20
    ) -> list[Risk]:
        """
        Search risks with optional filters.
        
        Args:
            query: Text search query
            category: Filter by MIT category
            source: Filter by risk source
            limit: Maximum results to return
            
        Returns:
            List of matching risks
        """
        results = list(self._in_memory.values())
        
        # Apply filters
        if category:
            results = [r for r in results if r.mit_category == category]
        
        if source:
            results = [r for r in results if r.source == source]
        
        if query:
            query_lower = query.lower()
            results = [
                r for r in results
                if query_lower in r.title.lower()
                or (r.description and query_lower in r.description.lower())
            ]
        
        return results[:limit]
    
    def count(self) -> int:
        """Get total number of risks in catalog."""
        return len(self._in_memory)
    
    def get_by_category(self) -> dict[MITCategory, int]:
        """Get count of risks per MIT category."""
        counts = {cat: 0 for cat in MITCategory}
        for risk in self._in_memory.values():
            counts[risk.mit_category] += 1
        return counts
    
    # Future: Vector similarity search
    # def search_similar(self, embedding: list[float], limit: int = 10) -> list[Risk]:
    #     """Search for similar risks using vector embeddings."""
    #     pass


__all__ = ["RiskCatalog"]
