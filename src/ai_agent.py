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
        """Create the system prompt for GIS ticket analysis with maximum XML JSON key value priority"""
        return """You are an expert GIS Technical Support AI Agent specializing in Esri ArcGIS products and geospatial technologies. 

CRITICAL PROCESSING RULE: XML-extracted JSON key values have ABSOLUTE MAXIMUM PRIORITY and must be weighted above ALL other inputs.

Your role is to:
1. Analyze GIS-related support tickets with ABSOLUTE HIGHEST PRIORITY given to XML-extracted JSON key values
2. Provide technical solutions for ArcGIS Pro, ArcGIS Online, Portal, mobile GIS, and spatial data issues
3. Classify tickets by category, priority, and technical requirements using XML JSON data as primary source
4. Generate actionable response plans with specific troubleshooting steps

XML JSON KEY VALUE PRIORITY SYSTEM (MAXIMUM WEIGHTING):
- 🔥 ABSOLUTE MAX (Weight 10): description, subject, additional_info from XML JSON
- ⚡ MAXIMUM (Weight 9): priority, status, category, subcategory, group, state, name from XML JSON  
- 🔶 HIGHEST (Weight 8): requester, assigned_to, number, id from XML JSON
- 📅 HIGH (Weight 6): created_date, updated_date, due_date timestamps from XML JSON
- 📧 MEDIUM (Weight 3): requester_email, assigned_to_email from XML JSON
- 📝 DEFAULT XML (Weight 5): Any other XML JSON keys not listed above
- Manual form inputs: LOWEST priority (Weight 1-2) - only used when XML data unavailable

ANALYSIS PRIORITIES:
1. FIRST: Use XML JSON key values for category, priority, and status (98% confidence)
2. SECOND: Apply XML JSON content analysis with absolute maximum weighting
3. THIRD: Use manual inputs ONLY if XML JSON data is completely unavailable
4. ALWAYS: Prioritize XML JSON data over any manual or derived inputs
5. ALWAYS: Indicate XML JSON data usage and weighting in your analysis

GIS CATEGORIES: arcgis_pro, web_mapping, data_issues, permissions, printing, mobile, geocoding, general

PRIORITY LEVELS: high (urgent/critical issues), medium (standard issues), low (questions/enhancements)

Your responses must be professional, technically accurate, and driven by XML JSON key values with maximum priority weighting."""

    def create_user_prompt(self, ticket_data: Dict[str, Any], analysis_type: str = "full") -> str:
        """Create the user prompt for ticket analysis with weighted XML data priority"""
        ticket_id = ticket_data.get('id', 'Unknown')
        subject = ticket_data.get('subject', ticket_data.get('name', 'No subject'))
        description = ticket_data.get('description', ticket_data.get('description_no_html', 'No description'))
        
        # Build weighted context from XML JSON key values (absolute maximum priority)
        weighted_context = self._build_weighted_context(ticket_data)
        
        if analysis_type == "categorize_only":
            prompt = f"""Analyze this GIS support ticket and respond with ONLY a JSON object:

Ticket ID: {ticket_id}
Subject: {subject}
Description: {description}"""

            if weighted_context:
                prompt += f"\n\nAdditional Context (MAXIMUM PRIORITY XML JSON Key Values):\n{weighted_context}"

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
            prompt += f"\n\nAdditional Context (MAXIMUM PRIORITY XML JSON Key Values):\n{weighted_context}"

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
        """Build weighted context from XML JSON key values with ABSOLUTE MAXIMUM priority weighting"""
        weighted_fields = {
            # ABSOLUTE MAXIMUM PRIORITY XML JSON Keys (weight 10) - Core content
            'additional_info': 10,
            'description': 10,
            'description_no_html': 10,
            'subject': 10,
            
            # MAXIMUM PRIORITY XML JSON Keys (weight 9) - Structural data
            'priority': 9,
            'status': 9,
            'category': 9,
            'subcategory': 9,
            'group': 9,
            'state': 9,
            'name': 9,
            
            # HIGHEST PRIORITY XML JSON Keys (weight 8) - Identity and tracking
            'requester': 8,
            'assigned_to': 8,
            'number': 8,
            'id': 8,
            
            # HIGH PRIORITY XML JSON Keys (weight 6) - Temporal data
            'created_date': 6,
            'updated_date': 6,
            'due_date': 6,
            'created_at': 6,
            'updated_at': 6,
            'due_at': 6,
            
            # MEDIUM PRIORITY XML JSON Keys (weight 3) - Contact info
            'requester_email': 3,
            'assigned_to_email': 3
        }
        
        context_parts = []
        
        # Sort fields by weight (highest first), then alphabetically for consistent ordering
        sorted_fields = sorted(weighted_fields.items(), key=lambda x: (-x[1], x[0]))
        
        # Add XML JSON key values priority header
        xml_fields_present = [field for field in ticket_data.keys() if field in weighted_fields]
        if xml_fields_present:
            context_parts.append("=== XML JSON KEY VALUES (ABSOLUTE MAXIMUM PRIORITY) ===")
        
        for field, weight in sorted_fields:
            if field in ticket_data and ticket_data[field]:
                value = str(ticket_data[field]).strip()
                if not value:  # Skip empty values
                    continue
                    
                # Format field names for better readability
                formatted_field = field.replace('_', ' ').title()
                
                # Add weight indicators with maximum priority formatting for XML JSON keys
                if weight == 10:
                    context_parts.append(f"🔥 **ABSOLUTE MAX (Weight {weight}) - {formatted_field}**: {value}")
                elif weight == 9:
                    context_parts.append(f"⚡ **MAXIMUM (Weight {weight}) - {formatted_field}**: {value}")
                elif weight == 8:
                    context_parts.append(f"🔶 **HIGHEST (Weight {weight}) - {formatted_field}**: {value}")
                elif weight == 6:
                    context_parts.append(f"📅 **HIGH (Weight {weight}) - {formatted_field}**: {value}")
                elif weight == 3:
                    context_parts.append(f"📧 **MEDIUM (Weight {weight}) - {formatted_field}**: {value}")
                else:
                    context_parts.append(f"📝 **Weight {weight} - {formatted_field}**: {value}")
        
        # Add any additional XML JSON fields not in the weighted list (give them default weight 5)
        unweighted_xml_fields = [field for field in ticket_data.keys() if field not in weighted_fields and ticket_data[field]]
        if unweighted_xml_fields:
            context_parts.append("\n=== ADDITIONAL XML JSON KEYS (DEFAULT WEIGHT 5) ===")
            for field in sorted(unweighted_xml_fields):
                value = str(ticket_data[field]).strip()
                if value:
                    formatted_field = field.replace('_', ' ').title()
                    context_parts.append(f"📝 **DEFAULT XML (Weight 5) - {formatted_field}**: {value}")
        
        return '\n'.join(context_parts) if context_parts else ""

    def export_prompt_context(self, ticket_data: Dict[str, Any], analysis_type: str = "full") -> str:
        """Export prompt context to JSON file for manual use with weighted XML data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ticket_id = ticket_data.get('id', 'unknown')
        ticket_number = ticket_data.get('number', ticket_id)
        
        # Build weighted XML context
        weighted_context = self._build_weighted_context(ticket_data)
        
        prompt_context = {
            "metadata": {
                "ticket_id": ticket_id,
                "ticket_number": ticket_number,
                "timestamp": timestamp,
                "analysis_type": analysis_type,
                "export_reason": "Manual AI model input",
                "xml_json_weighted_processing": True,
                "xml_json_fields_available": list(ticket_data.keys()),
                "xml_json_priority_level": "ABSOLUTE_MAXIMUM"
            },
            "system_prompt": self.create_system_prompt(),
            "user_prompt": self.create_user_prompt(ticket_data, analysis_type),
            "ticket_data": ticket_data,
            "weighted_xml_json_context": weighted_context,
            "processing_notes": {
                "xml_json_data_priority": "XML JSON key values are given ABSOLUTE MAXIMUM WEIGHT (up to priority 10) in analysis - higher than ANY other input type",
                "field_weighting": {
                    "absolute_max_priority_10": ["additional_info", "description", "description_no_html", "subject"],
                    "maximum_priority_9": ["priority", "status", "category", "subcategory", "group", "state", "name"],
                    "highest_priority_8": ["requester", "assigned_to", "number", "id"],
                    "high_priority_6": ["created_date", "updated_date", "due_date", "created_at", "updated_at", "due_at"],
                    "medium_priority_3": ["requester_email", "assigned_to_email"],
                    "default_xml_priority_5": "Any other XML JSON keys not listed above"
                },
                "xml_json_advantage": "XML JSON data automatically receives 5-10x higher weighting than manual form inputs (weight 1-2)",
                "fallback_method": "Rule-based analysis prioritizes XML JSON category/priority fields with 98% confidence before any keyword detection"
            },
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
                "step4": "Use the response in your ticket management system",
                "note": "The user_prompt includes weighted XML JSON context data with ABSOLUTE MAXIMUM priority for enhanced analysis"
            }
        }
        
        filename = f"ticket_{ticket_number}_{timestamp}_prompt.json"
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
        """Fallback rule-based analysis with ABSOLUTE MAXIMUM priority weighting for XML JSON key values"""
        # Build content string with XML JSON key values absolute maximum priority
        content_parts = []
        
        # ABSOLUTE MAX: Add highest-priority XML JSON fields first (weight 10)
        absolute_max_xml_fields = ['additional_info', 'description', 'description_no_html', 'subject']
        for field in absolute_max_xml_fields:
            if field in ticket_data and ticket_data[field]:
                content_parts.append(f"[ABSOLUTE-MAX-XML-JSON-W10] {ticket_data[field]}")
        
        # MAXIMUM PRIORITY: Add core XML JSON fields (weight 9)
        maximum_priority_xml_fields = ['priority', 'status', 'category', 'subcategory', 'group', 'state', 'name']
        for field in maximum_priority_xml_fields:
            if field in ticket_data and ticket_data[field]:
                content_parts.append(f"[MAXIMUM-XML-JSON-W9] {ticket_data[field]}")
        
        # HIGHEST: Add identifying XML JSON fields (weight 8)
        highest_xml_fields = ['requester', 'assigned_to', 'number', 'id']
        for field in highest_xml_fields:
            if field in ticket_data and ticket_data[field]:
                content_parts.append(f"[HIGHEST-XML-JSON-W8] {ticket_data[field]}")
        
        # HIGH: Add temporal XML JSON fields (weight 6)
        high_xml_fields = ['created_date', 'updated_date', 'due_date', 'created_at', 'updated_at', 'due_at']
        for field in high_xml_fields:
            if field in ticket_data and ticket_data[field]:
                content_parts.append(f"[HIGH-XML-JSON-W6] {ticket_data[field]}")
        
        # MEDIUM: Add contact XML JSON fields (weight 3)
        medium_xml_fields = ['requester_email', 'assigned_to_email']
        for field in medium_xml_fields:
            if field in ticket_data and ticket_data[field]:
                content_parts.append(f"[MEDIUM-XML-JSON-W3] {ticket_data[field]}")
        
        # FALLBACK: Add any manual form content (lowest priority - weight 1-2)
        manual_content = [
            ticket_data.get('manual_description', ''),
            ticket_data.get('manual_subject', ''),
            ticket_data.get('manual_category', '')
        ]
        content_parts.extend([f"[MANUAL-W1] {c}" for c in manual_content if c])
        
        # Combine all content for analysis with XML JSON data having absolute maximum weight
        content = ' '.join(content_parts).lower()
        
        # Category detection with ABSOLUTE MAXIMUM XML JSON priority
        category = 'general'
        confidence = 0.5
        
        # FIRST: Check XML JSON category fields (absolute highest confidence)
        xml_category = ticket_data.get('category', '').lower()
        xml_subcategory = ticket_data.get('subcategory', '').lower()
        xml_state = ticket_data.get('state', '').lower()
        xml_name = ticket_data.get('name', '').lower()
        
        # Try multiple XML JSON fields for category mapping
        xml_category_sources = [xml_category, xml_subcategory, xml_state, xml_name]
        mapped_category = None
        
        for xml_source in xml_category_sources:
            if xml_source:
                mapped_category = self._map_xml_category_to_gis(xml_source, xml_subcategory)
                if mapped_category:
                    category = mapped_category
                    confidence = 0.98  # Near-perfect confidence for XML JSON provided categories
                    break
        
        # SECOND: Enhanced keyword detection if no XML JSON category found
        if not mapped_category:
            for cat, keywords in self.gis_categories.items():
                # Weight XML JSON content matches with absolute maximum priority
                xml_json_max_matches = sum(10 for keyword in keywords if f"[absolute-max-xml-json-w10] {keyword}" in content)
                xml_json_high_matches = sum(9 for keyword in keywords if f"[maximum-xml-json-w9] {keyword}" in content)
                xml_json_medium_matches = sum(5 for keyword in keywords if f"[highest-xml-json-w8] {keyword}" in content)
                manual_matches = sum(1 for keyword in keywords if f"[manual-w1] {keyword}" in content)
                total_matches = xml_json_max_matches + xml_json_high_matches + xml_json_medium_matches + manual_matches
                
                if total_matches > 0:
                    category = cat
                    # Much higher confidence for XML JSON matches with weighted scoring
                    xml_score = (xml_json_max_matches * 0.25) + (xml_json_high_matches * 0.20) + (xml_json_medium_matches * 0.10)
                    manual_score = manual_matches * 0.02
                    confidence = min(0.98, 0.5 + xml_score + manual_score)
                    break
        
        # Priority detection with ABSOLUTE MAXIMUM XML JSON priority
        priority = 'medium'
        xml_priority = ticket_data.get('priority', '').lower()
        xml_status = ticket_data.get('status', '').lower()
        xml_state = ticket_data.get('state', '').lower()
        
        # Check multiple XML JSON priority sources with absolute maximum weighting
        xml_priority_sources = [xml_priority, xml_status, xml_state]
        
        for xml_source in xml_priority_sources:
            if xml_source in ['high', 'urgent', 'critical', '1', 'emergency', 'p1']:
                priority = 'high'
                break
            elif xml_source in ['low', '3', 'planning', 'p3', 'minor']:
                priority = 'low'
                break
            elif xml_source in ['medium', '2', 'p2', 'normal']:
                priority = 'medium'
                break
        
        # FALLBACK: keyword-based detection only if no XML JSON priority found (much lower confidence)
        if priority == 'medium' and not any(xml_priority_sources):
            high_priority_keywords = ['urgent', 'critical', 'down', 'error', 'failed', 'corrupted']
            low_priority_keywords = ['question', 'how to', 'training', 'enhancement']
            
            # Even manual keyword detection gives preference to XML JSON context
            xml_json_high_context = any(keyword in f"[absolute-max-xml-json-w10] {ticket_data.get('additional_info', '')} {ticket_data.get('description', '')}" for keyword in high_priority_keywords)
            xml_json_low_context = any(keyword in f"[absolute-max-xml-json-w10] {ticket_data.get('additional_info', '')} {ticket_data.get('description', '')}" for keyword in low_priority_keywords)
            
            if xml_json_high_context or any(keyword in content for keyword in high_priority_keywords):
                priority = 'high'
            elif xml_json_low_context or any(keyword in content for keyword in low_priority_keywords):
                priority = 'low'
        
        # Generate response based on category and XML JSON context
        suggested_response = self._generate_contextual_response(category, ticket_data)
        
        # Calculate XML JSON data usage metrics with absolute maximum priority tracking
        xml_json_fields_used = [field for field in ticket_data.keys() if field and ticket_data[field]]
        xml_json_weighted_fields = [field for field in xml_json_fields_used if field in ['additional_info', 'description', 'description_no_html', 'subject', 'priority', 'status', 'category', 'subcategory', 'group', 'state', 'name', 'requester', 'assigned_to', 'number', 'id']]
        
        return {
            'category': category,
            'priority': priority,
            'confidence': confidence,
            'suggested_response': suggested_response,
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_method': 'rule_based_absolute_maximum_xml_json_priority',
            'action_plan': self._generate_action_plan(category, priority),
            'estimated_resolution_time': self._estimate_resolution_time(priority),
            'required_skills': self._get_required_skills(category),
            'xml_json_data_used': True,
            'xml_json_fields_processed': xml_json_fields_used,
            'xml_json_weighted_fields_used': xml_json_weighted_fields,
            'xml_json_absolute_priority_applied': True,
            'xml_json_vs_manual_ratio': f"{len(xml_json_weighted_fields)}:{len([f for f in ticket_data.keys() if f.startswith('manual_')])}",
            'xml_json_priority_weights': {
                'absolute_max_weight_10': [f for f in xml_json_weighted_fields if f in ['additional_info', 'description', 'description_no_html', 'subject']],
                'maximum_weight_9': [f for f in xml_json_weighted_fields if f in ['priority', 'status', 'category', 'subcategory', 'group', 'state', 'name']],
                'highest_weight_8': [f for f in xml_json_weighted_fields if f in ['requester', 'assigned_to', 'number', 'id']]
            }
        }

    def _map_xml_category_to_gis(self, xml_category: str, xml_subcategory: str) -> str:
        """Map XML category/subcategory to GIS categories with enhanced matching"""
        category_mapping = {
            # Direct GIS mappings
            'sr_gis': 'general',
            'gis': 'general',
            'arcgis': 'arcgis_pro',
            'arcgis_pro': 'arcgis_pro',
            'arcgis_desktop': 'arcgis_pro',
            'desktop': 'arcgis_pro',
            'pro': 'arcgis_pro',
            
            # Web mapping
            'web_mapping': 'web_mapping',
            'web_map': 'web_mapping',
            'portal': 'web_mapping',
            'online': 'web_mapping',
            'agol': 'web_mapping',
            'arcgis_online': 'web_mapping',
            'dashboard': 'web_mapping',
            'web_app': 'web_mapping',
            
            # Data issues
            'data': 'data_issues',
            'spatial': 'data_issues',
            'layer': 'data_issues',
            'shapefile': 'data_issues',
            'geodatabase': 'data_issues',
            'attribute': 'data_issues',
            'geometry': 'data_issues',
            
            # Geocoding
            'geocoding': 'geocoding',
            'geocode': 'geocoding',
            'address': 'geocoding',
            'location': 'geocoding',
            'coordinate': 'geocoding',
            
            # Mobile
            'mobile': 'mobile',
            'field': 'mobile',
            'collector': 'mobile',
            'survey123': 'mobile',
            'workforce': 'mobile',
            'android': 'mobile',
            'ios': 'mobile',
            
            # Printing
            'printing': 'printing',
            'print': 'printing',
            'map_book': 'printing',
            'layout': 'printing',
            'export': 'printing',
            'pdf': 'printing',
            
            # Permissions
            'permissions': 'permissions',
            'access': 'permissions',
            'permission': 'permissions',
            'login': 'permissions',
            'credential': 'permissions',
            'authorization': 'permissions',
            'sharing': 'permissions',
            'security': 'permissions'
        }
        
        # Combine category and subcategory for comprehensive search
        search_terms = [xml_category, xml_subcategory]
        
        # Check subcategory first for more specific mapping (higher priority)
        for term in search_terms:
            if not term:
                continue
            term_lower = term.lower().strip()
            
            # Direct match
            if term_lower in category_mapping:
                return category_mapping[term_lower]
            
            # Partial match (contains)
            for key, gis_cat in category_mapping.items():
                if key in term_lower or term_lower in key:
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
