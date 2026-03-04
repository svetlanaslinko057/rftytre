"""
Intel API Routes
Endpoints for crypto intelligence data
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/intel", tags=["intel"])


def get_db():
    """Dependency to get database"""
    from server import db
    return db


def get_dropstab_sync():
    """Dependency to get sync service"""
    from server import db
    from ..dropstab.sync import DropstabSync
    return DropstabSync(db)


# ═══════════════════════════════════════════════════════════════
# SYNC ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/sync/dropstab")
async def sync_dropstab_all(sync = Depends(get_dropstab_sync)):
    """Run full Dropstab sync"""
    result = await sync.sync_all()
    return result


@router.post("/sync/dropstab/{entity}")
async def sync_dropstab_entity(
    entity: str,
    sync = Depends(get_dropstab_sync)
):
    """Sync specific entity from Dropstab"""
    if entity == 'investors':
        result = await sync.sync_investors()
    elif entity == 'unlocks':
        result = await sync.sync_unlocks()
    elif entity == 'fundraising':
        result = await sync.sync_fundraising()
    elif entity == 'projects':
        result = await sync.sync_projects()
    elif entity == 'activity':
        result = await sync.sync_activity()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown entity: {entity}")
    
    return {
        'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
        'entity': entity,
        **result
    }


# ═══════════════════════════════════════════════════════════════
# INVESTORS
# ═══════════════════════════════════════════════════════════════

@router.get("/investors")
async def list_investors(
    search: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db = Depends(get_db)
):
    """List investors/VCs"""
    query = {}
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'slug': {'$regex': search, '$options': 'i'}}
        ]
    if tier:
        query['tier'] = tier
    
    cursor = db.intel_investors.find(query, {'_id': 0, 'raw': 0})
    items = await cursor.sort('investments_count', -1).skip(offset).limit(limit).to_list(limit)
    total = await db.intel_investors.count_documents(query)
    
    return {
        'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
        'total': total,
        'items': items
    }


# ═══════════════════════════════════════════════════════════════
# UNLOCKS
# ═══════════════════════════════════════════════════════════════

@router.get("/unlocks")
async def list_unlocks(
    symbol: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db = Depends(get_db)
):
    """List token unlocks"""
    query = {}
    if symbol:
        query['symbol'] = symbol.upper()
    if category:
        query['category'] = category.lower()
    
    cursor = db.intel_unlocks.find(query, {'_id': 0, 'raw': 0})
    items = await cursor.sort('unlock_date', 1).limit(limit).to_list(limit)
    
    return {
        'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
        'count': len(items),
        'items': items
    }


@router.get("/unlocks/upcoming")
async def upcoming_unlocks(
    days: int = Query(30, ge=1, le=180),
    min_percent: Optional[float] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db = Depends(get_db)
):
    """Get upcoming token unlocks"""
    now = int(datetime.now(timezone.utc).timestamp())
    end = now + (days * 86400)
    
    query = {
        'unlock_date': {'$gte': now, '$lte': end}
    }
    if min_percent:
        query['unlock_percent'] = {'$gte': min_percent}
    
    cursor = db.intel_unlocks.find(query, {'_id': 0, 'raw': 0})
    items = await cursor.sort('unlock_date', 1).limit(limit).to_list(limit)
    
    # Add days_until
    for item in items:
        item['days_until'] = (item['unlock_date'] - now) // 86400
    
    return {
        'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
        'days': days,
        'count': len(items),
        'items': items
    }


# ═══════════════════════════════════════════════════════════════
# FUNDRAISING
# ═══════════════════════════════════════════════════════════════

@router.get("/fundraising")
async def list_fundraising(
    symbol: Optional[str] = Query(None),
    round: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db = Depends(get_db)
):
    """List funding rounds"""
    query = {}
    if symbol:
        query['symbol'] = symbol.upper()
    if round:
        query['round'] = {'$regex': round, '$options': 'i'}
    
    cursor = db.intel_fundraising.find(query, {'_id': 0, 'raw': 0})
    items = await cursor.sort('date', -1).limit(limit).to_list(limit)
    
    return {
        'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
        'count': len(items),
        'items': items
    }


@router.get("/fundraising/recent")
async def recent_fundraising(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(50, ge=1, le=200),
    db = Depends(get_db)
):
    """Get recent funding rounds"""
    cutoff = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    
    query = {'date': {'$gte': cutoff}}
    
    cursor = db.intel_fundraising.find(query, {'_id': 0, 'raw': 0})
    items = await cursor.sort('date', -1).limit(limit).to_list(limit)
    
    return {
        'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
        'days': days,
        'count': len(items),
        'items': items
    }


# ═══════════════════════════════════════════════════════════════
# PROJECTS
# ═══════════════════════════════════════════════════════════════

@router.get("/projects")
async def list_projects(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db = Depends(get_db)
):
    """List projects"""
    query = {}
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'symbol': {'$regex': search, '$options': 'i'}}
        ]
    if category:
        query['category'] = {'$regex': category, '$options': 'i'}
    
    cursor = db.intel_projects.find(query, {'_id': 0, 'raw': 0})
    items = await cursor.sort('symbol', 1).skip(offset).limit(limit).to_list(limit)
    total = await db.intel_projects.count_documents(query)
    
    return {
        'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
        'total': total,
        'items': items
    }


@router.get("/projects/discovered")
async def discovered_projects(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(50, ge=1, le=200),
    db = Depends(get_db)
):
    """Get recently discovered/launched projects"""
    cutoff = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    
    query = {
        '$or': [
            {'ico_date': {'$gte': cutoff}},
            {'listing_date': {'$gte': cutoff}}
        ]
    }
    
    cursor = db.intel_projects.find(query, {'_id': 0, 'raw': 0})
    items = await cursor.limit(limit).to_list(limit)
    
    return {
        'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
        'days': days,
        'count': len(items),
        'items': items
    }


# ═══════════════════════════════════════════════════════════════
# ACTIVITY
# ═══════════════════════════════════════════════════════════════

@router.get("/activity")
async def list_activity(
    activity_type: Optional[str] = Query(None, alias='type'),
    project: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db = Depends(get_db)
):
    """List activity/news feed"""
    query = {}
    if activity_type:
        query['type'] = activity_type.lower()
    if project:
        query['projects'] = {'$in': [project.upper()]}
    
    cursor = db.intel_activity.find(query, {'_id': 0, 'raw': 0})
    items = await cursor.sort('date', -1).limit(limit).to_list(limit)
    
    return {
        'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
        'count': len(items),
        'items': items
    }


# ═══════════════════════════════════════════════════════════════
# MODERATION QUEUE
# ═══════════════════════════════════════════════════════════════

@router.get("/moderation")
async def get_moderation_queue(
    entity: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    status: str = Query('pending'),
    limit: int = Query(100, ge=1, le=500),
    db = Depends(get_db)
):
    """Get moderation queue items"""
    query = {'status': status}
    if entity:
        query['entity'] = entity
    if source:
        query['source'] = source
    
    cursor = db.moderation_queue.find(query, {'_id': 0})
    items = await cursor.sort('created_at', -1).limit(limit).to_list(limit)
    
    return {
        'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
        'count': len(items),
        'items': items
    }


@router.post("/moderation/{key}/approve")
async def approve_moderation(
    key: str,
    db = Depends(get_db)
):
    """Approve moderation item"""
    result = await db.moderation_queue.update_one(
        {'key': key},
        {'$set': {'status': 'approved', 'updated_at': datetime.now(timezone.utc)}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {'ok': True, 'key': key, 'status': 'approved'}


@router.post("/moderation/{key}/reject")
async def reject_moderation(
    key: str,
    db = Depends(get_db)
):
    """Reject moderation item"""
    result = await db.moderation_queue.update_one(
        {'key': key},
        {'$set': {'status': 'rejected', 'updated_at': datetime.now(timezone.utc)}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {'ok': True, 'key': key, 'status': 'rejected'}


# ═══════════════════════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════════════════════

@router.get("/stats")
async def intel_stats(db = Depends(get_db)):
    """Get intel layer statistics"""
    return {
        'ts': int(datetime.now(timezone.utc).timestamp() * 1000),
        'collections': {
            'investors': await db.intel_investors.count_documents({}),
            'unlocks': await db.intel_unlocks.count_documents({}),
            'fundraising': await db.intel_fundraising.count_documents({}),
            'projects': await db.intel_projects.count_documents({}),
            'activity': await db.intel_activity.count_documents({}),
        },
        'moderation_pending': await db.moderation_queue.count_documents({'status': 'pending'})
    }
