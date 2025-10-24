#!/usr/bin/env python3
"""
API Endpoint Testing for Large Figma Files
Shows you exactly how to test with Postman/curl
"""

import requests
import json

def test_with_curl_commands():
    """Show curl commands for testing the API"""
    
    # Your Figma file details
    figma_url = "https://www.figma.com/proto/oqat2jknkfaeKkebJpNbeL/NGO-PROJECT"
    file_key = "oqat2jknkfaeKkebJpNbeL"
    
    print("🧪 Testing Large Figma Files via API")
    print("=" * 50)
    print(f"📁 File: NGO-PROJECT")
    print(f"🔑 File Key: {file_key}")
    print()
    
    print("🔧 Step 1: Test Figma File Analysis")
    print("-" * 30)
    print("POST /api/v1/figma/analyze")
    print("Content-Type: application/json")
    print()
    print("Request Body:")
    print(json.dumps({
        "file_id": file_key,
        "access_token": "YOUR_FIGMA_ACCESS_TOKEN"
    }, indent=2))
    print()
    
    print("🔧 Step 2: Test Code Generation (if analysis succeeds)")
    print("-" * 30)
    print("POST /api/v1/figma/generate")
    print("Content-Type: application/json")
    print()
    print("Request Body:")
    print(json.dumps({
        "file_id": file_key,
        "framework": "react",
        "backend_framework": "nodejs",
        "include_assets": True,
        "user_message": "Generate a complete NGO project application"
    }, indent=2))
    print()
    
    print("🔧 Step 3: Test with curl commands")
    print("-" * 30)
    print("# Test file analysis")
    print(f"curl -X POST http://localhost:8000/api/v1/figma/analyze \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print(f'    "file_id": "{file_key}",')
    print('    "access_token": "YOUR_FIGMA_ACCESS_TOKEN"')
    print("  }'")
    print()
    
    print("# Test code generation")
    print(f"curl -X POST http://localhost:8000/api/v1/figma/generate \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print(f'    "file_id": "{file_key}",')
    print('    "framework": "react",')
    print('    "backend_framework": "nodejs",')
    print('    "include_assets": true,')
    print('    "user_message": "Generate complete NGO project"')
    print("  }'")
    print()
    
    print("🔧 Step 4: Expected Response for Large Files")
    print("-" * 30)
    print("If your file has 44k+ nodes, you should see:")
    print("✅ processing_mode: 'screen_by_screen'")
    print("✅ screens: [list of screens]")
    print("✅ shared_components: [list of components]")
    print("✅ navigation: [routing structure]")
    print("✅ No 'Too many nodes' error!")
    print()
    
    print("🔧 Step 5: Postman Collection")
    print("-" * 30)
    print("Create a Postman collection with these requests:")
    print("1. POST /api/v1/figma/analyze")
    print("2. POST /api/v1/figma/generate")
    print("3. GET /api/v1/figma/export/{file_id}")
    print()

def test_with_requests():
    """Test using Python requests library"""
    
    base_url = "http://localhost:8000"
    file_key = "oqat2jknkfaeKkebJpNbeL"
    access_token = input("Enter your Figma access token: ").strip()
    
    if not access_token:
        print("❌ No access token provided")
        return
    
    print(f"\n🧪 Testing API with requests library")
    print(f"🌐 Base URL: {base_url}")
    print(f"🔑 File Key: {file_key}")
    
    # Test 1: Analyze file
    print("\n1. 📊 Analyzing file...")
    analyze_url = f"{base_url}/api/v1/figma/analyze"
    analyze_data = {
        "file_id": file_key,
        "access_token": access_token
    }
    
    try:
        response = requests.post(analyze_url, json=analyze_data, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Analysis successful!")
            print(f"   📊 Processing mode: {result.get('analysis', {}).get('processing_mode', 'unknown')}")
            
            # Check if it's screen-by-screen processing
            if result.get('analysis', {}).get('processing_mode') == 'screen_by_screen':
                print(f"   🎉 Screen-by-screen processing detected!")
                print(f"   📱 Screens: {len(result.get('analysis', {}).get('screens', {}))}")
            else:
                print(f"   ℹ️  Standard processing (file is small enough)")
        else:
            print(f"   ❌ Analysis failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {str(e)}")
        print("   Make sure the API server is running on localhost:8000")
        return
    
    # Test 2: Generate code (if analysis succeeded)
    print("\n2. 🚀 Generating code...")
    generate_url = f"{base_url}/api/v1/figma/generate"
    generate_data = {
        "file_id": file_key,
        "framework": "react",
        "backend_framework": "nodejs",
        "include_assets": True,
        "user_message": "Generate a complete NGO project application"
    }
    
    try:
        response = requests.post(generate_url, json=generate_data, timeout=60)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Code generation successful!")
            
            # Check the result structure
            if result.get('success'):
                generated_code = result.get('generated_code', {})
                metadata = result.get('metadata', {})
                
                print(f"   📊 Processing mode: {metadata.get('processing_mode', 'unknown')}")
                print(f"   📱 Total screens: {metadata.get('total_screens', 0)}")
                print(f"   🧩 Shared components: {metadata.get('shared_components_count', 0)}")
                
                if metadata.get('processing_mode') == 'screen_by_screen':
                    print(f"   🎉 SUCCESS! Your 44k node file was processed!")
                    print(f"   ✅ No more 'Too many nodes' error!")
                    
                    # Show screen breakdown
                    screens = generated_code.get('screens', {})
                    if screens:
                        print(f"\n   📱 Screen Results:")
                        for screen_name, screen_data in screens.items():
                            if isinstance(screen_data, dict) and screen_data.get('success'):
                                print(f"      ✅ {screen_name}")
                            else:
                                print(f"      ❌ {screen_name}")
                else:
                    print(f"   ℹ️  Standard processing completed")
            else:
                print(f"   ❌ Code generation failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Code generation failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 API Testing for Large Figma Files")
    print("=" * 40)
    print("Choose testing method:")
    print("1. Show curl commands and Postman setup")
    print("2. Test with Python requests library")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_with_curl_commands()
    elif choice == "2":
        test_with_requests()
    else:
        print("❌ Invalid choice")
