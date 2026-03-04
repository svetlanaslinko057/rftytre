"""
CryptoRank Sync Service
Scrapes data from CryptoRank frontend API (no API key required)
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

from .client import cryptorank_client
from .parsers import (
    parse_funding,
    parse_top_investors,
    parse_unlocks,
    parse_tge_unlocks,
    parse_launchpads,
    parse_categories
)
from ...common.storage import upsert_with_diff, push_to_moderation

logger = logging.getLogger(__name__)


class CryptoRankSync:
    """
    Sync service for CryptoRank data.
    Uses public frontend endpoints - no API key needed.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.client = cryptorank_client
    
    async def sync_funding(self, max_pages: int = 5) -> Dict[str, Any]:
        """
        Sync funding rounds with pagination.
        """
        logger.info("[CryptoRank] Syncing funding rounds...")
        
        all_docs = []
        offset = 0
        limit = 50
        
        for page in range(max_pages):
            response = await self.client.funding(limit=limit, offset=offset)
            data = response.get('data', [])
            
            if not data:
                break
            
            docs = parse_funding(data)
            all_docs.extend(docs)
            
            offset += limit
            total = response.get('total', 0)
            
            logger.debug(f"[CryptoRank] Funding page {page + 1}: {len(data)} items")
            
            if offset >= total or total == 0:
                break
        
        # Upsert to MongoDB
        collection = self.db.intel_fundraising
        changed = 0
        
        for doc in all_docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed'] and result['change_type']:
                changed += 1
                await push_to_moderation(
                    self.db, 'cryptorank', 'fundraising',
                    doc['key'], doc, result['change_type']
                )
        
        logger.info(f"[CryptoRank] Funding: {len(all_docs)} total, {changed} changed")
        return {'total': len(all_docs), 'changed': changed}
    
    async def sync_investors(self) -> Dict[str, Any]:
        """
        Sync top investors list.
        """
        logger.info("[CryptoRank] Syncing investors...")
        
        data = await self.client.top_investors(limit=100)
        docs = parse_top_investors(data)
        
        # Upsert to MongoDB
        collection = self.db.intel_investors
        changed = 0
        
        for doc in docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed'] and result['change_type']:
                changed += 1
                await push_to_moderation(
                    self.db, 'cryptorank', 'investor',
                    doc['key'], doc, result['change_type']
                )
        
        logger.info(f"[CryptoRank] Investors: {len(docs)} total, {changed} changed")
        return {'total': len(docs), 'changed': changed}
    
    async def sync_unlocks(self, max_pages: int = 3) -> Dict[str, Any]:
        """
        Sync token unlocks (vesting + TGE).
        """
        logger.info("[CryptoRank] Syncing token unlocks...")
        
        all_docs = []
        seen_keys = set()
        
        # Fetch vesting unlocks
        offset = 0
        limit = 50
        
        for page in range(max_pages):
            response = await self.client.unlocks(limit=limit, offset=offset)
            data = response.get('data', [])
            
            if not data:
                break
            
            docs = parse_unlocks(data)
            
            for doc in docs:
                if doc['key'] not in seen_keys:
                    all_docs.append(doc)
                    seen_keys.add(doc['key'])
            
            offset += limit
            logger.debug(f"[CryptoRank] Unlocks page {page + 1}: {len(data)} items")
        
        # Also fetch TGE unlocks
        tge_response = await self.client.unlock_tge(limit=50)
        tge_data = tge_response.get('data', [])
        tge_docs = parse_tge_unlocks(tge_data)
        
        for doc in tge_docs:
            if doc['key'] not in seen_keys:
                all_docs.append(doc)
                seen_keys.add(doc['key'])
        
        # Upsert to MongoDB
        collection = self.db.intel_unlocks
        changed = 0
        
        for doc in all_docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed'] and result['change_type']:
                changed += 1
                await push_to_moderation(
                    self.db, 'cryptorank', 'unlock',
                    doc['key'], doc, result['change_type']
                )
        
        logger.info(f"[CryptoRank] Unlocks: {len(all_docs)} total, {changed} changed")
        return {'total': len(all_docs), 'changed': changed}
    
    async def sync_unlock_totals(self) -> Dict[str, Any]:
        """
        Sync market-wide unlock totals (for sell pressure analysis).
        """
        logger.info("[CryptoRank] Syncing unlock totals...")
        
        data = await self.client.unlock_totals()
        
        # Store in separate collection for market metrics
        collection = self.db.market_unlocks
        changed = 0
        
        for item in data:
            date = item.get('timePoint')
            unlock_usd = item.get('usdUnlock', 0)
            
            if not date:
                continue
            
            doc = {
                'key': f"cryptorank:market_unlock:{date}",
                'date': date,
                'unlock_usd': unlock_usd,
                'source': 'cryptorank'
            }
            
            result = await upsert_with_diff(collection, doc)
            if result['changed']:
                changed += 1
        
        logger.info(f"[CryptoRank] Unlock totals: {len(data)} total, {changed} changed")
        return {'total': len(data), 'changed': changed}
    
    async def sync_launchpads(self) -> Dict[str, Any]:
        """
        Sync launchpad platforms.
        """
        logger.info("[CryptoRank] Syncing launchpads...")
        
        data = await self.client.launchpads(limit=200)
        docs = parse_launchpads(data)
        
        collection = self.db.intel_launchpads
        changed = 0
        
        for doc in docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed']:
                changed += 1
        
        logger.info(f"[CryptoRank] Launchpads: {len(docs)} total, {changed} changed")
        return {'total': len(docs), 'changed': changed}
    
    async def sync_categories(self) -> Dict[str, Any]:
        """
        Sync crypto categories/sectors.
        """
        logger.info("[CryptoRank] Syncing categories...")
        
        data = await self.client.categories()
        docs = parse_categories(data)
        
        collection = self.db.intel_categories
        changed = 0
        
        for doc in docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed']:
                changed += 1
        
        logger.info(f"[CryptoRank] Categories: {len(docs)} total, {changed} changed")
        return {'total': len(docs), 'changed': changed}
    
    async def sync_all(self) -> Dict[str, Any]:
        """
        Run full sync of all CryptoRank data types.
        """
        logger.info("[CryptoRank] Starting full sync...")
        
        results = {
            'source': 'cryptorank',
            'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
            'syncs': {}
        }
        
        sync_tasks = [
            ('funding', self.sync_funding),
            ('investors', self.sync_investors),
            ('unlocks', self.sync_unlocks),
            ('unlock_totals', self.sync_unlock_totals),
            ('launchpads', self.sync_launchpads),
            ('categories', self.sync_categories),
        ]
        
        for name, sync_func in sync_tasks:
            try:
                results['syncs'][name] = await sync_func()
            except Exception as e:
                logger.error(f"[CryptoRank] {name} sync failed: {e}")
                results['syncs'][name] = {'error': str(e)}
        
        logger.info(f"[CryptoRank] Full sync complete")
        return results
