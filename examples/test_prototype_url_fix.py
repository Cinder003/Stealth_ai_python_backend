import asyncio
import httpx
import json
import os

API_URL = "http://localhost:6000/api/v1/figma/process-url-frames"
HEALTH_URL = "http://localhost:6000/api/v1/health"
API_KEY = "test-api-key"

async def test_prototype_url_fix():
    print("Testing Prototype URL Fix...")
    print("=" * 60)
    
    # 1. Check API health
    try:
        async with httpx.AsyncClient() as client:
            health_response = await client.get(HEALTH_URL)
            health_response.raise_for_status()
            print(f"SUCCESS: API Health Check: {health_response.json()}")
    except httpx.HTTPStatusError as e:
        print(f"ERROR: API Health Check Failed: {e.response.status_code} - {e.response.text}")
        return
    except httpx.RequestError as e:
        print(f"ERROR: API Health Check Failed: Could not connect to {HEALTH_URL}. Is the Docker container running? {e}")
        return

    # 2. Test the prototype URL (should extract specific node IDs)
    request_body = {
        "figma_url": "https://www.figma.com/proto/dfvjl4ghcsdlD8hrVg4tpi/QIS_Project?page-id=0%3A1&node-id=92-11787&viewport=-550%2C1488%2C0.25&t=YnF0N8qqVDw2Gsw4-1&scaling=min-zoom&content-scaling=fixed&starting-point-node-id=26%3A59&show-proto-sidebar=1",
        "user_message": "Generate a modern web application from this QIS project prototype",
        "framework": "react",
        "backend_framework": "nodejs"
    }

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    print(f"\nTesting with prototype URL:")
    print(f"   URL: {request_body['figma_url']}")
    print(f"   Expected: Should extract node IDs '92-11787' and '26:59' from URL")
    print(f"   Expected: Should process only 2 frames instead of 2444 frames")
    print(f"   Expected: Should use get_nodes() API for each specific frame")
    print(f"\nSending POST request to {API_URL}")

    # 3. Send request
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(API_URL, headers=headers, json=request_body)
            response.raise_for_status()
            result = response.json()

            print("\nSUCCESS: Request Successful!")
            print(f"Summary: {result.get('frames_processed')}/{result.get('total_frames')} frames processed successfully.")
            print(f"Total Processing Time: {result.get('metadata', {}).get('processing_time', 0):.2f} seconds")
            print(f"Total Tokens Used: {result.get('metadata', {}).get('total_tokens', 0):,}")
            print(f"Project Directory: {result.get('saved_files', {}).get('project_dir', 'N/A')}")
            print(f"Total Files Saved: {result.get('saved_files', {}).get('total_files', 0)}")

            # Check if it processed the expected number of frames
            total_frames = result.get('total_frames', 0)
            if total_frames <= 5:  # Should be 2 frames, but allow some tolerance
                print(f"SUCCESS: Processed only {total_frames} frames (expected ~2 frames)")
                print(f"SUCCESS: This means the fix is working - it's using specific node IDs from the URL!")
            else:
                print(f"ISSUE: Processed {total_frames} frames (expected ~2 frames)")
                print(f"ISSUE: This means it's still processing all frames instead of specific ones")

            # Show frame results
            frame_results = result.get('metadata', {}).get('frame_results', [])
            if frame_results:
                print(f"\nFrame Results:")
                for i, frame in enumerate(frame_results):
                    status = "SUCCESS" if frame.get('success') else "ERROR"
                    print(f"   {i+1}. {status} Frame {frame.get('frame_id', 'Unknown')}: {frame.get('frame_name', 'Unknown')}")

            # Verify some basic structure
            assert result["success"] is True
            assert result["frames_processed"] > 0
            assert "project_id" in result
            assert "files" in result
            assert "metadata" in result

    except httpx.HTTPStatusError as e:
        print(f"ERROR: Request Failed: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"ERROR: Request Failed: An error occurred while requesting {e.request.url!r}.")
        print(f"   Error details: {e}")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_prototype_url_fix())
