"""
Script to view Docker container logs for Figma processing
Shows the generated LLM code and processing details
"""

import subprocess
import sys
import time

def view_app_logs():
    """View logs from the app container"""
    print("📱 Viewing app container logs...")
    print("=" * 50)
    
    try:
        # Follow logs in real-time
        subprocess.run([
            "docker-compose", "logs", "-f", "app"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Stopped viewing logs")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error viewing logs: {e}")

def view_all_logs():
    """View logs from all containers"""
    print("🐳 Viewing all container logs...")
    print("=" * 50)
    
    try:
        # Follow logs from all containers
        subprocess.run([
            "docker-compose", "logs", "-f"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Stopped viewing logs")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error viewing logs: {e}")

def view_recent_logs():
    """View recent logs (last 100 lines)"""
    print("📜 Viewing recent logs...")
    print("=" * 50)
    
    try:
        # Get last 100 lines from app container
        result = subprocess.run([
            "docker-compose", "logs", "--tail=100", "app"
        ], capture_output=True, text=True, check=True)
        
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting logs: {e}")

def view_worker_logs():
    """View logs from worker container (if processing is done there)"""
    print("👷 Viewing worker container logs...")
    print("=" * 50)
    
    try:
        subprocess.run([
            "docker-compose", "logs", "-f", "worker"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Stopped viewing logs")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error viewing logs: {e}")

def main():
    """Main function to choose log viewing option"""
    print("🐳 Docker Logs Viewer for Figma Processing")
    print("=" * 50)
    print("Choose an option:")
    print("1. View app container logs (real-time)")
    print("2. View all container logs (real-time)")
    print("3. View recent app logs (last 100 lines)")
    print("4. View worker container logs (real-time)")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                view_app_logs()
                break
            elif choice == "2":
                view_all_logs()
                break
            elif choice == "3":
                view_recent_logs()
                break
            elif choice == "4":
                view_worker_logs()
                break
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
