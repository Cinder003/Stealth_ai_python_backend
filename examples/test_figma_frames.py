"""
Test script for the new frame-specific Figma processing endpoint
Uses get_nodes() API for optimal performance
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:6000"
API_KEY = "test-api-key"

def test_figma_frames_endpoint():
    """Test the new frame-specific processing endpoint"""
    
    print("🧪 Testing Figma Frames Processing Endpoint")
    print("=" * 50)
    
    # Test data
    test_data = {
        "figma_url": "https://www.figma.com/file/oqat2jknkfaeKkebJpNbeL/NGO-PROJECT",
        "user_message": "Generate a modern web application with clean design",
        "framework": "react",
        "backend_framework": "nodejs"
    }
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"📋 Test Data:")
    print(f"   URL: {test_data['figma_url']}")
    print(f"   Framework: {test_data['framework']}")
    print(f"   Backend: {test_data['backend_framework']}")
    print()
    
    try:
        print("🚀 Sending request to /api/v1/figma/process-url-frames...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/v1/figma/process-url-frames",
            headers=headers,
            json=test_data,
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️  Processing time: {processing_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"   Frames processed: {result.get('frames_processed', 0)}/{result.get('total_frames', 0)}")
            print(f"   Total tokens: {result.get('metadata', {}).get('total_tokens', 0)}")
            print(f"   Processing time: {result.get('metadata', {}).get('processing_time', 0):.2f}s")
            
            if 'saved_files' in result:
                saved = result['saved_files']
                print(f"   Files saved: {saved.get('total_files', 0)}")
                print(f"   Project directory: {saved.get('project_dir', 'N/A')}")
            
            # Show frame results
            if 'metadata' in result and 'frame_results' in result['metadata']:
                print("\n📋 Frame Results:")
                for frame in result['metadata']['frame_results']:
                    status = "✅" if frame['success'] else "❌"
                    print(f"   {status} {frame['frame_name']} ({frame['frame_id'][:8]}...)")
                    if frame['success']:
                        print(f"      Tokens: {frame['tokens_used']}, Time: {frame['processing_time']:.2f}s")
                    else:
                        print(f"      Error: {frame.get('error', 'Unknown error')}")
            
        else:
            print("❌ FAILED!")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (5 minutes)")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - is the server running?")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def test_health_endpoint():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Figma Frames Processing Test")
    print("=" * 50)
    
    # Check server health first
    if not test_health_endpoint():
        print("❌ Server is not running. Please start with: docker-compose up -d")
        exit(1)
    
    print()
    
    # Test the new endpoint
    test_figma_frames_endpoint()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
