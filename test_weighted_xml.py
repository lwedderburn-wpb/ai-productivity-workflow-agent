#!/usr/bin/env python3
"""
Test script to demonstrate weighted XML processing in the GIS Ticket Management AI Agent
"""

import sys
import os
sys.path.append('src')

from ai_agent import EnhancedGISTicketAgent
import json

def test_weighted_xml_processing():
    """Test the weighted XML processing functionality"""
    
    # Initialize agent
    agent = EnhancedGISTicketAgent()
    
    # Sample ticket with rich XML data (simulating parsed XML)
    sample_ticket = {
        "id": "159143076",
        "number": "31149",
        "subject": "GIS Data - Geocode location addresses",
        "description": "GIS requests (GIS Data add/change, Addressing, Maps, Web App, etc)",
        "priority": "Medium",
        "status": "In progress",
        "category": "SR_GIS",
        "subcategory": "'SR_' Add / Change GIS Data",
        "group": "GIS",
        "requester": "Taylor Christian",
        "requester_email": "EChristian@wpb.org",
        "assigned_to": "Leighton Wedderburn",
        "assigned_to_email": "lwedderburn@wpb.org",
        "created_date": "2025-06-25T10:23:44-04:00",
        "updated_date": "2025-06-27T10:16:11-04:00",
        "due_date": "2025-07-08T00:00:00-04:00",
        "additional_info": "Hello! We have tried to create a GIS map for the High-Efficiency Toilet Program and had previously encountered some obstacles with address formatting. This program has been ongoing since 2012 and includes a lot of data (addresses) for where the toilets are/should be installed. I have included a copy of the file here for reference. Can you please let me know how to move forward with this? We keep putting it off, but having the map available will be beneficial for the program moving forward. The map should be internal-facing only. Thank you!; Request Type (GIS): Map Request"
    }
    
    print("🧪 Testing Weighted XML Processing")
    print("=" * 60)
    
    # Test 1: Weighted context building
    print("\n1. Testing Weighted Context Building:")
    weighted_context = agent._build_weighted_context(sample_ticket)
    print(weighted_context)
    
    # Test 2: Enhanced user prompt
    print("\n2. Testing Enhanced User Prompt:")
    user_prompt = agent.create_user_prompt(sample_ticket)
    print(user_prompt[:500] + "..." if len(user_prompt) > 500 else user_prompt)
    
    # Test 3: XML category mapping
    print("\n3. Testing XML Category Mapping:")
    xml_category = sample_ticket.get('category', '').lower()
    xml_subcategory = sample_ticket.get('subcategory', '').lower()
    mapped_category = agent._map_xml_category_to_gis(xml_category, xml_subcategory)
    print(f"XML Category: {xml_category}")
    print(f"XML Subcategory: {xml_subcategory}")
    print(f"Mapped GIS Category: {mapped_category}")
    
    # Test 4: Full analysis with weighted XML
    print("\n4. Testing Full Analysis with Weighted XML:")
    analysis_result = agent.analyze_ticket(sample_ticket)
    print(json.dumps(analysis_result, indent=2, default=str)[:800] + "...")
    
    # Test 5: Export with weighted context
    print("\n5. Testing Export with Weighted Context:")
    export_file = agent.export_prompt_context(sample_ticket)
    print(f"Export file created: {export_file}")
    
    # Load and display key parts of exported file
    with open(export_file, 'r') as f:
        exported_data = json.load(f)
    
    print("\nExported metadata:")
    print(json.dumps(exported_data['metadata'], indent=2))
    
    print("\nWeighted XML context:")
    print(exported_data.get('weighted_xml_context', 'Not found')[:300] + "...")
    
    print("\nProcessing notes:")
    print(json.dumps(exported_data.get('processing_notes', {}), indent=2))

if __name__ == "__main__":
    test_weighted_xml_processing()
