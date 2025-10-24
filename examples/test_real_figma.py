#!/usr/bin/env python3
"""
Test script for real Figma file processing
Tests screen-by-screen processing with actual Figma files
"""

import asyncio
import json
from app.services.figma_processor import FigmaProcessor

async def test_real_figma_processing():
    """Test screen-by-screen processing with real Figma files"""
    
    # You can replace this with your actual Figma file URL
    # Example: "https://www.figma.com/file/abc123/Your-Design-System"
    figma_url = input("Enter your Figma file URL: ").strip()
    
    if not figma_url:
        print("❌ No Figma URL provided. Using example URL...")
        # Example Figma file (you can replace with your own)
        figma_url = "https://www.figma.com/file/abc123/example-design-system"
    
    # You'll need to provide your Figma access token
    access_token = input("Enter your Figma access token (or press Enter to skip): ").strip()
    
    if not access_token:
        print("❌ No access token provided. Testing with mock data...")
        await test_with_mock_data()
        return
    
    processor = FigmaProcessor()
    
    print("🧪 Testing Real Figma File Processing")
    print("=" * 50)
    print(f"📁 File URL: {figma_url}")
    
    try:
        # Step 1: Extract file key
        print("\n1. Extracting file key...")
        file_key = processor.extract_file_key(figma_url)
        if not file_key:
            print("❌ Could not extract file key from URL")
            return
        print(f"   ✅ File key: {file_key}")
        
        # Step 2: Get Figma JSON
        print("\n2. Fetching Figma JSON...")
        figma_json = await processor.get_figma_json(file_key, access_token)
        print(f"   ✅ File name: {figma_json.get('name', 'Unknown')}")
        
        # Step 3: Analyze structure
        print("\n3. Analyzing file structure...")
        structure = processor._analyze_file_structure(figma_json)
        print(f"   📊 Total nodes: {structure['total_nodes']}")
        print(f"   📱 Screens found: {structure['screen_count']}")
        print(f"   🔄 Can process screen-by-screen: {structure['can_process_screen_by_screen']}")
        
        for screen in structure['screens']:
            print(f"   - {screen['name']}: {screen['node_count']} nodes")
        
        # Step 4: Test validation
        print("\n4. Testing validation...")
        is_valid, errors = processor.validate_figma_json(figma_json)
        print(f"   Validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        if errors:
            print(f"   Errors: {errors}")
        else:
            print(f"   Processing mode: {figma_json.get('_processing_mode', 'standard')}")
        
        # Step 5: Process if large file
        if figma_json.get('_processing_mode') == 'screen_by_screen':
            print("\n5. Processing screen-by-screen...")
            try:
                result = processor.process_large_figma_screen_by_screen(figma_json)
                print(f"   ✅ Successfully processed {len(result['screens'])} screens")
                print(f"   ✅ Found {len(result['shared_components'])} shared components")
                
                # Show results
                for screen_name, screen_result in result['screens'].items():
                    if screen_result.get('success'):
                        print(f"   📱 {screen_name}: {screen_result['chunk_count']} chunks")
                    else:
                        print(f"   ❌ {screen_name}: {screen_result.get('error', 'Unknown error')}")
                        
            except Exception as e:
                print(f"   ❌ Screen-by-screen processing failed: {str(e)}")
        else:
            print("\n5. File is small enough for standard processing")
        
        print("\n🎉 Real Figma test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("This might be due to:")
        print("- Invalid Figma URL")
        print("- Invalid access token")
        print("- Network issues")
        print("- File permissions")

async def test_with_mock_data():
    """Fallback test with mock data"""
    print("\n🔄 Running fallback test with mock data...")
    
    # Create a mock large Figma JSON
    mock_figma = {
        "name": "Large Design System",
        "document": {
            "id": "doc_1",
            "name": "Document", 
            "type": "DOCUMENT",
            "children": [
                {
                    "id": "page_1",
                    "name": "Page 1",
                    "type": "CANVAS",
                    "children": [
                        {
                            "id": "frame_1",
                            "name": "Login Screen",
                            "type": "FRAME",
                            "children": [
                                {"id": "node_1", "name": "Button", "type": "RECTANGLE"},
                                {"id": "node_2", "name": "Input", "type": "RECTANGLE"},
                            ]
                        },
                        {
                            "id": "frame_2",
                            "name": "Dashboard Screen", 
                            "type": "FRAME",
                            "children": [
                                {"id": "node_3", "name": "Chart", "type": "RECTANGLE"},
                                {"id": "node_4", "name": "Table", "type": "RECTANGLE"},
                            ]
                        }
                    ]
                }
            ]
        }
    }
    
    processor = FigmaProcessor()
    
    # Test structure analysis
    structure = processor._analyze_file_structure(mock_figma)
    print(f"   📊 Total nodes: {structure['total_nodes']}")
    print(f"   📱 Screens found: {structure['screen_count']}")
    print(f"   🔄 Can process screen-by-screen: {structure['can_process_screen_by_screen']}")
    
    # Test with large node count
    def mock_count_nodes(figma_json):
        return 44656  # Simulate your actual node count
    
    original_count = processor._count_nodes
    processor._count_nodes = mock_count_nodes
    
    try:
        is_valid, errors = processor.validate_figma_json(mock_figma)
        print(f"   Validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
        if errors:
            print(f"   Errors: {errors}")
        else:
            print(f"   Processing mode: {mock_figma.get('_processing_mode', 'standard')}")
    finally:
        processor._count_nodes = original_count

if __name__ == "__main__":
    print("🚀 Real Figma File Test")
    print("=" * 30)
    print("This test will:")
    print("1. Connect to your actual Figma file")
    print("2. Analyze the file structure")
    print("3. Test screen-by-screen processing")
    print("4. Show you the results")
    print()
    
    asyncio.run(test_real_figma_processing())
