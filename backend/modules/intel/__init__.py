"""
Intel Module - Crypto Intelligence Layer

Data sources:
- Dropstab: investors, unlocks, fundraising, projects, activity
- CryptoRank: funding, investors, unlocks, projects, launchpads, categories

Collections:
- intel_investors
- intel_unlocks  
- intel_fundraising
- intel_projects
- intel_activity
- intel_launchpads
- intel_categories
- moderation_queue
"""

from .api.routes import router as intel_router
from .dropstab import DropstabSync, dropstab_client
from .sources.cryptorank import CryptoRankSync, cryptorank_client

__all__ = [
    'intel_router',
    'DropstabSync', 
    'dropstab_client',
    'CryptoRankSync',
    'cryptorank_client'
]
