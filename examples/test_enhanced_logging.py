"""
Test script to verify enhanced logging is working
This will trigger the frame processing and show the detailed logs
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:6000"
API_KEY = "test-api-key"

def test_enhanced_logging():
    """Test the enhanced logging by triggering frame processing"""
    
    print("🧪 Testing Enhanced Logging for Figma Frame Processing")
    print("=" * 60)
    
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
    
    print(f"📋 Test Configuration:")
    print(f"   URL: {test_data['figma_url']}")
    print(f"   Framework: {test_data['framework']}")
    print(f"   Backend: {test_data['backend_framework']}")
    print()
    
    print("🚀 Starting frame processing...")
    print("📱 Check Docker logs to see detailed processing information!")
    print("   Run: docker-compose logs -f app")
    print()
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/v1/figma/process-url-frames",
            headers=headers,
            json=test_data,
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️  Request completed in: {processing_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"   Frames processed: {result.get('frames_processed', 0)}/{result.get('total_frames', 0)}")
            
            if 'metadata' in result:
                metadata = result['metadata']
                print(f"   Total tokens: {metadata.get('total_tokens', 0):,}")
                print(f"   Processing time: {metadata.get('processing_time', 0):.2f}s")
                print(f"   Average per frame: {metadata.get('processing_time', 0)/max(result.get('total_frames', 1), 1):.2f}s")
            
            if 'saved_files' in result:
                saved = result['saved_files']
                print(f"   Files saved: {saved.get('total_files', 0)}")
                print(f"   Project directory: {saved.get('project_dir', 'N/A')}")
            
            print("\n📱 To see the detailed LLM responses and generated code:")
            print("   Run: docker-compose logs -f app")
            print("   Look for sections starting with '🎯 LLM Response for frame'")
            
        else:
            print("❌ FAILED!")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (5 minutes)")
        print("📱 Check Docker logs to see what happened:")
        print("   Run: docker-compose logs -f app")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - is the server running?")
        print("   Start with: docker-compose up -d")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

def show_log_commands():
    """Show useful Docker log commands"""
    print("\n🛠️  Useful Docker Log Commands:")
    print("=" * 40)
    print("📱 View real-time app logs:")
    print("   docker-compose logs -f app")
    print()
    print("📱 View recent logs (last 100 lines):")
    print("   docker-compose logs --tail=100 app")
    print()
    print("📱 View all container logs:")
    print("   docker-compose logs -f")
    print()
    print("📱 Save logs to file:")
    print("   docker-compose logs app > figma_logs.txt")
    print()
    print("📱 Filter logs for specific content:")
    print("   docker-compose logs app | grep 'LLM Response'")
    print("   docker-compose logs app | grep 'Parsing'")
    print("   docker-compose logs app | grep 'Frame'")

if __name__ == "__main__":
    print("🧪 Enhanced Logging Test for Figma Frame Processing")
    print("=" * 60)
    
    # Show log commands first
    show_log_commands()
    
    print("\n" + "=" * 60)
    print("🚀 Starting test...")
    print("📱 Open another terminal and run: docker-compose logs -f app")
    print("   This will show you the detailed processing logs in real-time!")
    print("=" * 60)
    
    input("Press Enter to start the test...")
    
    # Run the test
    test_enhanced_logging()
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")
    print("📱 Check the Docker logs to see the detailed LLM responses!")
    print("=" * 60)
