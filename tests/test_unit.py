import unittest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
sys.path.append('src')

from ai_agent import EnhancedGISTicketAgent
from app import app, XMLTicketParser

class TestEnhancedGISTicketAgent(unittest.TestCase):
    """Unit tests for EnhancedGISTicketAgent class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = EnhancedGISTicketAgent()
        self.sample_ticket = {
            'id': 'TEST-001',
            'subject': 'ArcGIS Pro crashes',
            'description': 'Application crashes when opening large geodatabase'
        }
    
    def test_init_without_api_key(self):
        """Test agent initialization without OpenAI API key"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}, clear=True):
            agent = EnhancedGISTicketAgent()
            self.assertIsNone(agent.client)
            self.assertFalse(agent.ai_enabled)
    
    def test_init_with_api_key(self):
        """Test agent initialization with valid API key"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key-123'}):
            agent = EnhancedGISTicketAgent()
            self.assertIsNotNone(agent.client)
    
    def test_categorize_arcgis_pro_issue(self):
        """Test categorization of ArcGIS Pro related tickets"""
        ticket = {
            'id': 'TEST-001',
            'subject': 'ArcGIS Pro geoprocessing error',
            'description': 'Toolbox fails to run in ArcGIS Pro desktop application'
        }
        result = self.agent.analyze_with_rules(ticket)
        self.assertEqual(result['category'], 'arcgis_pro')
        self.assertGreater(result['confidence'], 0.6)
    
    def test_categorize_web_mapping_issue(self):
        """Test categorization of web mapping related tickets"""
        ticket = {
            'id': 'TEST-002',
            'subject': 'ArcGIS Online dashboard problem',
            'description': 'Web map not loading in portal application'
        }
        result = self.agent.analyze_with_rules(ticket)
        self.assertEqual(result['category'], 'web_mapping')
    
    def test_categorize_data_issues(self):
        """Test categorization of data related tickets"""
        ticket = {
            'id': 'TEST-003',
            'subject': 'Shapefile corruption detected',
            'description': 'Geodatabase layer showing corrupted attributes'
        }
        result = self.agent.analyze_with_rules(ticket)
        self.assertEqual(result['category'], 'data_issues')
    
    def test_determine_high_priority(self):
        """Test high priority determination"""
        content = "URGENT: System is down and users cannot access critical data"
        priority = self.agent.determine_priority(content)
        self.assertEqual(priority, 'high')
    
    def test_determine_low_priority(self):
        """Test low priority determination"""
        content = "Question about how to create a map layout for training purposes"
        priority = self.agent.determine_priority(content)
        self.assertEqual(priority, 'low')
    
    def test_determine_medium_priority_default(self):
        """Test medium priority as default"""
        content = "Need help with map symbology settings"
        priority = self.agent.determine_priority(content)
        self.assertEqual(priority, 'medium')
    
    def test_generate_response_method(self):
        """Test response generation method exists and works"""
        response = self.agent.generate_response('arcgis_pro', 'Application crashes frequently')
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_export_prompt_context(self):
        """Test prompt context export functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.agent.prompts_dir = temp_dir
            filepath = self.agent.export_prompt_context(self.sample_ticket)
            self.assertTrue(os.path.exists(filepath))
            
            # Verify JSON structure
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.assertIn('metadata', data)
                self.assertIn('system_prompt', data)
                self.assertIn('user_prompt', data)
                self.assertEqual(data['metadata']['ticket_id'], 'TEST-001')


class TestXMLTicketParser(unittest.TestCase):
    """Unit tests for XMLTicketParser class"""
    
    def test_parse_simple_ticket_xml(self):
        """Test parsing simple ticket XML structure"""
        xml_content = '''<?xml version="1.0"?>
        <tickets>
            <ticket>
                <id>12345</id>
                <subject>Test Issue</subject>
                <description>Test description</description>
            </ticket>
        </tickets>'''
        
        tickets = XMLTicketParser.parse_xml_file(xml_content)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]['id'], '12345')
        self.assertEqual(tickets[0]['subject'], 'Test Issue')
    
    def test_parse_incident_xml(self):
        """Test parsing incident XML structure"""
        xml_content = '''<?xml version="1.0"?>
        <incidents>
            <incident>
                <id>INC-001</id>
                <subject>Server Issue</subject>
                <priority>High</priority>
            </incident>
        </incidents>'''
        
        tickets = XMLTicketParser.parse_xml_file(xml_content)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0]['id'], 'INC-001')
        self.assertEqual(tickets[0]['priority'], 'High')
    
    def test_parse_invalid_xml(self):
        """Test handling of invalid XML"""
        invalid_xml = '<invalid><unclosed>tag</invalid>'
        with self.assertRaises(ValueError):
            XMLTicketParser.parse_xml_file(invalid_xml)
    
    def test_parse_empty_xml(self):
        """Test handling of empty XML"""
        empty_xml = '<?xml version="1.0"?><root></root>'
        tickets = XMLTicketParser.parse_xml_file(empty_xml)
        self.assertEqual(len(tickets), 0)


class TestFlaskApp(unittest.TestCase):
    """Unit tests for Flask application routes"""
    
    def setUp(self):
        """Set up test client"""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_index_route(self):
        """Test main index route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'GIS Ticket Management', response.data)
    
    def test_stats_api(self):
        """Test statistics API endpoint"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('tickets_processed_today', data)
    
    def test_analyze_ticket_api(self):
        """Test ticket analysis API endpoint"""
        ticket_data = {
            'id': 'TEST-001',
            'subject': 'Test ticket',
            'description': 'Test description'
        }
        response = self.client.post('/api/analyze_ticket',
                                  data=json.dumps(ticket_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
    
    def test_generate_response_api(self):
        """Test response generation API endpoint"""
        request_data = {
            'category': 'general',
            'content': 'How do I create a map?'
        }
        response = self.client.post('/api/generate_response',
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')


if __name__ == '__main__':
    # Create test suite
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestEnhancedGISTicketAgent))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestXMLTicketParser))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestFlaskApp))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
