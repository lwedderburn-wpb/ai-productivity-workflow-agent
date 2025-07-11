from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
from ai_agent import EnhancedGISTicketAgent

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'your-secret-key-here'

class XMLTicketParser:
    """Parse ticket information from XML files"""
    
    @staticmethod
    def parse_xml_file(xml_content: str) -> List[Dict[str, Any]]:
        """Parse XML content and extract ticket information"""
        try:
            root = ET.fromstring(xml_content)
            tickets = []
            
            # Handle different XML structures
            # Structure 1: <tickets><ticket>...</ticket></tickets>
            if root.tag == 'tickets':
                for ticket_elem in root.findall('ticket'):
                    ticket = XMLTicketParser._extract_ticket_data(ticket_elem)
                    if ticket:
                        tickets.append(ticket)
            
            # Structure 2: <incidents><incident>...</incident></incidents>
            elif root.tag == 'incidents':
                for ticket_elem in root.findall('incident'):
                    ticket = XMLTicketParser._extract_incident_data(ticket_elem)
                    if ticket:
                        tickets.append(ticket)
            
            # Structure 3: <ticket>...</ticket> (single ticket)
            elif root.tag == 'ticket':
                ticket = XMLTicketParser._extract_ticket_data(root)
                if ticket:
                    tickets.append(ticket)
            
            # Structure 4: <incident>...</incident> (single incident)
            elif root.tag == 'incident':
                ticket = XMLTicketParser._extract_incident_data(root)
                if ticket:
                    tickets.append(ticket)
            
            # Structure 5: Custom root with ticket/incident elements
            else:
                for ticket_elem in root.iter('ticket'):
                    ticket = XMLTicketParser._extract_ticket_data(ticket_elem)
                    if ticket:
                        tickets.append(ticket)
                for ticket_elem in root.iter('incident'):
                    ticket = XMLTicketParser._extract_incident_data(ticket_elem)
                    if ticket:
                        tickets.append(ticket)
            
            return tickets
            
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing XML: {str(e)}")
    
    @staticmethod
    def _extract_ticket_data(ticket_elem) -> Dict[str, Any]:
        """Extract ticket data from XML element"""
        ticket = {}
        
        # Common field mappings
        field_mappings = {
            'id': ['id', 'ticket_id', 'ticketId', 'number'],
            'subject': ['subject', 'title', 'summary'],
            'description': ['description', 'details', 'body', 'content'],
            'priority': ['priority', 'urgency', 'severity'],
            'category': ['category', 'type', 'classification'],
            'requester': ['requester', 'user', 'customer', 'reporter'],
            'status': ['status', 'state'],
            'created_date': ['created', 'date_created', 'timestamp', 'submitted'],
            'assigned_to': ['assigned_to', 'assignee', 'owner']
        }
        
        # Extract data using multiple possible field names
        for field, possible_names in field_mappings.items():
            for name in possible_names:
                elem = ticket_elem.find(name)
                if elem is not None and elem.text:
                    ticket[field] = elem.text.strip()
                    break
                # Try as attribute
                if ticket_elem.get(name):
                    ticket[field] = ticket_elem.get(name).strip()
                    break
        
        # Ensure required fields
        if not ticket.get('id'):
            ticket['id'] = f"XML-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if not ticket.get('subject') and not ticket.get('description'):
            return None  # Skip invalid tickets
        
        return ticket

    @staticmethod
    def _extract_incident_data(incident_elem) -> Dict[str, Any]:
        """Extract incident data from XML element (ServiceNow/Samanage format)"""
        ticket = {}
        
        # Direct field mappings for incident XML structure
        field_mappings = {
            'id': 'id',
            'number': 'number', 
            'subject': 'name',
            'description': 'description_no_html',
            'priority': 'priority',
            'status': 'state',
            'created_date': 'created_at',
            'updated_date': 'updated_at',
            'due_date': 'due_at'
        }
        
        # Extract basic fields
        for field, xml_tag in field_mappings.items():
            elem = incident_elem.find(xml_tag)
            if elem is not None and elem.text:
                ticket[field] = elem.text.strip()
        
        # Extract requester information
        requester_elem = incident_elem.find('requester')
        if requester_elem is not None:
            name_elem = requester_elem.find('name')
            email_elem = requester_elem.find('email')
            if name_elem is not None and name_elem.text:
                ticket['requester'] = name_elem.text.strip()
            if email_elem is not None and email_elem.text:
                ticket['requester_email'] = email_elem.text.strip()
        
        # Extract assignee information  
        assignee_elem = incident_elem.find('assignee')
        if assignee_elem is not None:
            name_elem = assignee_elem.find('name')
            email_elem = assignee_elem.find('email')
            if name_elem is not None and name_elem.text:
                ticket['assigned_to'] = name_elem.text.strip()
            if email_elem is not None and email_elem.text:
                ticket['assigned_to_email'] = email_elem.text.strip()
        
        # Extract category information
        category_elem = incident_elem.find('category')
        if category_elem is not None:
            name_elem = category_elem.find('name')
            if name_elem is not None and name_elem.text:
                ticket['category'] = name_elem.text.strip()
        
        # Extract subcategory information
        subcategory_elem = incident_elem.find('subcategory')
        if subcategory_elem is not None:
            name_elem = subcategory_elem.find('name')
            if name_elem is not None and name_elem.text:
                ticket['subcategory'] = name_elem.text.strip()
        
        # Extract group assignee
        group_elem = incident_elem.find('group_assignee')
        if group_elem is not None:
            name_elem = group_elem.find('name')
            if name_elem is not None and name_elem.text:
                ticket['group'] = name_elem.text.strip()
        
        # Extract custom fields for additional information
        custom_fields_elem = incident_elem.find('custom_fields_values')
        if custom_fields_elem is not None:
            additional_info = []
            for custom_field in custom_fields_elem.findall('custom_fields_value'):
                name_elem = custom_field.find('name')
                value_elem = custom_field.find('value')
                if name_elem is not None and value_elem is not None:
                    if name_elem.text and value_elem.text:
                        additional_info.append(f"{name_elem.text.strip()}: {value_elem.text.strip()}")
            if additional_info:
                ticket['additional_info'] = '; '.join(additional_info)
        
        # Ensure required fields
        if not ticket.get('id'):
            ticket['id'] = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if not ticket.get('subject') and not ticket.get('description'):
            return None  # Skip invalid incidents
        
        # Set default values for missing fields
        if not ticket.get('priority'):
            ticket['priority'] = 'Medium'
        if not ticket.get('status'):
            ticket['status'] = 'Open'
            
        return ticket

