import unittest
import json
import requests
import time
import tempfile
import os
from unittest.mock import patch
import sys
sys.path.append('src')

from app import app

class TestSecurityValidation(unittest.TestCase):
    """Security tests for the GIS Ticket Management AI Agent"""
    
    def setUp(self):
        """Set up test client"""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.base_url = 'http://localhost:5000'
    
    def test_sql_injection_in_ticket_data(self):
        """Test protection against SQL injection in ticket data"""
        malicious_ticket = {
            'id': "'; DROP TABLE tickets; --",
            'subject': 'Normal subject',
            'description': "'; DELETE FROM users WHERE '1'='1"
        }
        
        response = self.client.post('/api/analyze_ticket',
                                  data=json.dumps(malicious_ticket),
                                  content_type='application/json')
        
        # Should handle malicious input gracefully
        self.assertIn(response.status_code, [200, 400])
        if response.status_code == 200:
            data = json.loads(response.data)
            # Verify no SQL commands in response
            response_text = str(data).lower()
            self.assertNotIn('drop table', response_text)
            self.assertNotIn('delete from', response_text)
    
    def test_xss_protection_in_responses(self):
        """Test protection against XSS attacks in responses"""
        xss_ticket = {
            'id': 'XSS-001',
            'subject': '<script>alert("XSS")</script>',
            'description': '<img src="x" onerror="alert(\'XSS\')">'
        }
        
        response = self.client.post('/api/analyze_ticket',
                                  data=json.dumps(xss_ticket),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify no script tags in response
        response_text = str(data).lower()
        self.assertNotIn('<script>', response_text)
        self.assertNotIn('onerror=', response_text)
    
    def test_file_upload_size_limit(self):
        """Test file upload size limitations"""
        # Create a large dummy file (simulate oversized XML)
        large_content = 'x' * (10 * 1024 * 1024)  # 10MB
        
        with tempfile.NamedTemporaryFile(suffix='.xml', delete=False) as temp_file:
            temp_file.write(large_content.encode())
            temp_file.flush()
            
            try:
                with open(temp_file.name, 'rb') as f:
                    response = self.client.post('/api/import_xml',
                                              data={'xml_file': (f, 'large_file.xml')},
                                              content_type='multipart/form-data')
                
                # Should handle large files appropriately
                self.assertIn(response.status_code, [200, 400, 413])
            finally:
                os.unlink(temp_file.name)
    
    def test_malicious_xml_content(self):
        """Test protection against XML bombs and malicious XML"""
        # XML bomb attempt
        xml_bomb = '''<?xml version="1.0"?>
        <!DOCTYPE lolz [
          <!ENTITY lol "lol">
          <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
          <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
        ]>
        <tickets><ticket><id>&lol3;</id></ticket></tickets>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as temp_file:
            temp_file.write(xml_bomb)
            temp_file.flush()
            
            try:
                with open(temp_file.name, 'rb') as f:
                    response = self.client.post('/api/import_xml',
                                              data={'xml_file': (f, 'malicious.xml')},
                                              content_type='multipart/form-data')
                
                # Should handle malicious XML safely
                self.assertIn(response.status_code, [200, 400, 500])
                
                if response.status_code == 500:
                    # Error should be handled gracefully
                    data = json.loads(response.data)
                    self.assertIn('error', data)
            finally:
                os.unlink(temp_file.name)
    
    def test_api_rate_limiting_simulation(self):
        """Test API endpoints for potential rate limiting issues"""
        # Simulate rapid requests
        responses = []
        for i in range(20):
            response = self.client.get('/api/stats')
            responses.append(response.status_code)
            time.sleep(0.1)
        
        # All requests should be handled (no rate limiting implemented, but test responsiveness)
        self.assertTrue(all(status == 200 for status in responses))
    
    def test_unauthorized_file_access(self):
        """Test protection against unauthorized file access"""
        # Attempt to access files outside prompts directory
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\windows\\system32\\drivers\\etc\\hosts',
            '/etc/shadow',
            'C:\\Windows\\System32\\config\\SAM'
        ]
        
        for path in malicious_paths:
            response = self.client.get(f'/api/prompts/{path}')
            # Should return 404 or 403, not expose system files
            self.assertIn(response.status_code, [403, 404, 500])
    
    def test_environment_variable_exposure(self):
        """Test that sensitive environment variables are not exposed"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        response_text = str(data).lower()
        
        # Check that sensitive data is not leaked
        sensitive_patterns = ['api_key', 'password', 'secret', 'token', 'credential']
        for pattern in sensitive_patterns:
            self.assertNotIn(pattern, response_text)
    
    def test_input_validation_for_special_characters(self):
        """Test input validation for special characters and encoding"""
        special_ticket = {
            'id': 'TEST-SPECIAL-001',
            'subject': 'Special chars: ñáéíóú中文日本語',
            'description': 'Unicode test: 🔐🛡️⚠️ and control chars: \x00\x01\x02'
        }
        
        response = self.client.post('/api/analyze_ticket',
                                  data=json.dumps(special_ticket),
                                  content_type='application/json')
        
        # Should handle special characters safely
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
    
    def test_json_payload_size_limit(self):
        """Test protection against oversized JSON payloads"""
        # Create large JSON payload
        large_description = 'x' * (1024 * 1024)  # 1MB description
        large_ticket = {
            'id': 'LARGE-001',
            'subject': 'Large ticket',
            'description': large_description
        }
        
        response = self.client.post('/api/analyze_ticket',
                                  data=json.dumps(large_ticket),
                                  content_type='application/json')
        
        # Should handle large payloads appropriately
        self.assertIn(response.status_code, [200, 400, 413])
    
    def test_http_method_restrictions(self):
        """Test that endpoints only accept appropriate HTTP methods"""
        # Test POST-only endpoints with GET requests
        post_endpoints = ['/api/analyze_ticket', '/api/generate_response', '/api/import_xml']
        
        for endpoint in post_endpoints:
            response = self.client.get(endpoint)
            # Should return 405 Method Not Allowed
            self.assertEqual(response.status_code, 405)


class TestAuthenticationSecurity(unittest.TestCase):
    """Authentication and authorization security tests"""
    
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_api_key_protection(self):
        """Test that OpenAI API key is not exposed in responses"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-secret-key-123'}):
            response = self.client.get('/api/stats')
            self.assertEqual(response.status_code, 200)
            
            # Check response doesn't contain API key
            response_text = response.get_data(as_text=True)
            self.assertNotIn('test-secret-key-123', response_text)
    
    def test_session_security(self):
        """Test session handling security"""
        # Test that sessions are handled securely
        with self.client.session_transaction() as sess:
            sess['test_key'] = 'test_value'
        
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Verify session data is not leaked in response
        response_text = response.get_data(as_text=True)
        self.assertNotIn('test_value', response_text)


if __name__ == '__main__':
    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestSecurityValidation))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestAuthenticationSecurity))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print security test summary
    print(f"\n{'='*50}")
    print("SECURITY TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nSECURITY FAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].strip()}")
    
    if result.errors:
        print("\nSECURITY ERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception: ')[-1].strip()}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
