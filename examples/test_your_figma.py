#!/usr/bin/env python3
"""
Test your specific 44k node Figma file
This script will test the screen-by-screen processing with your actual file
"""

import asyncio
import sys
from app.services.figma_processor import FigmaProcessor

async def test_your_figma_file():
    """Test your specific Figma file that has 44,656 nodes"""
    
    # Replace these with your actual values
    FIGMA_URL = "https://www.figma.com/file/YOUR_FILE_ID/YOUR_FILE_NAME"
    ACCESS_TOKEN = "YOUR_FIGMA_ACCESS_TOKEN"
    
    print("🧪 Testing Your 44k Node Figma File")
    print("=" * 40)
    print("This will test the screen-by-screen processing")
    print("that solves your 'Too many nodes: 44656' error")
    print()
    
    # Check if user provided their own values
    if "YOUR_FILE_ID" in FIGMA_URL or "YOUR_ACCESS_TOKEN" in ACCESS_TOKEN:
        print("⚠️  Please update the script with your actual Figma details:")
        print("   1. Replace FIGMA_URL with your file URL")
        print("   2. Replace ACCESS_TOKEN with your Figma token")
        print()
        print("Or run with command line arguments:")
        print("   python test_your_figma.py 'https://figma.com/file/abc123' 'your_token'")
        print()
        
        # Try to get from command line
        if len(sys.argv) >= 3:
            FIGMA_URL = sys.argv[1]
            ACCESS_TOKEN = sys.argv[2]
            print(f"✅ Using provided URL: {FIGMA_URL}")
        else:
            print("❌ No valid Figma details provided")
            return
    
    processor = FigmaProcessor()
    
    try:
        print("1. 🔍 Extracting file key...")
        file_key = processor.extract_file_key(FIGMA_URL)
        if not file_key:
            print("❌ Could not extract file key from URL")
            return
        print(f"   ✅ File key: {file_key}")
        
        print("\n2. 📥 Fetching Figma JSON...")
        figma_json = await processor.get_figma_json(file_key, ACCESS_TOKEN)
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
                    
                    print(f"\n🎉 SUCCESS! Your 44k node file was processed!")
                    print(f"   📊 Original: {total_nodes:,} nodes")
                    print(f"   📱 Split into: {total_screens} screens")
                    print(f"   🧩 Shared components: {shared_components}")
                    print(f"   ✅ No more 'Too many nodes' error!")
                    
                except Exception as e:
                    print(f"   ❌ Screen-by-screen processing failed: {str(e)}")
            else:
                print("\n5. ℹ️  File is small enough for standard processing")
                print("   (No screen-by-screen processing needed)")
        else:
            print("   ❌ File validation failed:")
            for error in errors:
                print(f"      - {error}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("\nPossible issues:")
        print("- Invalid Figma URL")
        print("- Invalid access token") 
        print("- Network connectivity")
        print("- File permissions")
        print("\nTo get your Figma access token:")
        print("1. Go to https://www.figma.com/developers/api#authentication")
        print("2. Generate a personal access token")
        print("3. Use it in this script")

if __name__ == "__main__":
    print("🚀 Testing Your 44k Node Figma File")
    print("=" * 40)
    print("This script will test the screen-by-screen processing")
    print("that solves your 'Too many nodes: 44656' error")
    print()
    
    asyncio.run(test_your_figma_file())
