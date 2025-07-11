import openai
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EnhancedGISTicketAgent:
    """Enhanced GIS Ticket Agent with OpenAI integration and prompt export"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.ai_enabled = os.getenv('AI_ENABLED', 'false').lower() == 'true'
        self.fallback_to_rules = os.getenv('FALLBACK_TO_RULES', 'true').lower() == 'true'
        self.export_prompts = os.getenv('EXPORT_PROMPTS', 'true').lower() == 'true'
        
        # Initialize OpenAI client if API key is provided
        if self.openai_api_key and self.openai_api_key != 'your_openai_api_key_here':
            openai.api_key = self.openai_api_key
            self.client = openai.OpenAI(api_key=self.openai_api_key)
        else:
            self.client = None
            print("⚠️  OpenAI API key not configured. Using rule-based responses.")
        
        # Create prompts directory
        self.prompts_dir = 'prompts_export'
        os.makedirs(self.prompts_dir, exist_ok=True)
        
        # GIS-specific categories and patterns
        self.gis_categories = {
            'arcgis_pro': ['arcgis pro', 'desktop', 'pro software', 'geoprocessing', 'toolbox'],
            'web_mapping': ['web map', 'online', 'portal', 'dashboard', 'web app', 'agol'],
            'data_issues': ['data', 'layer', 'shapefile', 'geodatabase', 'attribute', 'geometry'],
            'permissions': ['access', 'permission', 'login', 'credential', 'authorization', 'sharing'],
            'printing': ['print', 'map book', 'layout', 'export', 'pdf', 'large format'],
            'mobile': ['mobile', 'field', 'collector', 'survey123', 'workforce', 'android', 'ios'],
            'geocoding': ['geocode', 'address', 'location', 'coordinate', 'reverse geocoding'],
            'general': ['help', 'question', 'support', 'issue', 'problem']
        }

    def create_system_prompt(self) -> str:
        """Create the system prompt for GIS ticket analysis"""
        return """You are an expert GIS Technical Support AI Agent specializing in Esri ArcGIS products and geospatial technologies. 

Your role is to:
1. Analyze GIS-related support tickets
2. Categorize issues accurately
3. Determine appropriate priority levels
4. Generate helpful, technical responses
5. Create actionable resolution plans

Categories you work with:
- arcgis_pro: ArcGIS Desktop Pro software issues
- web_mapping: ArcGIS Online, Portal, web applications
- data_issues: Spatial data, layers, geodatabases
- permissions: Access rights, authentication, sharing
- printing: Map layouts, exports, large format printing
- mobile: Field apps (Collector, Survey123, Workforce)
- geocoding: Address matching and coordinate services
- general: General inquiries and other issues

Priority Levels:
- high: System down, data corruption, blocking production
- medium: Feature not working, workflow disruption
- low: Enhancement requests, training questions

Respond professionally with technical accuracy and provide step-by-step solutions when possible."""

    def create_user_prompt(self, ticket_data: Dict[str, Any], analysis_type: str = "full") -> str:
        """Create the user prompt for ticket analysis with weighted XML data priority"""
        ticket_id = ticket_data.get('id', 'Unknown')
        subject = ticket_data.get('subject', ticket_data.get('name', 'No subject'))
        description = ticket_data.get('description', ticket_data.get('description_no_html', 'No description'))
        
        # Build weighted context from XML-extracted fields (highest priority)
        weighted_context = self._build_weighted_context(ticket_data)
        
        if analysis_type == "categorize_only":
            prompt = f"""Analyze this GIS support ticket and respond with ONLY a JSON object:

Ticket ID: {ticket_id}
Subject: {subject}
Description: {description}"""

            if weighted_context:
                prompt += f"\n\nAdditional Context (High Priority XML Data):\n{weighted_context}"

            prompt += """

Required JSON format:
{
    "category": "category_name",
    "priority": "high|medium|low",
    "confidence": 0.95
}"""
            return prompt
        
        prompt = f"""Analyze this GIS support ticket and provide a comprehensive response:

Ticket ID: {ticket_id}
Subject: {subject}
Description: {description}"""

        if weighted_context:
            prompt += f"\n\nAdditional Context (High Priority XML Data):\n{weighted_context}"

        prompt += """

Please provide:
1. Category classification
2. Priority assessment
3. Detailed technical response with solution steps
4. Action plan for resolution

