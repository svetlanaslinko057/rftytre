"""
Launchpads parser for CryptoRank
"""

from typing import Dict, List, Any, Optional


def parse_launchpads(data: List[Dict]) -> List[Dict]:
    """
    Parse launchpads from CryptoRank.
    
    Expected input format (from /v1/launchpads):
    {
        "key": "binance-launchpad",
        "name": "Binance Launchpad",
        "type": "IEO",
        "projectsCount": 45,
        "totalRaised": 500000000,
        "athRoi": 150.5,
        "avgRoi": 12.3,
        "avgAthRoi": 45.6,
        "links": {...},
        "image": {...}
    }
    
    This data is valuable for:
    - Project scoring (which launchpad?)
    - Historical ROI analysis
    - Launchpad activity tracking
    """
    results = []
    
    for lp in data:
        lp_key = lp.get('key')
        lp_name = lp.get('name')
        
        if not lp_key or not lp_name:
            continue
        
        key = f"cryptorank:launchpad:{lp_key}"
        
        # Parse links
        links = lp.get('links') or {}
        
        doc = {
            'key': key,
            'source': 'cryptorank',
            'source_key': lp_key,
            
            'name': lp_name,
            'slug': lp_key,
            'type': lp.get('type'),  # IEO, IDO, etc.
            
            # Stats - very valuable for launchpad scoring
            'projects_count': lp.get('projectsCount') or lp.get('projects_count') or 0,
            'total_raised': lp.get('totalRaised') or lp.get('total_raised'),
            
            # ROI metrics
            'ath_roi': lp.get('athRoi') or lp.get('ath_roi'),
            'avg_roi': lp.get('avgRoi') or lp.get('avg_roi'),
            'avg_ath_roi': lp.get('avgAthRoi') or lp.get('avg_ath_roi'),
            
            # Links
            'website': links.get('website') if isinstance(links, dict) else None,
            'twitter': links.get('twitter') if isinstance(links, dict) else None,
            
            # Image
            'image': lp.get('image', {}).get('native') if isinstance(lp.get('image'), dict) else None,
            
            'raw': lp
        }
        
        results.append(doc)
    
    return results
