#!/usr/bin/env python3
"""
Simple API Test for Large Figma Files
Tests the screen-by-screen processing via HTTP API
"""

import requests
import json
import time

def test_figma_api():
    """Test the Figma API with your NGO project file"""
    
    # Your Figma file details
    file_key = "oqat2jknkfaeKkebJpNbeL"
    base_url = "http://localhost:8000"
    
    print("Testing Large Figma File Processing")
    print("=" * 40)
    print(f"File: NGO-PROJECT")
    print(f"File Key: {file_key}")
    print(f"API URL: {base_url}")
    print()
    
    # Get access token
    access_token = input("Enter your Figma access token: ").strip()
    if not access_token:
        print("No access token provided. Exiting.")
        return
    
    print("\n1. Testing file analysis...")
    
    # Test 1: Analyze file
    analyze_url = f"{base_url}/api/v1/figma/analyze"
    analyze_data = {
        "file_id": file_key,
        "access_token": access_token
    }
    
    try:
        print("   Sending request to analyze file...")
        response = requests.post(analyze_url, json=analyze_data, timeout=30)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   SUCCESS: File analysis completed!")
            
            # Check processing mode
            analysis = result.get('analysis', {})
            processing_mode = analysis.get('processing_mode', 'unknown')
            print(f"   Processing Mode: {processing_mode}")
            
            if processing_mode == 'screen_by_screen':
                print("   SCREEN-BY-SCREEN PROCESSING DETECTED!")
                screens = analysis.get('screens', {})
                print(f"   Screens found: {len(screens)}")
                
                for screen_name, screen_data in screens.items():
                    node_count = screen_data.get('node_count', 0)
                    can_process = screen_data.get('can_process', False)
                    status = "OK" if can_process else "TOO LARGE"
                    print(f"   - {screen_name}: {node_count:,} nodes ({status})")
                
                print("\n   This solves your 'Too many nodes' error!")
            else:
                print("   Standard processing (file is small enough)")
                
        else:
            print(f"   ERROR: Analysis failed")
            print(f"   Response: {response.text}")
            return
            
    except requests.exceptions.RequestException as e:
        print(f"   ERROR: Request failed - {str(e)}")
        print("   Make sure the API server is running on localhost:8000")
        return
    
    print("\n2. Testing code generation...")
    
    # Test 2: Generate code
    generate_url = f"{base_url}/api/v1/figma/generate"
    generate_data = {
        "file_id": file_key,
        "framework": "react",
        "backend_framework": "nodejs",
        "include_assets": True,
        "user_message": "Generate complete NGO project application"
    }
    
    try:
        print("   Sending request to generate code...")
        response = requests.post(generate_url, json=generate_data, timeout=120)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   SUCCESS: Code generation completed!")
            
            # Check results
            if result.get('success'):
                metadata = result.get('metadata', {})
                processing_mode = metadata.get('processing_mode', 'unknown')
                total_screens = metadata.get('total_screens', 0)
                
                print(f"   Processing Mode: {processing_mode}")
                print(f"   Total Screens: {total_screens}")
                
                if processing_mode == 'screen_by_screen':
                    print("\n   SUCCESS! Your 44k node file was processed!")
                    print("   No more 'Too many nodes' error!")
                    
                    # Show generated code structure
                    generated_code = result.get('generated_code', {})
                    screens = generated_code.get('screens', {})
                    
                    if screens:
                        print(f"\n   Generated Screens:")
                        for screen_name, screen_data in screens.items():
                            if isinstance(screen_data, dict) and screen_data.get('success'):
                                print(f"   - {screen_name}: Generated successfully")
                            else:
                                print(f"   - {screen_name}: Failed")
                else:
                    print("   Standard processing completed")
            else:
                print(f"   ERROR: Code generation failed")
                print(f"   Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ERROR: Code generation failed")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ERROR: Request failed - {str(e)}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_figma_api()
