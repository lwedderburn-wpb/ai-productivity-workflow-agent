import unittest
from src.app import AI_Agent  # Adjust the import based on the actual class name in app.py

class TestAIAgent(unittest.TestCase):

    def setUp(self):
        self.agent = AI_Agent()  # Initialize the AI Agent/Application

    def test_initialization(self):
        self.assertIsNotNone(self.agent)  # Check if the agent is initialized

    def test_functionality(self):
        # Add tests for specific functionalities of the AI Agent/Application
        result = self.agent.some_functionality()  # Replace with actual method
        self.assertEqual(result, expected_value)  # Replace expected_value with the actual expected result

    def test_error_handling(self):
        with self.assertRaises(ExpectedException):  # Replace with the actual exception expected
            self.agent.some_function_that_should_fail()  # Replace with actual method

if __name__ == '__main__':
    unittest.main()
import unittest
import json
from src.app import app, gis_agent

class TestGISTicketAgent(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_index_page(self):
        """Test main dashboard loads"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'GIS Ticket Management AI Agent', response.data)
    
    def test_analyze_ticket_api(self):
        """Test single ticket analysis API"""
        test_ticket = {
            'id': 'TEST-001',
            'subject': 'ArcGIS Pro crashing',
            'description': 'ArcGIS Pro keeps crashing when I try to open large shapefiles'
        }
        
        response = self.app.post('/api/analyze_ticket',
                               data=json.dumps(test_ticket),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('analysis', data)
        self.assertIn('category', data['analysis'])
        self.assertIn('priority', data['analysis'])
    
    def test_bulk_analyze_api(self):
        """Test bulk ticket analysis API"""
        test_tickets = [
            {
                'id': 'TEST-001',
                'subject': 'Web map not loading',
                'description': 'The web map viewer is not loading properly'
            },
            {
                'id': 'TEST-002',
                'subject': 'Database connection issue',
                'description': 'Cannot connect to the geodatabase'
            }
        ]
        
        response = self.app.post('/api/bulk_analyze',
                               data=json.dumps({'tickets': test_tickets}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['total_processed'], 2)
    
    def test_generate_response_api(self):
        """Test response generation API"""
        test_data = {
            'category': 'arcgis_pro',
            'content': 'ArcGIS Pro is running slowly'
        }
        
        response = self.app.post('/api/generate_response',
                               data=json.dumps(test_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('response', data)
    
    def test_stats_api(self):
        """Test statistics API"""
        response = self.app.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('tickets_processed_today', data)
        self.assertIn('automation_rate', data)

class TestGISAgentCore(unittest.TestCase):
    
    def setUp(self):
        self.agent = gis_agent
    
    def test_categorize_ticket(self):
        """Test ticket categorization"""
        # Test ArcGIS Pro categorization
        pro_ticket = "ArcGIS Pro keeps crashing when I open large datasets"
        category = self.agent.categorize_ticket(pro_ticket)
        self.assertEqual(category, 'arcgis_pro')
        
        # Test web mapping categorization
        web_ticket = "The web map viewer is not displaying layers properly"
        category = self.agent.categorize_ticket(web_ticket)
        self.assertEqual(category, 'web_mapping')
        
        # Test data issues categorization
        data_ticket = "Cannot access the shapefile on the network drive"
        category = self.agent.categorize_ticket(data_ticket)
        self.assertEqual(category, 'data_issues')
    
    def test_determine_priority(self):
        """Test priority determination"""
        # Test high priority
        urgent_ticket = "URGENT: GIS system is completely down"
        priority = self.agent.determine_priority(urgent_ticket)
        self.assertEqual(priority, 'high')
        
        # Test medium priority
        medium_ticket = "Having issues with map printing"
        priority = self.agent.determine_priority(medium_ticket)
        self.assertEqual(priority, 'medium')
        
        # Test low priority
        low_ticket = "How do I create a buffer in ArcGIS?"
        priority = self.agent.determine_priority(low_ticket)
        self.assertEqual(priority, 'low')
    
    def test_generate_response(self):
        """Test response generation"""
        # Test ArcGIS Pro response
        response = self.agent.generate_response('arcgis_pro', 'Pro is crashing')
        self.assertIn('ArcGIS Pro', response)
        self.assertIn('cache', response)
        
        # Test default response
        response = self.agent.generate_response('unknown_category', 'Some issue')
        self.assertIn('GIS Support', response)
    
    def test_analyze_ticket(self):
        """Test complete ticket analysis"""
        test_ticket = {
            'id': 'TEST-123',
            'subject': 'ArcGIS Pro Performance Issue',
            'description': 'ArcGIS Pro is running very slowly when loading large datasets'
        }
        
        analysis = self.agent.analyze_ticket(test_ticket)
        
        self.assertIn('category', analysis)
        self.assertIn('priority', analysis)
        self.assertIn('suggested_response', analysis)
        self.assertIn('analysis_timestamp', analysis)
        self.assertIn('confidence', analysis)
        
        # Verify the analysis makes sense
        self.assertEqual(analysis['category'], 'arcgis_pro')
        self.assertIn(analysis['priority'], ['high', 'medium', 'low'])

if __name__ == '__main__':
    unittest.main()
