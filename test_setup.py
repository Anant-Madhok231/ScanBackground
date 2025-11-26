#!/usr/bin/env python3
"""
Quick setup verification script
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    try:
        from models import QueryInputs, ScanResponse, Platform
        print("✓ Models imported successfully")
        
        from scraper_manager import ScraperManager
        print("✓ ScraperManager imported successfully")
        
        from identity_matcher import IdentityMatcher
        print("✓ IdentityMatcher imported successfully")
        
        from risk_analyzer import RiskAnalyzer
        print("✓ RiskAnalyzer imported successfully")
        
        from timeline_builder import TimelineBuilder
        print("✓ TimelineBuilder imported successfully")
        
        # Test scraper loading
        sm = ScraperManager()
        count = sm.get_scraper_count()
        print(f"✓ Loaded {count} scrapers")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("FootprintScan Setup Verification\n")
    success = test_imports()
    if success:
        print("\n✓ All imports successful! The backend should work.")
    else:
        print("\n✗ Some imports failed. Check dependencies.")
    sys.exit(0 if success else 1)