# Initialize the enhanced AI agent
gis_agent = EnhancedGISTicketAgent()

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

@app.route('/api/import_xml', methods=['POST'])
def import_xml():
    """Import tickets from XML file"""
    try:
        if 'xml_file' not in request.files:
            return jsonify({'error': 'No XML file provided'}), 400
        
        xml_file = request.files['xml_file']
        if xml_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not xml_file.filename.lower().endswith('.xml'):
            return jsonify({'error': 'File must be an XML file'}), 400
        
        # Read XML content
        xml_content = xml_file.read().decode('utf-8')
        
        # Parse XML and extract tickets
        parser = XMLTicketParser()
        tickets = parser.parse_xml_file(xml_content)
        
        if not tickets:
            return jsonify({'error': 'No valid tickets found in XML file'}), 400
        
        # Analyze each ticket
        results = []
        for ticket in tickets:
            analysis = gis_agent.analyze_ticket(ticket)
            results.append({
                'ticket_id': ticket.get('id'),
                'ticket_data': ticket,
                'analysis': analysis
            })
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully imported {len(tickets)} tickets from XML',
            'total_imported': len(tickets),
            'results': results
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to process XML file: {str(e)}'}), 500

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

@app.route('/api/process_tickets', methods=['POST'])
def process_tickets():
    """Process imported tickets with enhanced AI functionality"""
    try:
        data = request.json
        tickets = data.get('tickets', [])
        processing_options = data.get('processing_options', {})
        
        if not tickets:
            return jsonify({'error': 'No tickets provided for processing'}), 400
        
        processed_tickets = []
        start_time = datetime.now()
        responses_generated = 0
        action_plans_created = 0
        
        for ticket_data in tickets:
            ticket = ticket_data.get('ticket_data', {})
            existing_analysis = ticket_data.get('analysis', {})
            
            # Enhanced processing for each ticket
            processing_result = {
                'ticket_id': ticket.get('id'),
                'original_analysis': existing_analysis,
                'enhanced_analysis': {},
                'response': '',
                'action_plan': [],
                'processing_timestamp': datetime.now().isoformat()
            }
            
            # Re-analyze with enhanced context
            if processing_options.get('categorize', True):
                enhanced_analysis = gis_agent.analyze_ticket(ticket)
                processing_result['enhanced_analysis'] = enhanced_analysis
            
            # Generate detailed response
            if processing_options.get('generate_responses', True):
                category = existing_analysis.get('category', 'general')
                content = ticket.get('description', '') + ' ' + ticket.get('subject', '')
                response = gis_agent.generate_response(category, content)
                processing_result['response'] = response
                responses_generated += 1
            
            # Create action plan
            if processing_options.get('create_action_plan', True):
                action_plan = create_action_plan(ticket, existing_analysis)
                processing_result['action_plan'] = action_plan
                action_plans_created += 1
            
            # Assign priority if requested
            if processing_options.get('assign_priority', True):
                content = ticket.get('description', '') + ' ' + ticket.get('subject', '')
                priority = gis_agent.determine_priority(content)
                processing_result['assigned_priority'] = priority
            
            processed_tickets.append(processing_result)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
        avg_processing_time = processing_time / len(tickets) if tickets else 0
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully processed {len(tickets)} tickets',
            'total_processed': len(tickets),
            'processed_tickets': processed_tickets,
            'responses_generated': responses_generated,
            'action_plans_created': action_plans_created,
            'total_processing_time_ms': processing_time,
            'avg_processing_time': round(avg_processing_time, 2),
            'processing_options': processing_options
        })
    
    except Exception as e:
        return jsonify({'error': f'Failed to process tickets: {str(e)}'}), 500

