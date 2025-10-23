"""
GitHub Service
Handles GitHub API integration and repository operations
"""

import httpx
import base64
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.config import get_settings

settings = get_settings()


class GitHubService:
    """Service for GitHub API integration"""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.timeout = 30.0
    
    async def validate_token(self, access_token: str) -> Dict[str, Any]:
        """Validate GitHub access token"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/user",
                    headers={"Authorization": f"token {access_token}"}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"GitHub token validation failed: {str(e)}")
    
    async def get_user_repositories(self, access_token: str) -> List[Dict[str, Any]]:
        """Get user's repositories"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/user/repos",
                    headers={"Authorization": f"token {access_token}"},
                    params={"sort": "updated", "per_page": 100}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Failed to get repositories: {str(e)}")
    
    async def create_repository(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = False,
        auto_init: bool = True,
        gitignore_template: Optional[str] = None,
        access_token: str = ""
    ) -> Dict[str, Any]:
        """Create new repository"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                data = {
                    "name": name,
                    "description": description,
                    "private": private,
                    "auto_init": auto_init
                }
                
                if gitignore_template:
                    data["gitignore_template"] = gitignore_template
                
                response = await client.post(
                    f"{self.base_url}/user/repos",
                    headers={"Authorization": f"token {access_token}"},
                    json=data
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Repository creation failed: {str(e)}")
    
    async def get_repository_details(
        self,
        owner: str,
        repo: str,
        access_token: str = ""
    ) -> Dict[str, Any]:
        """Get repository details"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = {}
                if access_token:
                    headers["Authorization"] = f"token {access_token}"
                
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Failed to get repository details: {str(e)}")
    
    async def get_repository_contents(
        self,
        owner: str,
        repo: str,
        path: Optional[str] = None,
        branch: str = "main",
        access_token: str = ""
    ) -> List[Dict[str, Any]]:
        """Get repository contents"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = {}
                if access_token:
                    headers["Authorization"] = f"token {access_token}"
                
                url = f"{self.base_url}/repos/{owner}/{repo}/contents"
                if path:
                    url += f"/{path}"
                
                response = await client.get(
                    url,
                    headers=headers,
                    params={"ref": branch}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Failed to get repository contents: {str(e)}")
    
    async def create_commit(
        self,
        owner: str,
        repo: str,
        branch: str,
        files: Dict[str, str],
        message: str,
        access_token: str = ""
    ) -> Dict[str, Any]:
        """Create commit with multiple files"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Get current branch reference
                ref_response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/git/refs/heads/{branch}",
                    headers={"Authorization": f"token {access_token}"}
                )
                
                if ref_response.status_code == 404:
                    # Create branch if it doesn't exist
                    await self._create_branch(owner, repo, branch, access_token)
                    ref_response = await client.get(
                        f"{self.base_url}/repos/{owner}/{repo}/git/refs/heads/{branch}",
                        headers={"Authorization": f"token {access_token}"}
                    )
                
                ref_response.raise_for_status()
                ref_data = ref_response.json()
                base_sha = ref_data["object"]["sha"]
                
                # Get current tree
                tree_response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/git/trees/{base_sha}",
                    headers={"Authorization": f"token {access_token}"}
                )
                tree_response.raise_for_status()
                tree_data = tree_response.json()
                
                # Create new tree with files
                tree_items = []
                for file_path, content in files.items():
                    # Check if file exists
                    existing_file = None
                    for item in tree_data.get("tree", []):
                        if item["path"] == file_path:
                            existing_file = item
                            break
                    
                    # Create blob
                    blob_data = {
                        "content": content,
                        "encoding": "utf-8"
                    }
                    blob_response = await client.post(
                        f"{self.base_url}/repos/{owner}/{repo}/git/blobs",
                        headers={"Authorization": f"token {access_token}"},
                        json=blob_data
                    )
                    blob_response.raise_for_status()
                    blob_sha = blob_response.json()["sha"]
                    
                    tree_items.append({
                        "path": file_path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob_sha
                    })
                
                # Create new tree
                tree_data = {
                    "base_tree": base_sha,
                    "tree": tree_items
                }
                tree_response = await client.post(
                    f"{self.base_url}/repos/{owner}/{repo}/git/trees",
                    headers={"Authorization": f"token {access_token}"},
                    json=tree_data
                )
                tree_response.raise_for_status()
                tree_sha = tree_response.json()["sha"]
                
                # Create commit
                commit_data = {
                    "message": message,
                    "tree": tree_sha,
                    "parents": [base_sha]
                }
                commit_response = await client.post(
                    f"{self.base_url}/repos/{owner}/{repo}/git/commits",
                    headers={"Authorization": f"token {access_token}"},
                    json=commit_data
                )
                commit_response.raise_for_status()
                commit_sha = commit_response.json()["sha"]
                
                # Update branch reference
                ref_data = {
                    "sha": commit_sha
                }
                ref_response = await client.patch(
                    f"{self.base_url}/repos/{owner}/{repo}/git/refs/heads/{branch}",
                    headers={"Authorization": f"token {access_token}"},
                    json=ref_data
                )
                ref_response.raise_for_status()
                
                return {
                    "sha": commit_sha,
                    "message": message,
                    "files_count": len(files)
                }
                
            except httpx.HTTPError as e:
                raise Exception(f"Commit creation failed: {str(e)}")
    
    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str = "main",
        body: Optional[str] = None,
        access_token: str = ""
    ) -> Dict[str, Any]:
        """Create pull request"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                data = {
                    "title": title,
                    "head": head,
                    "base": base
                }
                if body:
                    data["body"] = body
                
                response = await client.post(
                    f"{self.base_url}/repos/{owner}/{repo}/pulls",
                    headers={"Authorization": f"token {access_token}"},
                    json=data
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Pull request creation failed: {str(e)}")
    
    async def get_repository_branches(
        self,
        owner: str,
        repo: str,
        access_token: str = ""
    ) -> List[Dict[str, Any]]:
        """Get repository branches"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = {}
                if access_token:
                    headers["Authorization"] = f"token {access_token}"
                
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/branches",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Failed to get branches: {str(e)}")
    
    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        branch: str = "main",
        access_token: str = ""
    ) -> str:
        """Get file content"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                headers = {}
                if access_token:
                    headers["Authorization"] = f"token {access_token}"
                
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                    headers=headers,
                    params={"ref": branch}
                )
                response.raise_for_status()
                
                file_data = response.json()
                if file_data.get("encoding") == "base64":
                    content = base64.b64decode(file_data["content"]).decode("utf-8")
                else:
                    content = file_data["content"]
                
                return content
                
            except httpx.HTTPError as e:
                raise Exception(f"Failed to get file content: {str(e)}")
    
    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        access_token: str = ""
    ) -> Dict[str, Any]:
        """Create issue"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                data = {
                    "title": title,
                    "body": body
                }
                if labels:
                    data["labels"] = labels
                
                response = await client.post(
                    f"{self.base_url}/repos/{owner}/{repo}/issues",
                    headers={"Authorization": f"token {access_token}"},
                    json=data
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"Issue creation failed: {str(e)}")
    
    async def get_repository_templates(self) -> List[Dict[str, Any]]:
        """Get available repository templates"""
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
    
    # Private helper methods
    
    async def _create_branch(
        self,
        owner: str,
        repo: str,
        branch: str,
        access_token: str
    ) -> None:
        """Create new branch"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Get main branch reference
                main_response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/git/refs/heads/main",
                    headers={"Authorization": f"token {access_token}"}
                )
                main_response.raise_for_status()
                main_sha = main_response.json()["object"]["sha"]
                
                # Create new branch
                branch_data = {
                    "ref": f"refs/heads/{branch}",
                    "sha": main_sha
                }
                response = await client.post(
                    f"{self.base_url}/repos/{owner}/{repo}/git/refs",
                    headers={"Authorization": f"token {access_token}"},
                    json=branch_data
                )
                response.raise_for_status()
                
            except httpx.HTTPError as e:
                raise Exception(f"Branch creation failed: {str(e)}")
