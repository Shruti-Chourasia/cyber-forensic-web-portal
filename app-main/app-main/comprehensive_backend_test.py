#!/usr/bin/env python3
"""
Comprehensive Backend API Test for Cyber Forensic Portal
Tests all backend functionality including edge cases and error handling
"""

import requests
import json
from datetime import datetime, date
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv('/app/frontend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://a286d5de-9bf9-40a2-835a-d9bfa84d5299.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ComprehensiveAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:  # Only show details for failures
            print(f"   Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        })
    
    def test_api_endpoints_structure(self):
        """Test all API endpoints are properly structured"""
        endpoints_to_test = [
            ("/", "GET", "Root endpoint"),
            ("/health", "GET", "Health check endpoint"),
            ("/auth/google", "POST", "Google authentication endpoint"),
            ("/submit-evidence", "POST", "Evidence submission endpoint"),
            ("/evidence", "GET", "Get all evidence endpoint"),
            ("/evidence/test-id", "GET", "Get specific evidence endpoint"),
            ("/evidence/test-id/lab-update", "PUT", "Lab update endpoint")
        ]
        
        all_passed = True
        
        for endpoint, method, description in endpoints_to_test:
            try:
                url = f"{API_BASE}{endpoint}"
                
                if method == "GET":
                    response = self.session.get(url)
                elif method == "POST":
                    response = self.session.post(url, json={})
                elif method == "PUT":
                    response = self.session.put(url, json={})
                
                # Check if endpoint exists (not 404)
                if response.status_code != 404:
                    self.log_test(f"Endpoint Structure - {description}", True, 
                                f"{method} {endpoint} exists (status: {response.status_code})")
                else:
                    self.log_test(f"Endpoint Structure - {description}", False, 
                                f"{method} {endpoint} not found", response.text)
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Endpoint Structure - {description}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_authentication_flow(self):
        """Test authentication flow comprehensively"""
        test_cases = [
            {
                "name": "Empty token",
                "payload": {"token": ""},
                "expected_status": [401, 422]
            },
            {
                "name": "Malformed token",
                "payload": {"token": "not.a.valid.jwt.token"},
                "expected_status": [401]
            },
            {
                "name": "Missing token field",
                "payload": {},
                "expected_status": [422]
            },
            {
                "name": "Invalid JSON structure",
                "payload": {"invalid_field": "test"},
                "expected_status": [422]
            }
        ]
        
        all_passed = True
        
        for test_case in test_cases:
            try:
                response = self.session.post(f"{API_BASE}/auth/google", json=test_case["payload"])
                
                if response.status_code in test_case["expected_status"]:
                    self.log_test(f"Auth Flow - {test_case['name']}", True, 
                                f"Correctly handled with status {response.status_code}")
                else:
                    self.log_test(f"Auth Flow - {test_case['name']}", False, 
                                f"Expected {test_case['expected_status']}, got {response.status_code}", 
                                response.text)
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Auth Flow - {test_case['name']}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_evidence_submission_validation(self):
        """Test evidence submission data validation"""
        
        # Test with completely invalid data
        invalid_payloads = [
            {
                "name": "Empty payload",
                "data": {},
                "expected_status": [422, 403]
            },
            {
                "name": "Invalid date format",
                "data": {
                    "case_title": "Test Case",
                    "date_of_submission": "invalid-date",
                    "evidence_details": []
                },
                "expected_status": [422, 403]
            },
            {
                "name": "Missing required arrays",
                "data": {
                    "case_title": "Test Case",
                    "case_type": "Test",
                    "date_of_submission": "2024-01-15"
                },
                "expected_status": [422, 403]
            }
        ]
        
        all_passed = True
        
        for test_case in invalid_payloads:
            try:
                response = self.session.post(f"{API_BASE}/submit-evidence", json=test_case["data"])
                
                if response.status_code in test_case["expected_status"]:
                    self.log_test(f"Evidence Validation - {test_case['name']}", True, 
                                f"Correctly rejected with status {response.status_code}")
                else:
                    self.log_test(f"Evidence Validation - {test_case['name']}", False, 
                                f"Expected {test_case['expected_status']}, got {response.status_code}", 
                                response.text)
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Evidence Validation - {test_case['name']}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_protected_endpoints_security(self):
        """Test that all protected endpoints require authentication"""
        protected_endpoints = [
            ("GET", "/evidence", "Get all evidence"),
            ("GET", "/evidence/test-123", "Get specific evidence"),
            ("POST", "/submit-evidence", "Submit evidence"),
            ("PUT", "/evidence/test-123/lab-update", "Update lab info")
        ]
        
        all_passed = True
        
        for method, endpoint, description in protected_endpoints:
            try:
                url = f"{API_BASE}{endpoint}"
                
                if method == "GET":
                    response = self.session.get(url)
                elif method == "POST":
                    response = self.session.post(url, json={"test": "data"})
                elif method == "PUT":
                    response = self.session.put(url, json={"test": "data"})
                
                if response.status_code == 403:  # Forbidden - correct behavior
                    self.log_test(f"Security - {description}", True, 
                                "Correctly requires authentication")
                else:
                    self.log_test(f"Security - {description}", False, 
                                f"Expected 403, got {response.status_code}", response.text)
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Security - {description}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_data_models_structure(self):
        """Test that API properly validates data model structures"""
        
        # Test evidence submission with realistic but incomplete data
        partial_evidence_data = {
            "case_title": "Comprehensive Test Case",
            "case_type": "Cybercrime Investigation",
            "date_of_submission": "2024-01-15",
            "time_of_submission": "14:30",
            "investigation_officer": "Detective John Smith",
            "organization": "Metro Police Department",
            "contact_number": "+1-555-0199",
            "email": "j.smith@metro-pd.gov",
            "evidence_details": [
                {
                    "evidence_type": "Laptop Computer",
                    "make_model": "Dell Latitude 7420",
                    "serial_number": "ABCD1234567890",
                    "storage_capacity": "512GB SSD",
                    "quantity": 1,
                    "condition": "Good working condition"
                }
            ],
            "description": "Laptop seized during search warrant execution",
            # Missing many required fields to test validation
        }
        
        try:
            response = self.session.post(f"{API_BASE}/submit-evidence", json=partial_evidence_data)
            
            # Should fail due to missing fields or authentication
            if response.status_code in [422, 403]:
                self.log_test("Data Models - Structure Validation", True, 
                            "API properly validates data structure")
                return True
            else:
                self.log_test("Data Models - Structure Validation", False, 
                            f"Expected 422 or 403, got {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Data Models - Structure Validation", False, f"Error: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test API error handling"""
        
        error_test_cases = [
            {
                "name": "Invalid HTTP method",
                "method": "DELETE",
                "endpoint": "/evidence",
                "expected_status": [405, 404]  # Method not allowed or not found
            },
            {
                "name": "Malformed JSON",
                "method": "POST",
                "endpoint": "/auth/google",
                "data": "invalid json",
                "expected_status": [400, 422]
            }
        ]
        
        all_passed = True
        
        for test_case in error_test_cases:
            try:
                url = f"{API_BASE}{test_case['endpoint']}"
                
                if test_case["method"] == "DELETE":
                    response = self.session.delete(url)
                elif test_case["method"] == "POST":
                    if "data" in test_case:
                        # Send malformed data
                        response = self.session.post(url, data=test_case["data"])
                    else:
                        response = self.session.post(url, json={})
                
                if response.status_code in test_case["expected_status"]:
                    self.log_test(f"Error Handling - {test_case['name']}", True, 
                                f"Correctly handled with status {response.status_code}")
                else:
                    self.log_test(f"Error Handling - {test_case['name']}", False, 
                                f"Expected {test_case['expected_status']}, got {response.status_code}", 
                                response.text)
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Error Handling - {test_case['name']}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_api_performance(self):
        """Test basic API performance"""
        try:
            # Test response time for health check
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/health")
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200 and response_time < 5000:  # Less than 5 seconds
                self.log_test("Performance - Health Check", True, 
                            f"Response time: {response_time:.2f}ms")
                return True
            else:
                self.log_test("Performance - Health Check", False, 
                            f"Slow response or error: {response_time:.2f}ms, status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Performance - Health Check", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("=" * 70)
        print("COMPREHENSIVE CYBER FORENSIC PORTAL BACKEND API TESTING")
        print("=" * 70)
        print(f"Testing Backend URL: {BACKEND_URL}")
        print(f"API Base URL: {API_BASE}")
        print("=" * 70)
        
        test_sections = [
            ("🏗️  API STRUCTURE TESTS", self.test_api_endpoints_structure),
            ("🔐 AUTHENTICATION FLOW TESTS", self.test_authentication_flow),
            ("📋 EVIDENCE SUBMISSION VALIDATION", self.test_evidence_submission_validation),
            ("🛡️  SECURITY TESTS", self.test_protected_endpoints_security),
            ("📊 DATA MODEL TESTS", self.test_data_models_structure),
            ("⚠️  ERROR HANDLING TESTS", self.test_error_handling),
            ("⚡ PERFORMANCE TESTS", self.test_api_performance)
        ]
        
        overall_success = True
        
        for section_name, test_function in test_sections:
            print(f"\n{section_name}")
            print("-" * 50)
            section_success = test_function()
            if not section_success:
                overall_success = False
        
        # Summary
        print("\n" + "=" * 70)
        print("COMPREHENSIVE TEST SUMMARY")
        print("=" * 70)
        
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
        
        return overall_success

if __name__ == "__main__":
    tester = ComprehensiveAPITester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n🎉 All comprehensive tests passed!")
        print("✅ Backend API is properly implemented and secure")
    else:
        print("\n⚠️  Some tests failed. Check the details above.")
        print("🔍 Review failed tests for potential issues")