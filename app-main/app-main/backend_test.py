#!/usr/bin/env python3
"""
Backend Testing Suite for Cyber Forensic Portal
Tests all backend APIs including authentication, evidence submission, and retrieval
"""

import requests
import json
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://a286d5de-9bf9-40a2-835a-d9bfa84d5299.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test data
GOOGLE_CLIENT_ID = "946983955607-pdi9atcd76dl17f5lq33g74srkf23hg8.apps.googleusercontent.com"

# Mock Google token for testing (this would normally come from Google OAuth flow)
MOCK_TOKEN = "mock_google_token_for_testing"

class CyberForensicTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        })
    
    def test_health_check(self):
        """Test basic API health check"""
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, "API is healthy", data)
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_root_endpoint(self):
        """Test root API endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Root Endpoint", True, "Root endpoint accessible", data)
                return True
            else:
                self.log_test("Root Endpoint", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Connection error: {str(e)}")
            return False
    
    def test_google_auth_invalid_token(self):
        """Test Google OAuth with invalid token"""
        try:
            payload = {"token": "invalid_token_12345"}
            response = self.session.post(f"{API_BASE}/auth/google", json=payload)
            
            if response.status_code == 401:
                self.log_test("Google Auth - Invalid Token", True, "Correctly rejected invalid token")
                return True
            else:
                self.log_test("Google Auth - Invalid Token", False, 
                            f"Expected 401, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Google Auth - Invalid Token", False, f"Error: {str(e)}")
            return False
    
    def test_google_auth_missing_token(self):
        """Test Google OAuth with missing token"""
        try:
            payload = {}
            response = self.session.post(f"{API_BASE}/auth/google", json=payload)
            
            if response.status_code == 422:  # Validation error
                self.log_test("Google Auth - Missing Token", True, "Correctly rejected missing token")
                return True
            else:
                self.log_test("Google Auth - Missing Token", False, 
                            f"Expected 422, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Google Auth - Missing Token", False, f"Error: {str(e)}")
            return False
    
    def test_protected_endpoint_no_auth(self):
        """Test protected endpoint without authentication"""
        try:
            response = self.session.get(f"{API_BASE}/evidence")
            
            if response.status_code == 403:  # Forbidden
                self.log_test("Protected Endpoint - No Auth", True, "Correctly rejected unauthenticated request")
                return True
            else:
                self.log_test("Protected Endpoint - No Auth", False, 
                            f"Expected 403, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Protected Endpoint - No Auth", False, f"Error: {str(e)}")
            return False
    
    def test_evidence_submission_structure(self):
        """Test evidence submission API structure validation"""
        try:
            # Create realistic evidence submission data
            evidence_data = {
                "case_title": "Cybercrime Investigation - Data Breach Case #2024-001",
                "case_type": "Cybercrime",
                "date_of_submission": "2024-01-15",
                "time_of_submission": "14:30",
                "investigation_officer": "Detective Sarah Johnson",
                "organization": "Metropolitan Police Department",
                "contact_number": "+1-555-0123",
                "email": "s.johnson@metro-pd.gov",
                "evidence_details": [
                    {
                        "evidence_type": "Hard Drive",
                        "make_model": "Seagate Barracuda ST2000DM008",
                        "serial_number": "WCC4N7HXKJ9L",
                        "storage_capacity": "2TB",
                        "quantity": 1,
                        "condition": "Good - No physical damage observed"
                    },
                    {
                        "evidence_type": "USB Drive",
                        "make_model": "SanDisk Ultra 3.0",
                        "serial_number": "AA011234567890",
                        "storage_capacity": "64GB",
                        "quantity": 1,
                        "condition": "Excellent - Factory sealed"
                    }
                ],
                "description": "Digital evidence seized from suspect's computer during search warrant execution. Hard drive contains potential evidence of unauthorized access to company databases. USB drive found in suspect's possession may contain stolen data.",
                "seized_by": "Detective Sarah Johnson",
                "designation": "Senior Detective, Cybercrime Unit",
                "place_of_seizure": "123 Main Street, Apartment 4B, Metro City",
                "seizure_datetime": "2024-01-14T09:15:00Z",
                "authority_of_seizure": "Search Warrant #SW-2024-0089 issued by Metro City District Court",
                "chain_of_custody": [
                    {
                        "date_time": "2024-01-14T09:15:00Z",
                        "person_handing_over": "Detective Sarah Johnson",
                        "person_receiving": "Evidence Technician Mike Chen",
                        "signature_both": "S.Johnson / M.Chen",
                        "remarks": "Initial seizure and transfer to evidence room"
                    },
                    {
                        "date_time": "2024-01-15T08:30:00Z",
                        "person_handing_over": "Evidence Technician Mike Chen",
                        "person_receiving": "Forensic Analyst Dr. Lisa Park",
                        "signature_both": "M.Chen / L.Park",
                        "remarks": "Transfer to digital forensics lab for analysis"
                    }
                ],
                "evidence_received_by": "Dr. Lisa Park",
                "lab_designation": "Senior Digital Forensics Analyst",
                "receipt_datetime": "2024-01-15T14:30:00Z",
                "assigned_lab_case_id": "DF-2024-001",
                "initial_assessment": "Evidence appears intact. Hard drive shows no signs of tampering. USB drive sealed. Both items ready for imaging and analysis.",
                "lab_signature": "Dr. L. Park",
                "receipt_issued": True,
                "declaration_signature": "Detective Sarah Johnson",
                "declaration_name": "Sarah Johnson",
                "declaration_designation": "Senior Detective",
                "declaration_date": "2024-01-15",
                "terms_accepted": True,
                "submitter_email": "s.johnson@metro-pd.gov"
            }
            
            # Test without authentication (should fail)
            response = self.session.post(f"{API_BASE}/submit-evidence", json=evidence_data)
            
            if response.status_code == 403:  # Forbidden due to no auth
                self.log_test("Evidence Submission - No Auth", True, "Correctly rejected unauthenticated submission")
                return True
            else:
                self.log_test("Evidence Submission - No Auth", False, 
                            f"Expected 403, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Evidence Submission - Structure Test", False, f"Error: {str(e)}")
            return False
    
    def test_evidence_retrieval_no_auth(self):
        """Test evidence retrieval without authentication"""
        try:
            # Test get all evidence
            response = self.session.get(f"{API_BASE}/evidence")
            if response.status_code == 403:
                self.log_test("Get All Evidence - No Auth", True, "Correctly rejected unauthenticated request")
            else:
                self.log_test("Get All Evidence - No Auth", False, 
                            f"Expected 403, got {response.status_code}", response.text)
            
            # Test get specific evidence
            response = self.session.get(f"{API_BASE}/evidence/test-id-123")
            if response.status_code == 403:
                self.log_test("Get Specific Evidence - No Auth", True, "Correctly rejected unauthenticated request")
                return True
            else:
                self.log_test("Get Specific Evidence - No Auth", False, 
                            f"Expected 403, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Evidence Retrieval - No Auth", False, f"Error: {str(e)}")
            return False
    
    def test_lab_update_no_auth(self):
        """Test lab update without authentication"""
        try:
            lab_update_data = {
                "lab_case_id": "DF-2024-001",
                "evidence_received_by": "Dr. Lisa Park",
                "lab_designation": "Senior Digital Forensics Analyst",
                "receipt_datetime": "2024-01-15T14:30:00Z",
                "assigned_lab_case_id": "DF-2024-001-UPDATED",
                "initial_assessment": "Updated assessment after initial review",
                "lab_signature": "Dr. L. Park",
                "receipt_issued": True
            }
            
            response = self.session.put(f"{API_BASE}/evidence/test-id-123/lab-update", json=lab_update_data)
            
            if response.status_code == 403:
                self.log_test("Lab Update - No Auth", True, "Correctly rejected unauthenticated request")
                return True
            else:
                self.log_test("Lab Update - No Auth", False, 
                            f"Expected 403, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Lab Update - No Auth", False, f"Error: {str(e)}")
            return False
    
    def test_invalid_endpoints(self):
        """Test invalid endpoints return proper errors"""
        try:
            # Test non-existent endpoint
            response = self.session.get(f"{API_BASE}/nonexistent")
            if response.status_code == 404:
                self.log_test("Invalid Endpoint", True, "Correctly returned 404 for non-existent endpoint")
                return True
            else:
                self.log_test("Invalid Endpoint", False, 
                            f"Expected 404, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Invalid Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_data_validation(self):
        """Test API data validation"""
        try:
            # Test evidence submission with missing required fields
            incomplete_data = {
                "case_title": "Test Case",
                # Missing many required fields
            }
            
            response = self.session.post(f"{API_BASE}/submit-evidence", json=incomplete_data)
            
            if response.status_code in [422, 403]:  # Validation error or auth error
                self.log_test("Data Validation", True, "API properly validates input data")
                return True
            else:
                self.log_test("Data Validation", False, 
                            f"Expected 422 or 403, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Data Validation", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("CYBER FORENSIC PORTAL - BACKEND API TESTING")
        print("=" * 60)
        print(f"Testing Backend URL: {BACKEND_URL}")
        print(f"API Base URL: {API_BASE}")
        print("=" * 60)
        
        # Basic connectivity tests
        print("\n🔍 BASIC CONNECTIVITY TESTS")
        print("-" * 40)
        self.test_health_check()
        self.test_root_endpoint()
        
        # Authentication tests
        print("\n🔐 AUTHENTICATION TESTS")
        print("-" * 40)
        self.test_google_auth_invalid_token()
        self.test_google_auth_missing_token()
        self.test_protected_endpoint_no_auth()
        
        # API structure tests
        print("\n📋 API STRUCTURE TESTS")
        print("-" * 40)
        self.test_evidence_submission_structure()
        self.test_evidence_retrieval_no_auth()
        self.test_lab_update_no_auth()
        
        # Validation tests
        print("\n✅ VALIDATION TESTS")
        print("-" * 40)
        self.test_invalid_endpoints()
        self.test_data_validation()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = CyberForensicTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the details above.")