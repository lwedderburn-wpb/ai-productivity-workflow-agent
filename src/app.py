
from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
import re
from typing import Dict, List, Any

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'your-secret-key-here'

class GISTicketAgent:
    def __init__(self):
        self.ticket_categories = {
            'arcgis_pro': ['arcgis pro', 'pro', 'desktop', 'crash', 'slow performance'],
            'web_mapping': ['web map', 'portal', 'online', 'web application', 'viewer'],
            'data_issues': ['data', 'layer', 'shapefile', 'geodatabase', 'feature class'],
            'permissions': ['access', 'permission', 'login', 'authentication', 'user'],
            'printing': ['print', 'map book', 'layout', 'export', 'pdf'],
            'mobile': ['collector', 'survey123', 'field maps', 'mobile']
        }
        
        self.priority_keywords = {
            'high': ['urgent', 'critical', 'down', 'not working', 'broken', 'emergency'],
            'medium': ['slow', 'issue', 'problem', 'help', 'support'],
            'low': ['question', 'how to', 'training', 'enhancement', 'request']
        }
        
        self.response_templates = {
            'arcgis_pro': """Thank you for reporting the ArcGIS Pro issue. I've analyzed your request and identified the most likely cause. Please try the following:

1. Close ArcGIS Pro completely
2. Clear the application cache: %LOCALAPPDATA%\\ESRI\\ArcGISPro\\
3. Restart your computer
4. Try opening ArcGIS Pro again

If the issue persists, please let me know and I'll escalate this to our GIS team for further investigation.

Best regards,
GIS Support Team""",
            
            'web_mapping': """Thank you for contacting GIS Support regarding the web mapping issue. Based on your description, here are the recommended steps:

1. Clear your browser cache and cookies
2. Try accessing the web map in an incognito/private browsing window
3. Check if the issue occurs in a different browser
4. Verify your network connection is stable

If these steps don't resolve the issue, I'll need to check the server status and may need additional details about your specific use case.

Best regards,
GIS Support Team""",
            
            'data_issues': """Thank you for reporting the data issue. I understand this can be frustrating. Let me help you resolve this:

1. Verify the data source path is correct and accessible
2. Check if the data has been moved or renamed recently
3. Ensure you have proper read permissions for the data location
4. Try refreshing the data source in your project

I'll also check our data server status and coordinate with the data management team if needed.

Best regards,
GIS Support Team""",
            
            'permissions': """Thank you for contacting us about the access issue. I'll help you resolve this permissions problem:

1. Please verify your username and confirm you're using the correct login credentials
2. Check if your account has been recently updated or if passwords have expired
3. Clear your browser cache if accessing web-based GIS services

I'm also checking with our system administrators to ensure your account has the proper permissions assigned. You should receive an update within 2 hours.

Best regards,
GIS Support Team""",
            
            'default': """Thank you for contacting GIS Support. I've received your request and will review it shortly.

To help me provide the best assistance, could you please provide:
1. Steps to reproduce the issue
2. Any error messages you're seeing
3. Which GIS software/application you're using
4. When the issue first occurred

I'll respond with a solution or next steps within 4 hours.

Best regards,
GIS Support Team"""
        }

    def categorize_ticket(self, ticket_content: str) -> str:
        """Categorize ticket based on content analysis"""
        content_lower = ticket_content.lower()
        
        for category, keywords in self.ticket_categories.items():
            if any(keyword in content_lower for keyword in keywords):
                return category
        
        return 'general'

    def determine_priority(self, ticket_content: str) -> str:
        """Determine ticket priority based on content"""
        content_lower = ticket_content.lower()
        
        for priority, keywords in self.priority_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return priority
        
        return 'medium'

    def generate_response(self, category: str, ticket_content: str) -> str:
        """Generate appropriate response based on ticket category"""
        if category in self.response_templates:
            return self.response_templates[category]
        else:
            return self.response_templates['default']

    def analyze_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze ticket and return categorization, priority, and suggested response"""
        content = ticket_data.get('description', '') + ' ' + ticket_data.get('subject', '')
        
        category = self.categorize_ticket(content)
        priority = self.determine_priority(content)
        suggested_response = self.generate_response(category, content)
        
        return {
            'category': category,
            'priority': priority,
            'suggested_response': suggested_response,
            'analysis_timestamp': datetime.now().isoformat(),
            'confidence': 0.85  # Placeholder confidence score
        }

# Initialize the AI agent
gis_agent = GISTicketAgent()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/analyze_ticket', methods=['POST'])
def analyze_ticket():
    """Analyze a ticket and return AI recommendations"""
    try:
        ticket_data = request.json
        if not ticket_data:
            return jsonify({'error': 'No ticket data provided'}), 400
        
        analysis = gis_agent.analyze_ticket(ticket_data)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis,
            'ticket_id': ticket_data.get('id', 'unknown')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bulk_analyze', methods=['POST'])
def bulk_analyze():
    """Analyze multiple tickets at once"""
    try:
        tickets = request.json.get('tickets', [])
        if not tickets:
            return jsonify({'error': 'No tickets provided'}), 400
        
        results = []
        for ticket in tickets:
            analysis = gis_agent.analyze_ticket(ticket)
            results.append({
                'ticket_id': ticket.get('id', 'unknown'),
                'analysis': analysis
            })
        
        return jsonify({
            'status': 'success',
            'results': results,
            'total_processed': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate a response for a specific ticket"""
    try:
        data = request.json
        ticket_content = data.get('content', '')
        category = data.get('category', 'general')
        
        response = gis_agent.generate_response(category, ticket_content)
        
        return jsonify({
            'status': 'success',
            'response': response,
            'category': category
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get productivity statistics"""
    # This would typically pull from a database
    # For now, returning mock data
    return jsonify({
        'tickets_processed_today': 12,
        'avg_response_time': '2.3 hours',
        'automation_rate': '78%',
        'time_saved': '4.2 hours',
        'categories': {
            'arcgis_pro': 5,
            'web_mapping': 3,
            'data_issues': 2,
            'permissions': 1,
            'other': 1
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
