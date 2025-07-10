
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

class TicketProcessor:
    """Advanced ticket processing utilities for GIS workflow automation"""
    
    def __init__(self):
        self.gis_keywords = {
            'software': ['arcgis', 'qgis', 'autocad', 'erdas', 'envi', 'global mapper'],
            'data_formats': ['shapefile', 'geodatabase', 'kml', 'geojson', 'raster', 'feature class'],
            'operations': ['buffer', 'clip', 'merge', 'dissolve', 'spatial join', 'geocoding'],
            'errors': ['error', 'crash', 'freeze', 'slow', 'not responding', 'corrupt'],
            'urgency': ['urgent', 'asap', 'critical', 'emergency', 'down', 'broken']
        }
    
    def extract_ticket_info(self, raw_text: str) -> Dict[str, Any]:
        """Extract structured information from raw ticket text"""
        info = {
            'software_mentioned': [],
            'data_formats': [],
            'operations': [],
            'error_indicators': [],
            'urgency_level': 'normal',
            'email_addresses': [],
            'phone_numbers': [],
            'file_paths': [],
            'coordinates': []
        }
        
        text_lower = raw_text.lower()
        
        # Extract software mentions
        for software in self.gis_keywords['software']:
            if software in text_lower:
                info['software_mentioned'].append(software)
        
        # Extract data formats
        for format_type in self.gis_keywords['data_formats']:
            if format_type in text_lower:
                info['data_formats'].append(format_type)
        
        # Extract operations
        for operation in self.gis_keywords['operations']:
            if operation in text_lower:
                info['operations'].append(operation)
        
        # Check for error indicators
        for error in self.gis_keywords['errors']:
            if error in text_lower:
                info['error_indicators'].append(error)
        
        # Determine urgency
        for urgent_word in self.gis_keywords['urgency']:
            if urgent_word in text_lower:
                info['urgency_level'] = 'high'
                break
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        info['email_addresses'] = re.findall(email_pattern, raw_text)
        
        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        info['phone_numbers'] = re.findall(phone_pattern, raw_text)
        
        # Extract file paths
        path_pattern = r'[A-Za-z]:\\[^<>:"|?*\n\r]+|/[^<>:"|?*\n\r]+'
        info['file_paths'] = re.findall(path_pattern, raw_text)
        
        # Extract coordinates (basic pattern)
        coord_pattern = r'-?\d{1,3}\.\d+,\s*-?\d{1,3}\.\d+'
        info['coordinates'] = re.findall(coord_pattern, raw_text)
        
        return info
    
    def generate_ticket_summary(self, ticket_data: Dict[str, Any]) -> str:
        """Generate a concise summary of the ticket"""
        subject = ticket_data.get('subject', 'No subject')
        description = ticket_data.get('description', 'No description')
        
        # Extract key information
        info = self.extract_ticket_info(description)
        
        summary_parts = [f"Subject: {subject}"]
        
        if info['software_mentioned']:
            summary_parts.append(f"Software: {', '.join(info['software_mentioned'])}")
        
        if info['error_indicators']:
            summary_parts.append(f"Issues: {', '.join(info['error_indicators'])}")
        
        if info['urgency_level'] == 'high':
            summary_parts.append("Priority: HIGH")
        
        if info['data_formats']:
            summary_parts.append(f"Data: {', '.join(info['data_formats'])}")
        
        return " | ".join(summary_parts)
    
    def suggest_next_steps(self, ticket_info: Dict[str, Any]) -> List[str]:
        """Suggest next steps based on ticket analysis"""
        steps = []
        
        if 'arcgis' in ticket_info.get('software_mentioned', []):
            steps.append("Check ArcGIS Pro/Desktop version and compatibility")
            steps.append("Verify license status and extensions")
        
        if 'crash' in ticket_info.get('error_indicators', []):
            steps.append("Collect crash logs and system information")
            steps.append("Check for recent system updates or software changes")
        
        if 'slow' in ticket_info.get('error_indicators', []):
            steps.append("Review system resources (CPU, RAM, disk space)")
            steps.append("Check data source performance and network connectivity")
        
        if ticket_info.get('data_formats'):
            steps.append("Verify data integrity and format compatibility")
            steps.append("Check file permissions and accessibility")
        
        if ticket_info.get('urgency_level') == 'high':
            steps.append("Schedule immediate phone call or remote session")
            steps.append("Escalate to senior GIS analyst if needed")
        
        if not steps:
            steps.append("Gather more information about the specific issue")
            steps.append("Schedule follow-up within 24 hours")
        
        return steps
    
    def create_response_template(self, ticket_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Create a personalized response template"""
        user_name = ticket_data.get('requester', 'User')
        ticket_id = ticket_data.get('id', 'N/A')
        
        template = f"""Dear {user_name},

Thank you for submitting ticket #{ticket_id}. I have reviewed your request and here's my analysis:

**Issue Summary:**
{analysis.get('summary', 'GIS-related technical issue')}

**Recommended Steps:**
"""
        
        steps = self.suggest_next_steps(analysis)
        for i, step in enumerate(steps, 1):
            template += f"{i}. {step}\n"
        
        template += """
I will monitor this ticket closely and provide updates as we work through the resolution. Please let me know if you have any questions or if the issue persists after trying these steps.

Best regards,
GIS Support Team

This response was generated with AI assistance and reviewed for accuracy."""
        
        return template

class WorkflowAutomator:
    """Automate common GIS workflow tasks"""
    
    def __init__(self):
        self.common_tasks = {
            'project_setup': self.setup_project_template,
            'data_check': self.perform_data_check,
            'user_access': self.check_user_access,
            'system_status': self.check_system_status
        }
    
    def setup_project_template(self, project_name: str) -> Dict[str, Any]:
        """Generate project setup checklist"""
        return {
            'task': 'project_setup',
            'project_name': project_name,
            'checklist': [
                'Create project directory structure',
                'Set up geodatabase',
                'Configure coordinate system',
                'Set up symbology templates',
                'Create backup procedures',
                'Document data sources',
                'Set user permissions'
            ],
            'estimated_time': '30 minutes',
            'priority': 'medium'
        }
    
    def perform_data_check(self, data_path: str) -> Dict[str, Any]:
        """Generate data quality check tasks"""
        return {
            'task': 'data_check',
            'data_path': data_path,
            'checks': [
                'Verify data accessibility',
                'Check coordinate system',
                'Validate attribute fields',
                'Test data integrity',
                'Check for missing values',
                'Verify spatial extent'
            ],
            'estimated_time': '15 minutes',
            'priority': 'high'
        }
    
    def check_user_access(self, username: str) -> Dict[str, Any]:
        """Generate user access verification tasks"""
        return {
            'task': 'user_access',
            'username': username,
            'checks': [
                'Verify Active Directory account',
                'Check GIS software licenses',
                'Validate database permissions',
                'Test network drive access',
                'Confirm Portal/Online access',
                'Check group memberships'
            ],
            'estimated_time': '10 minutes',
            'priority': 'high'
        }
    
    def check_system_status(self) -> Dict[str, Any]:
        """Generate system status check tasks"""
        return {
            'task': 'system_status',
            'checks': [
                'Check server availability',
                'Verify database connections',
                'Monitor disk space',
                'Check service status',
                'Validate network connectivity',
                'Review system logs'
            ],
            'estimated_time': '20 minutes',
            'priority': 'medium'
        }
    
    def generate_automation_plan(self, tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate automation plan for multiple tickets"""
        plan = {
            'total_tickets': len(tickets),
            'automation_opportunities': [],
            'manual_review_required': [],
            'estimated_time_saved': 0,
            'recommended_actions': []
        }
        
        for ticket in tickets:
            processor = TicketProcessor()
            info = processor.extract_ticket_info(ticket.get('description', ''))
            
            # Determine automation potential
            if info['software_mentioned'] and info['error_indicators']:
                plan['automation_opportunities'].append({
                    'ticket_id': ticket.get('id'),
                    'automation_type': 'standard_response',
                    'confidence': 0.8,
                    'time_saved': 15
                })
                plan['estimated_time_saved'] += 15
            elif info['urgency_level'] == 'high':
                plan['manual_review_required'].append({
                    'ticket_id': ticket.get('id'),
                    'reason': 'high_urgency',
                    'priority': 1
                })
            
        return plan
