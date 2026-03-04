"""
Dropstab Sync Service
Handles syncing all data types and pushing to moderation queue
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

from .client import dropstab_client
from .parsers import (
    parse_investors,
    parse_unlocks,
    parse_fundraising,
    parse_projects,
    parse_activity
)
from ..common.storage import upsert_with_diff, push_to_moderation

logger = logging.getLogger(__name__)


class DropstabSync:
    """
    Sync service for all Dropstab data.
    - Fetches from API
    - Parses and normalizes
    - Upserts to MongoDB
    - Pushes changes to moderation queue
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.client = dropstab_client
    
    async def sync_investors(self) -> Dict[str, Any]:
        """Sync investors/VCs"""
        logger.info("[Dropstab] Syncing investors...")
        
        raw = await self.client.investors()
        docs = parse_investors(raw)
        
        collection = self.db.intel_investors
        changed = 0
        
        for doc in docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed'] and result['change_type']:
                changed += 1
                await push_to_moderation(
                    self.db, 'dropstab', 'investor',
                    doc['key'], doc, result['change_type']
                )
        
        logger.info(f"[Dropstab] Investors: {len(docs)} total, {changed} changed")
        return {'total': len(docs), 'changed': changed}
    
    async def sync_unlocks(self) -> Dict[str, Any]:
        """Sync token unlocks/vesting"""
        logger.info("[Dropstab] Syncing unlocks...")
        
        # Try both endpoints
        raw = await self.client.vesting()
        if not raw:
            raw = await self.client.unlocks()
        
        docs = parse_unlocks(raw)
        
        collection = self.db.intel_unlocks
        changed = 0
        
        for doc in docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed'] and result['change_type']:
                changed += 1
                await push_to_moderation(
                    self.db, 'dropstab', 'unlock',
                    doc['key'], doc, result['change_type']
                )
        
        logger.info(f"[Dropstab] Unlocks: {len(docs)} total, {changed} changed")
        return {'total': len(docs), 'changed': changed}
    
    async def sync_fundraising(self) -> Dict[str, Any]:
        """Sync funding rounds"""
        logger.info("[Dropstab] Syncing fundraising...")
        
        raw = await self.client.fundraising()
        docs = parse_fundraising(raw)
        
        collection = self.db.intel_fundraising
        changed = 0
        
        for doc in docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed'] and result['change_type']:
                changed += 1
                await push_to_moderation(
                    self.db, 'dropstab', 'fundraising',
                    doc['key'], doc, result['change_type']
                )
        
        logger.info(f"[Dropstab] Fundraising: {len(docs)} total, {changed} changed")
        return {'total': len(docs), 'changed': changed}
    
    async def sync_projects(self) -> Dict[str, Any]:
        """Sync projects"""
        logger.info("[Dropstab] Syncing projects...")
        
        raw = await self.client.projects()
        # Also try discover for new projects
        discover = await self.client.discover()
        if discover:
            raw.extend(discover)
        
        docs = parse_projects(raw)
        
        collection = self.db.intel_projects
        changed = 0
        
        for doc in docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed'] and result['change_type']:
                changed += 1
                await push_to_moderation(
                    self.db, 'dropstab', 'project',
                    doc['key'], doc, result['change_type']
                )
        
        logger.info(f"[Dropstab] Projects: {len(docs)} total, {changed} changed")
        return {'total': len(docs), 'changed': changed}
    
    async def sync_activity(self) -> Dict[str, Any]:
        """Sync activity/news feed"""
        logger.info("[Dropstab] Syncing activity...")
        
        raw = await self.client.activity()
        docs = parse_activity(raw)
        
        collection = self.db.intel_activity
        changed = 0
        
        for doc in docs:
            result = await upsert_with_diff(collection, doc)
            if result['changed'] and result['change_type']:
                changed += 1
                await push_to_moderation(
                    self.db, 'dropstab', 'activity',
                    doc['key'], doc, result['change_type']
                )
        
        logger.info(f"[Dropstab] Activity: {len(docs)} total, {changed} changed")
        return {'total': len(docs), 'changed': changed}
    
    async def sync_all(self) -> Dict[str, Any]:
        """Run full sync of all data types"""
        logger.info("[Dropstab] Starting full sync...")
        
        results = {
            'source': 'dropstab',
            'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
            'syncs': {}
        }
        
        # Sync each type
        try:
            results['syncs']['investors'] = await self.sync_investors()
        except Exception as e:
            logger.error(f"[Dropstab] Investors sync failed: {e}")
            results['syncs']['investors'] = {'error': str(e)}
        
        try:
            results['syncs']['unlocks'] = await self.sync_unlocks()
        except Exception as e:
            logger.error(f"[Dropstab] Unlocks sync failed: {e}")
            results['syncs']['unlocks'] = {'error': str(e)}
        
        try:
            results['syncs']['fundraising'] = await self.sync_fundraising()
        except Exception as e:
            logger.error(f"[Dropstab] Fundraising sync failed: {e}")
            results['syncs']['fundraising'] = {'error': str(e)}
        
        try:
            results['syncs']['projects'] = await self.sync_projects()
        except Exception as e:
            logger.error(f"[Dropstab] Projects sync failed: {e}")
            results['syncs']['projects'] = {'error': str(e)}
        
        try:
            results['syncs']['activity'] = await self.sync_activity()
        except Exception as e:
            logger.error(f"[Dropstab] Activity sync failed: {e}")
            results['syncs']['activity'] = {'error': str(e)}
        
        logger.info(f"[Dropstab] Full sync complete: {results['syncs']}")
        return results
