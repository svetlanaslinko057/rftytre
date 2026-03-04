"""
Intel Module - Crypto Intelligence Layer

Data sources:
- Dropstab: investors, unlocks, fundraising, projects, activity
- CryptoRank: (planned)

Collections:
- intel_investors
- intel_unlocks  
- intel_fundraising
- intel_projects
- intel_activity
- moderation_queue
"""

from .api.routes import router as intel_router
from .dropstab import DropstabSync, dropstab_client

__all__ = ['intel_router', 'DropstabSync', 'dropstab_client']
