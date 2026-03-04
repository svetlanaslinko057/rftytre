"""
CryptoRank Sync Service
Handles syncing all data types and pushing to moderation queue

NOTE: Requires CRYPTORANK_API_KEY environment variable.
Get your key at: https://cryptorank.io/public-api
"""

import logging
from typing import Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

from .client import cryptorank_client
from .parsers import (
    parse_funding,
    parse_top_investors,
    parse_unlocks,
    parse_projects,
    parse_launchpads,
    parse_categories
)
from ...common.storage import upsert_with_diff, push_to_moderation

logger = logging.getLogger(__name__)


class CryptoRankSync:
    """
    Sync service for all CryptoRank data.
    - Fetches from API with pagination
    - Parses and normalizes
    - Upserts to MongoDB
    - Pushes changes to moderation queue
    
    Requires CRYPTORANK_API_KEY environment variable.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.client = cryptorank_client
    
    def is_configured(self) -> bool:
        """Check if CryptoRank API is configured"""
        return self.client.is_configured()
    
    async def sync_funding(self, max_pages: int = 5) -> Dict[str, Any]:
        """
        Sync funding rounds with pagination.
        """
        if not self.is_configured():
            return {'error': 'CRYPTORANK_API_KEY not configured', 'total': 0, 'changed': 0}
        
        logger.info("[CryptoRank] Syncing funding rounds...")
        
        all_docs = []
        offset = 0
        limit = 100
        
        for page in range(max_pages):
            response = await self.client.funding(limit=limit, offset=offset)
            data = response.get('data', [])
            
            if not data:
                break
            
            docs = parse_funding(data)
            all_docs.extend(docs)
            
            offset += limit
            total = response.get('total', 0)
            
            logger.debug(f"[CryptoRank] Funding page {page + 1}: {len(data)} items, total: {total}")
            
            if offset >= total:
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
    
    async def sync_investors(self, max_pages: int = 3) -> Dict[str, Any]:
        """
        Sync top investors list.
        """
        logger.info("[CryptoRank] Syncing investors...")
        
        all_docs = []
        offset = 0
        limit = 100
        
        for page in range(max_pages):
            response = await self.client.top_investors(limit=limit, offset=offset)
            data = response.get('data', [])
            
            if not data:
                break
            
            docs = parse_top_investors(data)
            all_docs.extend(docs)
            
            offset += limit
            total = response.get('total', 0)
            
            if offset >= total:
                break
        
        # Upsert to MongoDB
        collection = self.db.intel_investors
        changed = 0
        
        for doc in all_docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed'] and result['change_type']:
                changed += 1
                await push_to_moderation(
                    self.db, 'cryptorank', 'investor',
                    doc['key'], doc, result['change_type']
                )
        
        logger.info(f"[CryptoRank] Investors: {len(all_docs)} total, {changed} changed")
        return {'total': len(all_docs), 'changed': changed}
    
    async def sync_unlocks(self, periods: list = None) -> Dict[str, Any]:
        """
        Sync token unlocks for multiple periods.
        """
        logger.info("[CryptoRank] Syncing token unlocks...")
        
        if periods is None:
            periods = ['1w', '2w', '1m', '3m']
        
        all_docs = []
        seen_keys = set()
        
        for period in periods:
            response = await self.client.unlock_feed(limit=100, period=period)
            data = response.get('data', [])
            
            docs = parse_unlocks(data)
            
            # Dedupe across periods
            for doc in docs:
                if doc['key'] not in seen_keys:
                    all_docs.append(doc)
                    seen_keys.add(doc['key'])
            
            logger.debug(f"[CryptoRank] Unlocks period {period}: {len(data)} items")
        
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
    
    async def sync_projects(self, max_pages: int = 5) -> Dict[str, Any]:
        """
        Sync projects/coins.
        """
        logger.info("[CryptoRank] Syncing projects...")
        
        all_docs = []
        offset = 0
        limit = 100
        
        for page in range(max_pages):
            response = await self.client.coins(limit=limit, offset=offset)
            data = response.get('data', [])
            
            if not data:
                break
            
            docs = parse_projects(data)
            all_docs.extend(docs)
            
            offset += limit
            total = response.get('total', 0)
            
            if offset >= total:
                break
        
        # Upsert to MongoDB
        collection = self.db.intel_projects
        changed = 0
        
        for doc in all_docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed'] and result['change_type']:
                changed += 1
                await push_to_moderation(
                    self.db, 'cryptorank', 'project',
                    doc['key'], doc, result['change_type']
                )
        
        logger.info(f"[CryptoRank] Projects: {len(all_docs)} total, {changed} changed")
        return {'total': len(all_docs), 'changed': changed}
    
    async def sync_launchpads(self) -> Dict[str, Any]:
        """
        Sync launchpads.
        """
        logger.info("[CryptoRank] Syncing launchpads...")
        
        response = await self.client.launchpads(limit=100)
        data = response.get('data', [])
        
        docs = parse_launchpads(data)
        
        # Store in intel_launchpads collection
        collection = self.db.intel_launchpads
        changed = 0
        
        for doc in docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed'] and result['change_type']:
                changed += 1
        
        logger.info(f"[CryptoRank] Launchpads: {len(docs)} total, {changed} changed")
        return {'total': len(docs), 'changed': changed}
    
    async def sync_categories(self) -> Dict[str, Any]:
        """
        Sync categories.
        """
        logger.info("[CryptoRank] Syncing categories...")
        
        response = await self.client.categories(limit=200)
        data = response.get('data', [])
        
        docs = parse_categories(data)
        
        # Store in intel_categories collection
        collection = self.db.intel_categories
        changed = 0
        
        for doc in docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed'] and result['change_type']:
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
        
        # Sync each type with error handling
        sync_tasks = [
            ('funding', self.sync_funding),
            ('investors', self.sync_investors),
            ('unlocks', self.sync_unlocks),
            ('projects', self.sync_projects),
            ('launchpads', self.sync_launchpads),
            ('categories', self.sync_categories),
        ]
        
        for name, sync_func in sync_tasks:
            try:
                results['syncs'][name] = await sync_func()
            except Exception as e:
                logger.error(f"[CryptoRank] {name} sync failed: {e}")
                results['syncs'][name] = {'error': str(e)}
        
        logger.info(f"[CryptoRank] Full sync complete: {results['syncs']}")
        return results