@app.route('/api/prompts')
def list_exported_prompts():
    """List all exported prompt files"""
    try:
        prompts_dir = 'prompts_export'
        if not os.path.exists(prompts_dir):
            return jsonify({'status': 'success', 'prompts': []})
        
        prompt_files = []
        for filename in os.listdir(prompts_dir):
            if filename.endswith('_prompt.json'):
                filepath = os.path.join(prompts_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                prompt_files.append({
                    'filename': filename,
                    'ticket_id': data['metadata']['ticket_id'],
                    'timestamp': data['metadata']['timestamp'],
                    'analysis_type': data['metadata']['analysis_type']
                })
        
        prompt_files.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'prompts': prompt_files,
            'total_count': len(prompt_files)
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/api/prompts/<filename>')
def get_prompt_file(filename):
    """Get specific prompt file content"""
    try:
        filepath = os.path.join('prompts_export', filename)
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'error': 'File not found'})
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            'status': 'success',
            'prompt_data': data
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

def create_action_plan(ticket: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
    """Create an action plan based on ticket content and analysis"""
    category = analysis.get('category', 'general')
    priority = analysis.get('priority', 'medium')
    
    # Base action items
    action_plan = [
        "Acknowledge receipt of ticket",
        "Review ticket details and requirements"
    ]
    
    # Category-specific action items
    if category == 'gis_data':
        action_plan.extend([
            "Verify data source and format requirements",
            "Check geodatabase compatibility",
            "Validate coordinate system and projections",
            "Process geocoding request",
            "Update enterprise geodatabase",
            "Notify requester of completion"
        ])
    elif category == 'gis_application':
        action_plan.extend([
            "Review application requirements",
            "Check map service URLs and data sources",
            "Test application functionality",
            "Update application configuration",
            "Deploy changes to production",
            "Provide user training if needed"
        ])
    elif category == 'service_request':
        action_plan.extend([
            "Assess project scope and requirements",
            "Coordinate with stakeholders",
            "Develop project timeline",
            "Create detailed project plan",
            "Begin project execution",
            "Provide regular progress updates"
        ])
    elif category == 'arcgis_pro':
        action_plan.extend([
            "Reproduce the reported issue",
            "Check system requirements and compatibility",
            "Apply relevant software updates",
            "Test with clean user profile",
            "Escalate to vendor support if needed"
        ])
    elif category == 'web_mapping':
        action_plan.extend([
            "Check web map configuration",
            "Verify map service status",
            "Test in multiple browsers",
            "Review user permissions",
            "Apply necessary fixes"
        ])
    elif category == 'data_issues':
        action_plan.extend([
            "Investigate data source integrity",
            "Check data permissions and access",
            "Verify data format and structure",
            "Repair or restore data if needed",
            "Update data documentation"
        ])
    elif category == 'permissions':
        action_plan.extend([
            "Verify user account status",
            "Check group memberships and roles",
            "Review permission settings",
            "Update user access as needed",
            "Test access restoration"
        ])
    else:
        action_plan.extend([
            "Investigate reported issue",
            "Research potential solutions",
            "Implement appropriate fix",
            "Test resolution",
            "Follow up with requester"
        ])
    
    # Priority-based timeline adjustments
    if priority == 'high':
        action_plan.append("URGENT: Complete within 4 hours")
    elif priority == 'medium':
        action_plan.append("Standard: Complete within 24 hours")
    else:
        action_plan.append("Low priority: Complete within 72 hours")
    
    return action_plan

# Flask server startup
if __name__ == '__main__':
    print("Starting GIS Ticket Management AI Agent...")
    print("Server will be available at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5000, debug=True)
