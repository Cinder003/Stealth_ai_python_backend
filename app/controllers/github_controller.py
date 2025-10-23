"""
GitHub Integration Controller
Handles GitHub repository operations and code deployment
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import time

from app.models.schemas import GitHubDeployRequest, GitHubDeployResponse
from app.services.github_service import GitHubService
from app.services.cache_service import CacheService
from app.services.observability_service import ObservabilityService
from app.core.config import get_settings

settings = get_settings()


class GitHubController:
    """Controller for GitHub integration"""
    
    def __init__(self):
        self.github_service = GitHubService()
        self.cache_service = CacheService()
        self.observability_service = ObservabilityService()
    
    async def connect_account(
        self,
        access_token: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Connect to GitHub account
        """
        try:
            # Validate token
            user_info = await self.github_service.validate_token(access_token)
            
            # Store connection
            connection_data = {
                "access_token": access_token,
                "user_id": user_id,
                "github_user_id": user_info.get("id"),
                "username": user_info.get("login"),
                "connected_at": datetime.utcnow().isoformat()
            }
            
            await self.cache_service.set(
                f"github_connection:{user_id}",
                connection_data,
                ttl=86400 * 30  # 30 days
            )
            
            return {
                "success": True,
                "user_info": user_info,
                "connected_at": connection_data["connected_at"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_user_repositories(
        self,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's GitHub repositories
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"github_connection:{user_id}")
            if not connection:
                raise Exception("GitHub account not connected")
            
            # Get repositories
            repositories = await self.github_service.get_user_repositories(
                access_token=connection["access_token"]
            )
            
            return repositories
            
        except Exception as e:
            raise Exception(f"Failed to get repositories: {str(e)}")
    
    async def create_repository(
        self,
        request: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new GitHub repository
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"github_connection:{user_id}")
            if not connection:
                raise Exception("GitHub account not connected")
            
            # Create repository
            repository = await self.github_service.create_repository(
                name=request["name"],
                description=request.get("description"),
                private=request.get("private", False),
                auto_init=request.get("auto_init", True),
                gitignore_template=request.get("gitignore_template"),
                access_token=connection["access_token"]
            )
            
            return {
                "success": True,
                "repository": repository
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_repository_details(
        self,
        owner: str,
        repo: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a repository
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"github_connection:{user_id}")
            if not connection:
                raise Exception("GitHub account not connected")
            
            # Get repository details
            details = await self.github_service.get_repository_details(
                owner=owner,
                repo=repo,
                access_token=connection["access_token"]
            )
            
            return details
            
        except Exception as e:
            raise Exception(f"Failed to get repository details: {str(e)}")
    
    async def get_repository_contents(
        self,
        owner: str,
        repo: str,
        path: Optional[str] = None,
        branch: str = "main",
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get repository contents
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"github_connection:{user_id}")
            if not connection:
                raise Exception("GitHub account not connected")
            
            # Get contents
            contents = await self.github_service.get_repository_contents(
                owner=owner,
                repo=repo,
                path=path,
                branch=branch,
                access_token=connection["access_token"]
            )
            
            return contents
            
        except Exception as e:
            raise Exception(f"Failed to get contents: {str(e)}")
    
    async def deploy_code(
        self,
        request: GitHubDeployRequest,
        background_tasks,
        user_id: Optional[str] = None
    ) -> GitHubDeployResponse:
        """
        Deploy generated code to GitHub repository
        """
        start_time = time.time()
        
        try:
            # Get connection
            connection = await self.cache_service.get(f"github_connection:{user_id}")
            if not connection:
                raise Exception("GitHub account not connected")
            
            # Parse repository
            owner, repo = request.repository.split("/")
            
            # Create commit
            commit_result = await self.github_service.create_commit(
                owner=owner,
                repo=repo,
                branch=request.branch,
                files=request.files,
                message=request.commit_message,
                access_token=connection["access_token"]
            )
            
            # Create pull request if requested
            pr_url = None
            if request.create_pr:
                pr = await self.github_service.create_pull_request(
                    owner=owner,
                    repo=repo,
                    title=request.pr_title or f"Generated code: {request.commit_message}",
                    head=request.branch,
                    base="main",
                    body=request.pr_description,
                    access_token=connection["access_token"]
                )
                pr_url = pr.get("html_url")
            
            # Log deployment
            await self.observability_service.log_github_deployment(
                request=request,
                commit_sha=commit_result.get("sha"),
                user_id=user_id
            )
            
            return GitHubDeployResponse(
                success=True,
                commit_sha=commit_result.get("sha"),
                pr_url=pr_url,
                repository_url=f"https://github.com/{owner}/{repo}",
                deployment_url=f"https://github.com/{owner}/{repo}/tree/{request.branch}"
            )
            
        except Exception as e:
            return GitHubDeployResponse(
                success=False,
                commit_sha=None,
                pr_url=None,
                repository_url="",
                deployment_url=None
            )
    
    async def commit_code(
        self,
        request: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Commit code to GitHub repository
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"github_connection:{user_id}")
            if not connection:
                raise Exception("GitHub account not connected")
            
            # Parse repository
            owner, repo = request["repository"].split("/")
            
            # Create commit
            result = await self.github_service.create_commit(
                owner=owner,
                repo=repo,
                branch=request.get("branch", "main"),
                files=request["files"],
                message=request["message"],
                access_token=connection["access_token"]
            )
            
            return {
                "success": True,
                "commit": result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str = "main",
        body: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create pull request
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"github_connection:{user_id}")
            if not connection:
                raise Exception("GitHub account not connected")
            
            # Create pull request
            pr = await self.github_service.create_pull_request(
                owner=owner,
                repo=repo,
                title=title,
                head=head,
                base=base,
                body=body,
                access_token=connection["access_token"]
            )
            
            return {
                "success": True,
                "pull_request": pr
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_repository_branches(
        self,
        owner: str,
        repo: str,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get repository branches
        """
        try:
            # Get connection
            connection = await self.cache_service.get(f"github_connection:{user_id}")
            if not connection:
                raise Exception("GitHub account not connected")
            
            # Get branches
            branches = await self.github_service.get_repository_branches(
                owner=owner,
                repo=repo,
                access_token=connection["access_token"]
            )
            
            return branches
            
        except Exception as e:
            raise Exception(f"Failed to get branches: {str(e)}")
    
    async def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GitHub webhook events"""
        try:
            event_type = webhook_data.get("event_type")
            
            if event_type == "push":
                # Handle push event
                await self._handle_push_event(webhook_data)
            elif event_type == "pull_request":
                # Handle pull request event
                await self._handle_pull_request_event(webhook_data)
            elif event_type == "issues":
                # Handle issues event
                await self._handle_issues_event(webhook_data)
            
            return {"success": True, "event_processed": event_type}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get available GitHub repository templates"""
        return [
            {
                "name": "react_app",
                "description": "React application template",
                "gitignore_template": "Node",
                "features": ["package.json", "src/", "public/"]
            },
            {
                "name": "nodejs_api",
                "description": "Node.js API template",
                "gitignore_template": "Node",
                "features": ["package.json", "src/", "tests/"]
            },
            {
                "name": "python_fastapi",
                "description": "Python FastAPI template",
                "gitignore_template": "Python",
                "features": ["requirements.txt", "src/", "tests/"]
            }
        ]
    
    async def _handle_push_event(self, webhook_data: Dict[str, Any]):
        """Handle push webhook event"""
        # Process push event for potential deployments
        pass
    
    async def _handle_pull_request_event(self, webhook_data: Dict[str, Any]):
        """Handle pull request webhook event"""
        # Process PR event for code review triggers
        pass
    
    async def _handle_issues_event(self, webhook_data: Dict[str, Any]):
        """Handle issues webhook event"""
        # Process issues event for potential code generation
        pass
