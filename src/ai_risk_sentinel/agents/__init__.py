"""
AI Risk Sentinel Agents
=======================

Agents for the AgenticX5 architecture.

Levels:
- N1: Collection (HF_Crawler, Incident_Monitor, Regulatory_Tracker)
- N2: Normalization (MIT_Classifier, Deduplicator)
- N3: Analysis (Gap_Detector, Risk_Propagation, SST_Impact_Scorer)
- N4: Recommendation (Checklist_Generator, Compliance_Reporter)
- N5: Orchestration (RiskDoc_Filler, Incident_Correlator, Compliance_Checker)
"""

# Agents will be implemented in separate modules
# This package provides the base agent class and common utilities

from typing import Protocol, runtime_checkable
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger(__name__)


@runtime_checkable
class AgentProtocol(Protocol):
    """Protocol defining the interface for all agents."""
    
    name: str
    level: int
    
    async def run(self) -> dict:
        """Execute the agent's main task."""
        ...
    
    async def health_check(self) -> bool:
        """Check if the agent is operational."""
        ...


class BaseAgent(ABC):
    """
    Base class for all AI Risk Sentinel agents.
    
    Provides common functionality for logging, error handling,
    and audit trail generation.
    """
    
    def __init__(self, name: str, level: int):
        """
        Initialize the agent.
        
        Args:
            name: Human-readable agent name
            level: AgenticX5 level (1-5)
        """
        self.name = name
        self.level = level
        self._run_id: UUID | None = None
        self._started_at: datetime | None = None
        self._items_processed: int = 0
        self._errors: list[str] = []
        
        self.logger = structlog.get_logger(
            agent_name=name,
            agent_level=level
        )
    
    @abstractmethod
    async def run(self) -> dict:
        """
        Execute the agent's main task.
        
        Returns:
            Dictionary with run results and statistics
        """
        pass
    
    async def health_check(self) -> bool:
        """
        Check if the agent is operational.
        
        Override in subclasses to add specific health checks.
        """
        return True
    
    async def _start_run(self) -> UUID:
        """Start a new run and return the run ID."""
        self._run_id = uuid4()
        self._started_at = datetime.utcnow()
        self._items_processed = 0
        self._errors = []
        
        self.logger.info(
            "Agent run started",
            run_id=str(self._run_id)
        )
        
        return self._run_id
    
    async def _end_run(self, status: str = "completed") -> dict:
        """End the current run and return statistics."""
        ended_at = datetime.utcnow()
        duration = (ended_at - self._started_at).total_seconds() if self._started_at else 0
        
        result = {
            "run_id": str(self._run_id),
            "agent_name": self.name,
            "agent_level": self.level,
            "status": status,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "ended_at": ended_at.isoformat(),
            "duration_seconds": duration,
            "items_processed": self._items_processed,
            "errors_count": len(self._errors),
            "errors": self._errors[:10]  # Limit to first 10 errors
        }
        
        self.logger.info(
            "Agent run completed",
            **result
        )
        
        return result
    
    def _log_progress(self, current: int, total: int | None = None) -> None:
        """Log progress during run."""
        self._items_processed = current
        
        if total:
            progress = (current / total) * 100
            self.logger.info(
                "Progress update",
                current=current,
                total=total,
                progress=f"{progress:.1f}%"
            )
        else:
            self.logger.info("Progress update", items_processed=current)
    
    def _log_error(self, error: str, exception: Exception | None = None) -> None:
        """Log an error during run."""
        self._errors.append(error)
        
        if exception:
            self.logger.error(
                error,
                exception=str(exception),
                exception_type=type(exception).__name__
            )
        else:
            self.logger.error(error)


# Placeholder for specific agent implementations
# These will be in separate files: hf_crawler.py, incident_monitor.py, etc.

__all__ = [
    "AgentProtocol",
    "BaseAgent",
]
