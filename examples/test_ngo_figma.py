#!/usr/bin/env python3
"""
Test script for the NGO Project Figma file
Tests screen-by-screen processing with the actual NGO project file
"""

import asyncio
import sys
from app.services.figma_processor import FigmaProcessor

async def test_ngo_figma_file():
    """Test the NGO Project Figma file with screen-by-screen processing"""
    
    # Your actual Figma file URL
    FIGMA_URL = "https://www.figma.com/proto/oqat2jknkfaeKkebJpNbeL/NGO-PROJECT?page-id=0%3A1&node-id=5-2115&viewport=301%2C235%2C0.09&t=K3VG0HyIAmLovngL-1&scaling=min-zoom&content-scaling=fixed&starting-point-node-id=2%3A2"
    
    # Extract the file key from the URL
    file_key = "oqat2jknkfaeKkebJpNbeL"  # Extracted from your URL
    
    print("🧪 Testing NGO Project Figma File")
    print("=" * 40)
    print("📁 File: NGO-PROJECT")
    print(f"🔗 URL: {FIGMA_URL}")
    print(f"🔑 File Key: {file_key}")
    print()
    
    # Get access token from user
    access_token = input("Enter your Figma access token: ").strip()
    
    if not access_token:
        print("❌ No access token provided. You need a Figma access token to test.")
        print("\nTo get your Figma access token:")
        print("1. Go to https://www.figma.com/developers/api#authentication")
        print("2. Click 'Get personal access token'")
        print("3. Generate a new token")
        print("4. Copy and paste it here")
        return
    
    processor = FigmaProcessor()
    
    try:
        print("\n1. 🔍 Validating file key...")
        if not file_key:
            print("❌ Could not extract file key from URL")
            return
        print(f"   ✅ File key: {file_key}")
        
        print("\n2. 📥 Fetching Figma JSON...")
        figma_json = await processor.get_figma_json(file_key, access_token)
        file_name = figma_json.get('name', 'Unknown')
        print(f"   ✅ File: {file_name}")
        
        print("\n3. 📊 Analyzing file structure...")
        structure = processor._analyze_file_structure(figma_json)
        total_nodes = structure['total_nodes']
        screen_count = structure['screen_count']
        can_process = structure['can_process_screen_by_screen']
        
        print(f"   📈 Total nodes: {total_nodes:,}")
        print(f"   📱 Screens found: {screen_count}")
        print(f"   🔄 Can process screen-by-screen: {can_process}")
        
        if screen_count > 0:
            print(f"\n   📋 Screen breakdown:")
            for screen in structure['screens']:
                status = "✅" if screen['can_process'] else "⚠️"
                print(f"      {status} {screen['name']}: {screen['node_count']:,} nodes")
        
        print("\n4. ✅ Testing validation...")
        is_valid, errors = processor.validate_figma_json(figma_json)
        
        if is_valid:
            print("   ✅ File is valid for processing!")
            processing_mode = figma_json.get('_processing_mode', 'standard')
            print(f"   🔧 Processing mode: {processing_mode}")
            
            if processing_mode == 'screen_by_screen':
                print("\n5. 🚀 Processing screen-by-screen...")
                print("   This will solve your 'Too many nodes' error!")
                
                try:
                    result = processor.process_large_figma_screen_by_screen(figma_json)
                    
                    successful_screens = len([s for s in result['screens'].values() if s.get('success', False)])
                    total_screens = len(result['screens'])
                    shared_components = len(result['shared_components'])
                    
                    print(f"   ✅ Successfully processed {successful_screens}/{total_screens} screens")
                    print(f"   🧩 Found {shared_components} shared components")
                    print(f"   🗺️  Generated navigation structure")
                    
                    print(f"\n   📱 Screen Results:")
                    for screen_name, screen_result in result['screens'].items():
                        if screen_result.get('success'):
                            chunks = screen_result.get('chunk_count', 0)
                            nodes = screen_result.get('node_count', 0)
                            print(f"      ✅ {screen_name}: {chunks} chunks, {nodes:,} nodes")
                        else:
                            error = screen_result.get('error', 'Unknown error')
                            print(f"      ❌ {screen_name}: {error}")
                    
                    print(f"\n🎉 SUCCESS! Your NGO project was processed!")
                    print(f"   📊 Original: {total_nodes:,} nodes")
                    print(f"   📱 Split into: {total_screens} screens")
                    print(f"   🧩 Shared components: {shared_components}")
                    print(f"   ✅ No more 'Too many nodes' error!")
                    
                    # Show navigation structure
                    if 'navigation' in result:
                        nav = result['navigation']
                        print(f"\n   🗺️  Navigation Structure:")
                        print(f"      Type: {nav.get('type', 'Unknown')}")
                        if 'screens' in nav:
                            for screen in nav['screens']:
                                print(f"      - {screen['name']} → {screen['route']}")
                    
                except Exception as e:
                    print(f"   ❌ Screen-by-screen processing failed: {str(e)}")
                    print(f"   Error details: {type(e).__name__}: {str(e)}")
            else:
                print("\n5. ℹ️  File is small enough for standard processing")
                print("   (No screen-by-screen processing needed)")
                print(f"   📊 Total nodes: {total_nodes:,} (under 10,000 limit)")
        else:
            print("   ❌ File validation failed:")
            for error in errors:
                print(f"      - {error}")
        
        print(f"\n📋 Summary:")
        print(f"   📁 File: {file_name}")
        print(f"   📊 Nodes: {total_nodes:,}")
        print(f"   📱 Screens: {screen_count}")
        print(f"   🔧 Mode: {figma_json.get('_processing_mode', 'standard')}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("\nPossible issues:")
        print("- Invalid access token")
        print("- Network connectivity")
        print("- File permissions")
        print("- File is private (needs proper permissions)")
        print("\nTo fix:")
        print("1. Make sure your access token is valid")
        print("2. Ensure you have access to the NGO-PROJECT file")
        print("3. Check your internet connection")

if __name__ == "__main__":
    print("🚀 Testing NGO Project Figma File")
    print("=" * 40)
    print("This will test the screen-by-screen processing")
    print("with your actual NGO project file")
    print()
    
    asyncio.run(test_ngo_figma_file())
