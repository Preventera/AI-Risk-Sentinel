"""
HF_Crawler Agent
================

Level N1 agent for crawling Hugging Face Hub and extracting model card risk sections.

Part of the AgenticX5 N1 (Collection) layer.
"""

import asyncio
import re
from datetime import datetime
from typing import AsyncGenerator, Optional

import httpx
import structlog
from huggingface_hub import HfApi, ModelCard, ModelCardData

from ai_risk_sentinel.models.risk import (
    MITCategory,
    ModelModality,
    Risk,
    RiskSource,
    SeverityLevel,
)

logger = structlog.get_logger(__name__)


class HFCrawler:
    """
    Crawls Hugging Face Hub to extract risk documentation from model cards.
    
    This agent is responsible for:
    1. Fetching model cards from HF Hub
    2. Extracting risk/limitation sections
    3. Parsing risk statements into structured format
    4. Yielding Risk objects for downstream processing
    
    Example:
        >>> crawler = HFCrawler()
        >>> async for risk in crawler.crawl(limit=100):
        ...     print(f"Found risk: {risk.title}")
    """
    
    # Patterns for identifying risk sections in model cards
    RISK_SECTION_PATTERNS = [
        r"#+\s*(?:risks?|limitations?|biases?|ethical\s+considerations?|known\s+issues?)",
        r"#+\s*(?:out-of-scope\s+use|misuse|intended\s+use)",
        r"\*\*(?:risks?|limitations?|biases?)\*\*",
    ]
    
    # Keywords indicating risk content
    RISK_KEYWORDS = [
        "bias", "biased", "discriminat", "toxic", "harmful", "hallucin",
        "misinformation", "false", "incorrect", "privacy", "security",
        "malicious", "misuse", "unsafe", "danger", "risk", "limitation",
        "fail", "error", "inaccura", "unreliab"
    ]
    
    # Model type inference patterns
    MODEL_TYPE_PATTERNS = {
        "LLM": ["llama", "gpt", "mistral", "phi", "qwen", "falcon", "gemma", "yi"],
        "Vision": ["clip", "vit", "resnet", "yolo", "dino", "sam", "segment"],
        "Audio": ["whisper", "wav2vec", "hubert", "speecht5"],
        "Multimodal": ["llava", "blip", "flamingo", "kosmos"],
        "Encoder": ["bert", "roberta", "electra", "deberta", "xlm"],
        "Diffusion": ["stable-diffusion", "sdxl", "dall-e", "midjourney"],
    }
    
    def __init__(
        self,
        hf_token: Optional[str] = None,
        rate_limit: float = 1.0,
        batch_size: int = 100,
    ):
        """
        Initialize the HF Crawler.
        
        Args:
            hf_token: Hugging Face API token (optional, for private repos)
            rate_limit: Minimum seconds between API requests
            batch_size: Number of models to fetch per API call
        """
        self.hf_api = HfApi(token=hf_token)
        self.rate_limit = rate_limit
        self.batch_size = batch_size
        self._last_request_time = 0.0
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE | re.MULTILINE)
            for p in self.RISK_SECTION_PATTERNS
        ]
    
    async def _rate_limit_wait(self) -> None:
        """Wait to respect rate limiting."""
        now = datetime.now().timestamp()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit:
            await asyncio.sleep(self.rate_limit - elapsed)
        self._last_request_time = datetime.now().timestamp()
    
    async def crawl(
        self,
        limit: Optional[int] = None,
        model_type: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> AsyncGenerator[Risk, None]:
        """
        Crawl HF Hub and yield Risk objects.
        
        Args:
            limit: Maximum number of models to process
            model_type: Filter by model type (e.g., "text-generation")
            since: Only fetch models updated since this date
            
        Yields:
            Risk objects extracted from model cards
        """
        logger.info(
            "Starting HF crawl",
            limit=limit,
            model_type=model_type,
            since=since
        )
        
        processed = 0
        risks_found = 0
        
        try:
            # Fetch models from HF Hub
            models = self.hf_api.list_models(
                sort="lastModified",
                direction=-1,
                limit=limit or 1000,
                pipeline_tag=model_type,
                cardData=True,
            )
            
            for model_info in models:
                if limit and processed >= limit:
                    break
                
                await self._rate_limit_wait()
                
                try:
                    # Extract risks from model card
                    async for risk in self._process_model(model_info):
                        risks_found += 1
                        yield risk
                    
                    processed += 1
                    
                    if processed % 100 == 0:
                        logger.info(
                            "Crawl progress",
                            processed=processed,
                            risks_found=risks_found
                        )
                        
                except Exception as e:
                    logger.warning(
                        "Error processing model",
                        model_id=model_info.id,
                        error=str(e)
                    )
                    continue
        
        except Exception as e:
            logger.error("Crawl failed", error=str(e))
            raise
        
        logger.info(
            "Crawl complete",
            processed=processed,
            risks_found=risks_found
        )
    
    async def _process_model(self, model_info) -> AsyncGenerator[Risk, None]:
        """
        Process a single model and extract risks.
        
        Args:
            model_info: Model info from HF API
            
        Yields:
            Risk objects extracted from this model's card
        """
        model_id = model_info.id
        
        try:
            # Load model card
            card = ModelCard.load(model_id)
            card_text = card.text if hasattr(card, 'text') else str(card)
            
            # Extract risk sections
            risk_sections = self._extract_risk_sections(card_text)
            
            if not risk_sections:
                return
            
            # Parse risk statements
            model_type = self._infer_model_type(model_id)
            modality = self._infer_modality(model_info)
            
            for section_text in risk_sections:
                for risk_statement in self._parse_risk_statements(section_text):
                    # Classify the risk
                    category = self._classify_risk(risk_statement)
                    
                    risk = Risk(
                        title=risk_statement[:200],  # Truncate if too long
                        description=section_text[:2000] if len(section_text) > 200 else None,
                        source=RiskSource.HF_CATALOG,
                        source_id=model_id,
                        model_type=model_type,
                        modality_input=modality,
                        modality_output=modality,
                        mit_category=category,
                        severity_potential=SeverityLevel.MODERATE,
                        sst_relevance_score=self._calculate_sst_relevance(risk_statement),
                    )
                    
                    yield risk
                    
        except Exception as e:
            logger.debug(
                "Could not process model card",
                model_id=model_id,
                error=str(e)
            )
    
    def _extract_risk_sections(self, card_text: str) -> list[str]:
        """Extract risk-related sections from model card text."""
        sections = []
        
        for pattern in self._compiled_patterns:
            matches = pattern.finditer(card_text)
            for match in matches:
                # Get text following the header
                start = match.end()
                # Find next header or end of text
                next_header = re.search(r'\n#+\s', card_text[start:])
                end = start + next_header.start() if next_header else len(card_text)
                
                section = card_text[start:end].strip()
                if section and len(section) > 20:
                    sections.append(section)
        
        return sections
    
    def _parse_risk_statements(self, section_text: str) -> list[str]:
        """Parse individual risk statements from a section."""
        statements = []
        
        # Split by bullet points or numbered lists
        lines = re.split(r'\n\s*[-*•]\s*|\n\s*\d+\.\s*', section_text)
        
        for line in lines:
            line = line.strip()
            # Filter out short lines and headers
            if len(line) > 30 and not line.startswith('#'):
                # Check if line contains risk keywords
                if any(kw in line.lower() for kw in self.RISK_KEYWORDS):
                    # Clean and format
                    statement = self._format_risk_statement(line)
                    if statement:
                        statements.append(statement)
        
        # If no bullet points found, treat whole section as one statement
        if not statements and len(section_text) > 30:
            statement = self._format_risk_statement(section_text[:500])
            if statement:
                statements.append(statement)
        
        return statements
    
    def _format_risk_statement(self, text: str) -> Optional[str]:
        """Format a risk statement to Verb + Object format."""
        text = text.strip()
        
        # Remove markdown formatting
        text = re.sub(r'\*+', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure it starts with a verb (simple heuristic)
        first_word = text.split()[0].lower() if text.split() else ""
        
        # Common starting patterns to normalize
        if text.lower().startswith(('the model', 'this model')):
            text = text[text.find(' ', 5) + 1:]  # Remove "The model"
        elif text.lower().startswith('it '):
            text = text[3:]
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text if len(text) > 20 else None
    
    def _classify_risk(self, statement: str) -> MITCategory:
        """Classify a risk statement into MIT category."""
        statement_lower = statement.lower()
        
        # Simple keyword-based classification
        if any(kw in statement_lower for kw in ['bias', 'discriminat', 'stereotyp', 'unfair']):
            return MITCategory.DISCRIMINATION_TOXICITY
        elif any(kw in statement_lower for kw in ['toxic', 'offensive', 'hate', 'harmful content']):
            return MITCategory.DISCRIMINATION_TOXICITY
        elif any(kw in statement_lower for kw in ['hallucin', 'incorrect', 'false', 'misinform', 'inaccura']):
            return MITCategory.MISINFORMATION
        elif any(kw in statement_lower for kw in ['malicious', 'misuse', 'fraud', 'scam', 'deepfake']):
            return MITCategory.MALICIOUS_ACTORS
        elif any(kw in statement_lower for kw in ['privacy', 'leak', 'personal data', 'security']):
            return MITCategory.PRIVACY_SECURITY
        elif any(kw in statement_lower for kw in ['overrel', 'automat', 'human oversight', 'judgment']):
            return MITCategory.HUMAN_COMPUTER_INTERACTION
        elif any(kw in statement_lower for kw in ['environment', 'energy', 'carbon', 'job', 'economic']):
            return MITCategory.SOCIOECONOMIC_ENVIRONMENTAL
        else:
            return MITCategory.AI_SYSTEM_SAFETY  # Default
    
    def _infer_model_type(self, model_id: str) -> str:
        """Infer model type from model ID."""
        model_id_lower = model_id.lower()
        
        for model_type, patterns in self.MODEL_TYPE_PATTERNS.items():
            if any(p in model_id_lower for p in patterns):
                return model_type
        
        return "Unknown"
    
    def _infer_modality(self, model_info) -> Optional[ModelModality]:
        """Infer modality from model info."""
        pipeline_tag = getattr(model_info, 'pipeline_tag', '') or ''
        
        if 'text' in pipeline_tag:
            return ModelModality.TEXT
        elif 'image' in pipeline_tag or 'vision' in pipeline_tag:
            return ModelModality.IMAGE
        elif 'audio' in pipeline_tag or 'speech' in pipeline_tag:
            return ModelModality.AUDIO
        elif 'video' in pipeline_tag:
            return ModelModality.VIDEO
        elif 'multimodal' in pipeline_tag:
            return ModelModality.MULTIMODAL
        
        return None
    
    def _calculate_sst_relevance(self, statement: str) -> float:
        """Calculate SST relevance score for a risk statement."""
        statement_lower = statement.lower()
        
        # SST-relevant keywords
        sst_keywords = {
            'high': ['safety', 'injury', 'accident', 'hazard', 'worker', 'health', 
                    'occupational', 'workplace', 'equipment', 'machine'],
            'medium': ['decision', 'judgment', 'oversight', 'critical', 'medical',
                      'diagnosis', 'automation', 'control', 'monitoring'],
            'low': ['bias', 'fairness', 'privacy', 'security', 'misinformation']
        }
        
        score = 0.0
        
        for kw in sst_keywords['high']:
            if kw in statement_lower:
                score += 0.3
        
        for kw in sst_keywords['medium']:
            if kw in statement_lower:
                score += 0.15
        
        for kw in sst_keywords['low']:
            if kw in statement_lower:
                score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def fetch_recent(
        self,
        limit: int = 100,
        with_risks: bool = True
    ) -> list[dict]:
        """
        Fetch recent models with optional risk filtering.
        
        Args:
            limit: Number of models to fetch
            with_risks: Only return models with risk sections
            
        Returns:
            List of model info dictionaries
        """
        models = []
        
        async for risk in self.crawl(limit=limit * 2 if with_risks else limit):
            model_id = risk.source_id
            if model_id and model_id not in [m.get('id') for m in models]:
                models.append({
                    'id': model_id,
                    'model_type': risk.model_type,
                    'has_risks': True,
                    'risk_count': 1
                })
            
            if len(models) >= limit:
                break
        
        return models
