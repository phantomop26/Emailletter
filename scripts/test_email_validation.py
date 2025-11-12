#!/usr/bin/env python3
"""
Test script to validate email extraction improvements
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.email_scraper_utils import is_valid_email, filter_valid_emails
import re

def test_email_validation():
    """Test the improved email validation"""
    
    print("🧪 Testing Email Validation Improvements")
    print("=" * 50)
    
    # Test cases with problematic patterns
    test_cases = [
        # Valid emails (should pass)
        ("contact@venue.com", True),
        ("info@restaurant.org", True),
        ("booking@eventspace.net", True),
        ("events@musicvenue.co.uk", True),
        
        # Invalid patterns that were being caught (should fail)
        ("direct-starter-prod@2.8.1", False),
        ("GRAD@20..48", False),
        ("package@1.0.0", False),
        ("build@123", False),
        ("version@3.14.159", False),
        ("test@123.456", False),
        
        # Edge cases
        ("user@domain", False),  # No TLD
        ("user@.com", False),    # No domain
        ("@domain.com", False),  # No user
        ("user.domain.com", False),  # No @
    ]
    
    print("Testing individual email validation:")
    print("-" * 30)
    
    passed = 0
    failed = 0
    
    for email, expected in test_cases:
        result = is_valid_email(email)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} {email:<25} Expected: {expected:<5} Got: {result}")
        
        if result == expected:
            passed += 1
        else:
            failed += 1
    
    print("-" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    # Test batch filtering
    print("\n🔍 Testing Batch Filtering:")
    print("-" * 30)
    
    sample_emails = [
        "contact@venue.com",
        "direct-starter-prod@2.8.1", 
        "info@restaurant.org",
        "GRAD@20..48",
        "booking@eventspace.net",
        "package@1.0.0"
    ]
    
    print("Original emails found:")
    for email in sample_emails:
        print(f"  • {email}")
    
    filtered_emails = filter_valid_emails(sample_emails)
    
    print("\nFiltered valid emails:")
    for email in filtered_emails:
        print(f"  ✅ {email}")
    
    removed_count = len(sample_emails) - len(filtered_emails)
    print(f"\n📊 Removed {removed_count} invalid patterns, kept {len(filtered_emails)} valid emails")
    
    return passed, failed

if __name__ == "__main__":
    passed, failed = test_email_validation()
    
    if failed == 0:
        print("\n🎉 All tests passed! Email validation is working correctly.")
        exit(0)
    else:
        print(f"\n⚠️ {failed} tests failed. Please review the validation logic.")
        exit(1)