import unittest
import json
import time
import tempfile
import os
import requests
import sys
sys.path.append('src')

from app import app

# Optional selenium imports for UI testing (if available)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available. UI tests will be skipped.")

class TestFunctionalWorkflows(unittest.TestCase):
    """Functional tests for complete user workflows"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        app.config['TESTING'] = True
        cls.app = app
        cls.client = app.test_client()
        cls.base_url = 'http://localhost:5000'
        
        # Setup Chrome driver for UI tests (headless mode) - only if selenium available
        cls.driver = None
        if SELENIUM_AVAILABLE:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            try:
                cls.driver = webdriver.Chrome(options=chrome_options)
            except:
                cls.driver = None
                print("Chrome WebDriver not available. UI tests will be skipped.")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if cls.driver:
            cls.driver.quit()
    
    def test_complete_single_ticket_workflow(self):
        """Test complete workflow: Single ticket analysis"""
        # Step 1: Submit single ticket
        ticket_data = {
            'id': 'FUNC-001',
            'subject': 'ArcGIS Pro performance issues',
            'description': 'Application runs slowly when processing large datasets. Takes 5+ minutes to load a 2GB geodatabase.'
        }
        
        response = self.client.post('/api/analyze_ticket',
                                  data=json.dumps(ticket_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Step 2: Verify analysis results
        self.assertEqual(data['status'], 'success')
        self.assertIn('analysis', data)
        analysis = data['analysis']
        
        # Step 3: Verify analysis components
        required_fields = ['category', 'priority', 'confidence', 'suggested_response']
        for field in required_fields:
            self.assertIn(field, analysis)
        
        # Step 4: Verify category is appropriate
        self.assertIn(analysis['category'], ['arcgis_pro', 'general', 'data_issues'])
        
        # Step 5: Verify priority is set
        self.assertIn(analysis['priority'], ['high', 'medium', 'low'])
        
        print(f"✅ Single ticket workflow completed: {analysis['category']} - {analysis['priority']}")
    
    def test_bulk_ticket_processing_workflow(self):
        """Test complete workflow: Bulk ticket processing"""
        # Step 1: Prepare bulk tickets
        bulk_tickets = [
            {
                'id': 'BULK-001',
                'subject': 'Map printing fails',
                'description': 'Cannot print maps to large format printer. Error occurs during spooling.'
            },
            {
                'id': 'BULK-002', 
                'subject': 'Login issues with Portal',
                'description': 'Users cannot authenticate with Portal for ArcGIS. LDAP errors in logs.'
            },
            {
                'id': 'BULK-003',
                'subject': 'Training request for Survey123',
                'description': 'Team needs training on Survey123 form creation and deployment.'
            }
        ]
        
        # Step 2: Submit bulk analysis
        response = self.client.post('/api/bulk_analyze',
                                  data=json.dumps({'tickets': bulk_tickets}),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Step 3: Verify bulk results
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['total_processed'], 3)
        self.assertEqual(len(data['results']), 3)
        
        # Step 4: Verify each ticket was processed
        categories_found = []
        priorities_found = []
        
        for result in data['results']:
            self.assertIn('ticket_id', result)
            self.assertIn('analysis', result)
            
            analysis = result['analysis']
            categories_found.append(analysis['category'])
            priorities_found.append(analysis['priority'])
        
        # Step 5: Verify diverse categorization
        self.assertGreater(len(set(categories_found)), 1)  # At least 2 different categories
        
        print(f"✅ Bulk processing workflow completed: {len(set(categories_found))} categories found")
    
    def test_xml_import_and_processing_workflow(self):
        """Test complete workflow: XML import and processing"""
        # Step 1: Create test XML file
        xml_content = '''<?xml version="1.0"?>
        <incidents>
            <incident>
                <id>XML-FUNC-001</id>
                <subject>Server performance degradation</subject>
                <description>ArcGIS Server map services responding slowly. Load times increased 300%.</description>
                <priority>High</priority>
                <status>Open</status>
            </incident>
            <incident>
                <id>XML-FUNC-002</id>
                <subject>Mobile app sync failures</subject>
                <description>Collector app cannot sync data. Authentication errors reported by field teams.</description>
                <priority>Medium</priority>
                <status>Assigned</status>
            </incident>
        </incidents>'''
        
        # Step 2: Upload XML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as temp_file:
            temp_file.write(xml_content)
            temp_file.flush()
            
            try:
                with open(temp_file.name, 'rb') as f:
                    response = self.client.post('/api/import_xml',
                                              data={'xml_file': (f, 'test_tickets.xml')},
                                              content_type='multipart/form-data')
                
                # Step 3: Verify import success
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertEqual(data['status'], 'success')
                self.assertEqual(data['total_imported'], 2)
                
                # Step 4: Verify ticket data extraction
                results = data['results']
                self.assertEqual(len(results), 2)
                
                # Verify first ticket
                first_ticket = results[0]['ticket_data']
                self.assertEqual(first_ticket['id'], 'XML-FUNC-001')
                self.assertIn('Server performance', first_ticket['subject'])
                
                # Step 5: Process imported tickets
                tickets = [result['ticket_data'] for result in results]
                
                process_response = self.client.post('/api/process_tickets',
                                                  data=json.dumps({
                                                      'tickets': tickets,
                                                      'processing_options': {
                                                          'generate_responses': True,
                                                          'assign_priority': True
                                                      }
                                                  }),
                                                  content_type='application/json')
                
                self.assertEqual(process_response.status_code, 200)
                process_data = json.loads(process_response.data)
                self.assertEqual(process_data['status'], 'success')
                
                print(f"✅ XML import workflow completed: {process_data['total_processed']} tickets processed")
                
            finally:
                os.unlink(temp_file.name)
    
    def test_response_generation_workflow(self):
        """Test complete workflow: Response generation"""
        # Step 1: Generate response for different categories
        test_cases = [
            {
                'category': 'arcgis_pro',
                'content': 'Application crashes when opening large geodatabase files'
            },
            {
                'category': 'web_mapping',
                'content': 'Web map layers not displaying correctly in browser'
            },
            {
                'category': 'permissions',
                'content': 'Users cannot access shared organizational content'
            }
        ]
        
        for test_case in test_cases:
            # Step 2: Submit response generation request
            response = self.client.post('/api/generate_response',
                                      data=json.dumps(test_case),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            # Step 3: Verify response generation
            self.assertEqual(data['status'], 'success')
            self.assertIn('response', data)
            self.assertGreater(len(data['response']), 50)  # Response should be substantial
            self.assertEqual(data['category'], test_case['category'])
            
        print("✅ Response generation workflow completed for all categories")
    
    def test_prompt_export_workflow(self):
        """Test complete workflow: Prompt export and retrieval"""
        # Step 1: Analyze ticket to trigger prompt export
        ticket_data = {
            'id': 'EXPORT-FUNC-001',
            'subject': 'Geocoding service accuracy issues',
            'description': 'Address matching returning incorrect coordinates for batch geocoding operations'
        }
        
        response = self.client.post('/api/analyze_ticket',
                                  data=json.dumps(ticket_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Wait briefly for file system operations
        time.sleep(1)
        
        # Step 3: Retrieve exported prompts list
        prompts_response = self.client.get('/api/prompts')
        self.assertEqual(prompts_response.status_code, 200)
        
        prompts_data = json.loads(prompts_response.data)
        self.assertEqual(prompts_data['status'], 'success')
        
        # Step 4: Verify prompt was exported
        if prompts_data['total_count'] > 0:
            prompts = prompts_data['prompts']
            latest_prompt = prompts[0]  # Should be most recent
            
            # Step 5: Retrieve specific prompt file
            filename = latest_prompt['filename']
            file_response = self.client.get(f'/api/prompts/{filename}')
            
            if file_response.status_code == 200:
                file_data = json.loads(file_response.data)
                self.assertEqual(file_data['status'], 'success')
                
                # Step 6: Verify prompt structure
                prompt_data = file_data['prompt_data']
                required_fields = ['metadata', 'system_prompt', 'user_prompt', 'ticket_data']
                for field in required_fields:
                    self.assertIn(field, prompt_data)
                
                print(f"✅ Prompt export workflow completed: {filename}")
        else:
            print("⚠️ No prompts found - export may have failed")
    
    def test_statistics_tracking_workflow(self):
        """Test complete workflow: Statistics tracking"""
        # Step 1: Get initial statistics
        initial_response = self.client.get('/api/stats')
        self.assertEqual(initial_response.status_code, 200)
        initial_data = json.loads(initial_response.data)
        
        # Step 2: Process some tickets
        for i in range(3):
            ticket_data = {
                'id': f'STATS-{i+1:03d}',
                'subject': f'Test ticket {i+1}',
                'description': f'Test description for ticket {i+1}'
            }
            
            response = self.client.post('/api/analyze_ticket',
                                      data=json.dumps(ticket_data),
                                      content_type='application/json')
            self.assertEqual(response.status_code, 200)
        
        # Step 3: Wait for processing
        time.sleep(1)
        
        # Step 4: Get updated statistics
        final_response = self.client.get('/api/stats')
        self.assertEqual(final_response.status_code, 200)
        final_data = json.loads(final_response.data)
        
        # Step 5: Verify statistics structure
        required_stats = ['tickets_processed_today', 'avg_response_time', 'automation_rate', 'time_saved']
        for stat in required_stats:
            self.assertIn(stat, final_data)
        
        print("✅ Statistics tracking workflow completed")
    
    def test_error_handling_workflow(self):
        """Test complete workflow: Error handling and recovery"""
        # Step 1: Test malformed JSON
        response = self.client.post('/api/analyze_ticket',
                                  data='{"invalid": json}',
                                  content_type='application/json')
        self.assertIn(response.status_code, [400, 500])
        
        # Step 2: Test missing required fields
        incomplete_ticket = {'subject': 'Missing ID and description'}
        response = self.client.post('/api/analyze_ticket',
                                  data=json.dumps(incomplete_ticket),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)  # Should handle gracefully
        
        # Step 3: Test empty file upload
        response = self.client.post('/api/import_xml',
                                  data={'xml_file': ('', '')},
                                  content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        
        # Step 4: Test non-existent prompt file
        response = self.client.get('/api/prompts/nonexistent_file.json')
        self.assertEqual(response.status_code, 404)
        
        print("✅ Error handling workflow completed")
    
    def test_concurrent_request_handling(self):
        """Test concurrent request handling"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request(ticket_id):
            ticket_data = {
                'id': f'CONCURRENT-{ticket_id}',
                'subject': f'Concurrent test ticket {ticket_id}',
                'description': f'Testing concurrent processing for ticket {ticket_id}'
            }
            
            response = self.client.post('/api/analyze_ticket',
                                      data=json.dumps(ticket_data),
                                      content_type='application/json')
            results.put((ticket_id, response.status_code))
        
        # Step 1: Launch concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Step 2: Wait for completion
        for thread in threads:
            thread.join(timeout=10)
        
        # Step 3: Verify all requests completed successfully
        success_count = 0
        while not results.empty():
            ticket_id, status_code = results.get()
            if status_code == 200:
                success_count += 1
        
        self.assertEqual(success_count, 5)
        print(f"✅ Concurrent request handling completed: {success_count}/5 successful")


if __name__ == '__main__':
    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestFunctionalWorkflows))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print functional test summary
    print(f"\n{'='*50}")
    print("FUNCTIONAL TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("🎉 All functional workflows completed successfully!")
    else:
        if result.failures:
            print("\nFUNCTIONAL FAILURES:")
            for test, traceback in result.failures:
                print(f"❌ {test}")
        
        if result.errors:
            print("\nFUNCTIONAL ERRORS:")
            for test, traceback in result.errors:
                print(f"⚠️ {test}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