Format your response as JSON:
{
    "category": "category_name",
    "priority": "high|medium|low",
    "confidence": 0.95,
    "suggested_response": "Detailed technical response here...",
    "action_plan": ["Step 1", "Step 2", "Step 3"],
    "estimated_resolution_time": "X hours/days",
    "required_skills": ["skill1", "skill2"]
}"""
        return prompt

    def _build_weighted_context(self, ticket_data: Dict[str, Any]) -> str:
        """Build weighted context from XML-extracted fields with priority weighting"""
        weighted_fields = {
            # High priority fields (weight 3) - core ticket information
            'priority': 3,
            'status': 3,
            'category': 3,
            'subcategory': 3,
            'group': 3,
            'additional_info': 3,
            
            # Medium priority fields (weight 2) - metadata
            'requester': 2,
            'assigned_to': 2,
            'created_date': 2,
            'updated_date': 2,
            'due_date': 2,
            'number': 2,
            
            # Lower priority fields (weight 1) - supplementary
            'requester_email': 1,
            'assigned_to_email': 1
        }
        
        context_parts = []
        
        # Sort fields by weight (highest first)
        sorted_fields = sorted(weighted_fields.items(), key=lambda x: x[1], reverse=True)
        
        for field, weight in sorted_fields:
            if field in ticket_data and ticket_data[field]:
                value = ticket_data[field]
                
                # Format field names for better readability
                formatted_field = field.replace('_', ' ').title()
                
                # Add weight indicator for high priority fields
                if weight == 3:
                    context_parts.append(f"**{formatted_field}**: {value}")
                elif weight == 2:
                    context_parts.append(f"*{formatted_field}*: {value}")
                else:
                    context_parts.append(f"{formatted_field}: {value}")
        
        return '\n'.join(context_parts) if context_parts else ""

    def export_prompt_context(self, ticket_data: Dict[str, Any], analysis_type: str = "full") -> str:
        """Export prompt context to JSON file for manual use"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ticket_id = ticket_data.get('id', 'unknown')
        
        prompt_context = {
            "metadata": {
                "ticket_id": ticket_id,
                "timestamp": timestamp,
                "analysis_type": analysis_type,
                "export_reason": "Manual AI model input"
            },
            "system_prompt": self.create_system_prompt(),
            "user_prompt": self.create_user_prompt(ticket_data, analysis_type),
            "ticket_data": ticket_data,
            "suggested_models": [
                "gpt-4o",
                "gpt-4o-mini",
                "claude-3.5-sonnet",
                "gemini-pro",
                "llama-3.1-70b"
            ],
            "usage_instructions": {
                "step1": "Copy the 'system_prompt' to your AI model's system message",
                "step2": "Copy the 'user_prompt' to your AI model's user input",
                "step3": "Run the model and get JSON response",
                "step4": "Use the response in your ticket management system"
            }
        }
        
        filename = f"ticket_{ticket_id}_{timestamp}_prompt.json"
        filepath = os.path.join(self.prompts_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(prompt_context, f, indent=2, ensure_ascii=False)
        
        return filepath

    def analyze_with_openai(self, ticket_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze ticket using OpenAI GPT"""
        if not self.client:
            return None
        
        try:
            system_prompt = self.create_system_prompt()
            user_prompt = self.create_user_prompt(ticket_data)
            
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent responses
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                # Remove any markdown formatting if present
                if content.startswith('```json'):
                    content = content.split('```json')[1].split('```')[0].strip()
                elif content.startswith('```'):
                    content = content.split('```')[1].split('```')[0].strip()
                
                result = json.loads(content)
                result['ai_model'] = self.openai_model
                result['analysis_timestamp'] = datetime.now().isoformat()
                return result
                
            except json.JSONDecodeError:
                print(f"⚠️  Failed to parse AI response as JSON: {content}")
                return None
                
        except Exception as e:
            print(f"⚠️  OpenAI API error: {str(e)}")
            return None

    def analyze_with_rules(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based analysis using weighted XML data"""
        # Build content string with weighted priority
        content_parts = []
        
        # Add high-priority XML fields first (highest weight in analysis)
        high_priority_fields = ['additional_info', 'category', 'subcategory', 'priority', 'status']
        for field in high_priority_fields:
            if field in ticket_data and ticket_data[field]:
                content_parts.append(ticket_data[field])
        
        # Add core content fields
        core_content = [
            ticket_data.get('description', ''),
            ticket_data.get('description_no_html', ''),
            ticket_data.get('subject', ''),
            ticket_data.get('name', '')
        ]
        content_parts.extend([c for c in core_content if c])
        
        # Combine all content for analysis
        content = ' '.join(content_parts).lower()
        
        # Category detection with XML category field priority
        category = 'general'
        confidence = 0.5
        
        # First check if XML already has a category mapping
        xml_category = ticket_data.get('category', '').lower()
        xml_subcategory = ticket_data.get('subcategory', '').lower()
        
        if self._map_xml_category_to_gis(xml_category, xml_subcategory):
            category = self._map_xml_category_to_gis(xml_category, xml_subcategory)
            confidence = 0.9  # High confidence for XML-provided categories
        else:
            # Fallback to keyword-based detection
            for cat, keywords in self.gis_categories.items():
                matches = sum(1 for keyword in keywords if keyword in content)
                if matches > 0:
                    category = cat
                    confidence = min(0.95, 0.6 + (matches * 0.1))
                    break
        
        # Priority detection with XML priority field priority
        priority = 'medium'
        xml_priority = ticket_data.get('priority', '').lower()
        
        if xml_priority in ['high', 'urgent', 'critical', '1']:
            priority = 'high'
        elif xml_priority in ['low', '3', 'planning']:
            priority = 'low'
        elif xml_priority in ['medium', '2']:
            priority = 'medium'
        else:
            # Fallback to keyword-based detection
            high_priority_keywords = ['urgent', 'critical', 'down', 'error', 'failed', 'corrupted']
            low_priority_keywords = ['question', 'how to', 'training', 'enhancement']
            
            if any(keyword in content for keyword in high_priority_keywords):
                priority = 'high'
            elif any(keyword in content for keyword in low_priority_keywords):
                priority = 'low'
        
        # Generate response based on category and XML context
        suggested_response = self._generate_contextual_response(category, ticket_data)
        
        return {
            'category': category,
            'priority': priority,
            'confidence': confidence,
            'suggested_response': suggested_response,
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_method': 'rule_based_weighted_xml',
            'action_plan': self._generate_action_plan(category, priority),
            'estimated_resolution_time': self._estimate_resolution_time(priority),
            'required_skills': self._get_required_skills(category),
            'xml_data_used': True,
            'xml_fields_processed': list(ticket_data.keys())
        }

    def _map_xml_category_to_gis(self, xml_category: str, xml_subcategory: str) -> str:
        """Map XML category/subcategory to GIS categories"""
        category_mapping = {
            'sr_gis': 'general',
            'gis': 'general',
            'arcgis': 'arcgis_pro',
            'web_mapping': 'web_mapping',
            'data': 'data_issues',
            'spatial': 'data_issues',
            'geocoding': 'geocoding',
            'mobile': 'mobile',
            'printing': 'printing',
            'permissions': 'permissions',
            'portal': 'web_mapping',
            'online': 'web_mapping'
        }
        
        # Check subcategory first for more specific mapping
        for key, gis_cat in category_mapping.items():
            if key in xml_subcategory:
                return gis_cat
        
        # Check main category
        for key, gis_cat in category_mapping.items():
            if key in xml_category:
                return gis_cat
        
        return None

    def _generate_contextual_response(self, category: str, ticket_data: Dict[str, Any]) -> str:
        """Generate response using XML context data"""
        base_response = self._get_base_response_template(category)
        
        # Enhance response with XML context
        xml_enhancements = []
        
        if ticket_data.get('requester'):
            xml_enhancements.append(f"Hi {ticket_data['requester']},")
        
        if ticket_data.get('number'):
            xml_enhancements.append(f"Regarding ticket #{ticket_data['number']}")
        
        if ticket_data.get('due_date'):
            xml_enhancements.append(f"Given the due date of {ticket_data['due_date']}, I'll prioritize this request.")
        
        if ticket_data.get('additional_info'):
            xml_enhancements.append(f"Based on the additional information provided: {ticket_data['additional_info'][:200]}...")
        
        # Combine base response with XML enhancements
        if xml_enhancements:
            enhanced_response = ' '.join(xml_enhancements) + '\n\n' + base_response
        else:
            enhanced_response = base_response
        
        return enhanced_response

    def _get_base_response_template(self, category: str) -> str:
        """Get base response template for category"""
        response_templates = {
            'arcgis_pro': "Thank you for contacting GIS support regarding ArcGIS Pro. I'll help you resolve this issue. Please ensure you're running the latest version of ArcGIS Pro and try the following steps: 1) Check system requirements, 2) Restart ArcGIS Pro, 3) Clear the application cache. If the issue persists, please provide your ArcGIS Pro version and detailed error messages.",
            
            'web_mapping': "I'll assist you with your ArcGIS Online/Portal issue. Please verify: 1) Your internet connection is stable, 2) You're using a supported browser, 3) Clear browser cache and cookies. For sharing issues, check your item permissions and organization settings.",
            
            'data_issues': "For data-related issues, let's troubleshoot systematically: 1) Verify data source integrity, 2) Check coordinate systems and projections, 3) Validate attribute table structure. Please share the data format and any error messages you're encountering.",
            
            'permissions': "For access and permission issues: 1) Verify your login credentials, 2) Check with your administrator about role assignments, 3) Ensure you have the appropriate licenses. Please confirm which specific resources you cannot access.",
            
            'geocoding': "For geocoding and address matching: 1) Verify address format and completeness, 2) Check geocoding service availability, 3) Review coordinate system settings. Please share sample addresses that are failing to geocode.",
            
            'printing': "For printing and map layout issues: 1) Check printer settings and connectivity, 2) Verify map layout dimensions, 3) Ensure sufficient system memory. Please provide details about the specific printing error.",
            
            'mobile': "For mobile GIS application issues: 1) Check device compatibility, 2) Verify network connectivity, 3) Update the mobile app to the latest version. Please specify which mobile app and device you're using."
        }
        
        return response_templates.get(category, "Thank you for contacting GIS support. I'll help you resolve this issue. Please provide more details about the specific problem you're experiencing, including any error messages and steps you've already tried.")

    def _generate_action_plan(self, category: str, priority: str) -> List[str]:
        """Generate action plan based on category and priority"""
        base_plan = [
            "Acknowledge ticket receipt",
            "Review issue details",
            "Reproduce issue if possible",
            "Research solution",
            "Implement fix",
            "Test resolution",
            "Follow up with user"
        ]
        
        if priority == 'high':
            base_plan.insert(1, "URGENT: Escalate to senior technician")
            base_plan.insert(2, "Contact user immediately")
        
        return base_plan

    def _estimate_resolution_time(self, priority: str) -> str:
        """Estimate resolution time based on priority"""
        time_estimates = {
            'high': '2-4 hours',
            'medium': '1-2 business days',
            'low': '3-5 business days'
        }
        return time_estimates.get(priority, '1-2 business days')

    def _get_required_skills(self, category: str) -> List[str]:
        """Get required skills based on category"""
        skill_map = {
            'arcgis_pro': ['ArcGIS Desktop', 'Geoprocessing', 'Python scripting'],
            'web_mapping': ['ArcGIS Online', 'Portal administration', 'Web technologies'],
            'data_issues': ['Data management', 'Geodatabase', 'Spatial analysis'],
            'permissions': ['System administration', 'User management', 'Security'],
            'geocoding': ['Address matching', 'Coordinate systems', 'Spatial reference']
        }
        return skill_map.get(category, ['General GIS knowledge'])

    def analyze_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to analyze a ticket"""
        # Export prompt context if enabled
        if self.export_prompts:
            prompt_file = self.export_prompt_context(ticket_data)
            print(f"📄 Prompt context exported to: {prompt_file}")
        
        # Try AI analysis first if enabled
        if self.ai_enabled and self.client:
            ai_result = self.analyze_with_openai(ticket_data)
            if ai_result:
                ai_result['prompt_export_file'] = prompt_file if self.export_prompts else None
                return ai_result
        
        # Fallback to rule-based analysis
        if self.fallback_to_rules:
            rule_result = self.analyze_with_rules(ticket_data)
            rule_result['prompt_export_file'] = prompt_file if self.export_prompts else None
            return rule_result
        
        # If both AI and rules are disabled
        return {
            'category': 'general',
            'priority': 'medium',
            'confidence': 0.1,
            'suggested_response': 'Ticket received and will be reviewed manually.',
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_method': 'manual_review_required',
            'prompt_export_file': prompt_file if self.export_prompts else None
        }

    def generate_response(self, category: str, content: str) -> str:
        """Generate a response for a ticket based on category and content"""
        # Create a ticket-like data structure for consistency
        ticket_data = {
            'id': f'temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'subject': 'Response Generation Request',
            'description': content,
            'category': category
        }
        
        # Use the full analysis but extract just the response
        analysis = self.analyze_ticket(ticket_data)
        return analysis.get('suggested_response', 'Thank you for contacting support. We will review your request and respond soon.')

    def determine_priority(self, content: str) -> str:
        """Determine priority level based on content"""
        content_lower = content.lower()
        
        # High priority indicators
        high_priority_keywords = [
            'urgent', 'critical', 'emergency', 'down', 'broken', 'failed', 'error', 
            'corrupted', 'cannot access', 'system down', 'production', 'outage'
        ]
        
        # Low priority indicators  
        low_priority_keywords = [
            'question', 'how to', 'training', 'enhancement', 'feature request',
            'nice to have', 'when you have time', 'documentation', 'tutorial'
        ]
        
        # Check for high priority
        if any(keyword in content_lower for keyword in high_priority_keywords):
            return 'high'
        
        # Check for low priority
        if any(keyword in content_lower for keyword in low_priority_keywords):
            return 'low'
        
        # Default to medium priority
        return 'medium'
