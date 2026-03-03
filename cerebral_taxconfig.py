"""
Configuration module for Cerebral Tax system.
Centralizes all configurable parameters with validation.
"""
import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Event types that trigger cerebral tax
class EventType(Enum):
    """Types of cognitive labor that can be taxed"""
    MARKET_ANALYSIS = "market_analysis"
    CODE_OPTIMIZATION = "code_optimization"
    DATA_PROCESSING = "data_processing"
    STRATEGY_FORMULATION = "strategy_formulation"
    RESEARCH_SYNTHESIS = "research_synthesis"

@dataclass
class BlockchainConfig:
    """Configuration for blockchain interactions"""
    rpc_url: str = "https://polygon-mumbai.g.alchemy.com/v2/demo"  # Testnet
    chain_id: int = 80001  # Polygon Mumbai
    contract_address: Optional[str] = None
    minter_private_key: Optional[str] = None  # In production, use env var + KMS
    gas_limit: int = 300000
    max_gwei: int = 50
    
@dataclass
class FirestoreConfig:
    """Firestore database configuration"""
    collection_prefix: str = "cerebral_tax"
    batch_size: int = 100
    cache_ttl_seconds: int = 3600

@dataclass 
class TaxConfig:
    """Tax calculation parameters"""
    base_fee_wei: int = 1000000000000  # 0.000001 ETH
    complexity_multiplier: Dict[str, float] = None  # type: ignore
    max_fee_wei: int = 10000000000000  # 0.00001 ETH
    
    def __post_init__(self):
        if self.complexity_multiplier is None:
            self.complexity_multiplier = {
                "simple": 1.0,
                "moderate": 2.5,
                "complex": 5.0,
                "expert": 10.0
            }

class CerebralTaxConfig:
    """Main configuration class with validation"""
    
    def __init__(self):
        # Initialize with defaults
        self.blockchain = BlockchainConfig()
        self.firestore = FirestoreConfig()
        self.tax = TaxConfig()
        
        # Environment overrides
        self._load_from_env()
        self._validate()
        
    def _load_from_env(self):
        """Override defaults with environment variables"""
        env_rpc = os.getenv("CTAX_RPC_URL")
        if env_rpc:
            self.blockchain.rpc_url = env_rpc
            
        env_chain_id = os.getenv("CTAX_CHAIN_ID")
        if env_chain_id:
            self.blockchain.chain_id = int(env_chain_id)
            
        # Critical: Private key should NEVER be hardcoded
        env_pk = os.getenv("CTAX_MINTER_PRIVATE_KEY")
        if env_pk:
            self.blockchain.minter_private_key = env_pk
            
    def _validate(self):
        """Validate configuration"""
        if not self.blockchain.rpc_url.startswith(("http://", "https://")):
            raise ValueError("Invalid RPC URL format")
            
        if self.blockchain.minter_private_key and len(self.blockchain.minter_private_key) < 64:
            raise ValueError("Invalid private key length")
            
        if self.tax.base_fee_wei <= 0:
            raise ValueError("Base fee must be positive")
            
    def to_dict(self) -> Dict[str, Any]:
        """Serialize config to dict (excluding sensitive data)"""
        data = {
            "blockchain": asdict(self.blockchain),
            "firestore": asdict(self.firestore),
            "tax": asdict(self.tax)
        }
        # Remove sensitive data
        if data["blockchain"]["minter_private_key"]:
            data["blockchain"]["minter_private_key"] = "***REDACTED***"
        return data

# Global config instance
config = CerebralTaxConfig()

def setup_logging(level=logging.INFO) -> logging.Logger:
    """Configure and return logger for Cerebral Tax system"""
    logger = logging.getLogger("cerebral_tax")
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger