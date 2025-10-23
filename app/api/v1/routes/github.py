"""
GitHub Integration Routes
Handles GitHub repository operations and code deployment
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.schemas import GitHubDeployRequest, GitHubDeployResponse
from app.controllers.github_controller import GitHubController
from app.core.security import get_current_user
from app.core.config import get_settings

router = APIRouter(prefix="/github", tags=["GitHub Integration"])
settings = get_settings()

# Initialize controller
github_controller = GitHubController()


class GitHubRepositoryRequest(BaseModel):
    """Request for GitHub repository operations"""
    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    branch: str = Field(default="main", description="Target branch")
    path: Optional[str] = Field(default=None, description="Specific path in repository")


class GitHubCreateRepoRequest(BaseModel):
    """Request for creating GitHub repository"""
    name: str = Field(..., description="Repository name")
    description: Optional[str] = Field(default=None, description="Repository description")
    private: bool = Field(default=False, description="Make repository private")
    auto_init: bool = Field(default=True, description="Initialize with README")
    gitignore_template: Optional[str] = Field(default=None, description="Gitignore template")


class GitHubCommitRequest(BaseModel):
    """Request for committing code to GitHub"""
    message: str = Field(..., description="Commit message")
    files: Dict[str, str] = Field(..., description="Files to commit (path: content)")
    branch: str = Field(default="main", description="Target branch")
    create_branch: bool = Field(default=False, description="Create new branch if it doesn't exist")


@router.post("/connect")
async def connect_github(
    access_token: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Connect to GitHub account
    """
    try:
        result = await github_controller.connect_account(
            access_token=access_token,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"GitHub connection failed: {str(e)}")


@router.get("/repositories")
async def get_github_repositories(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's GitHub repositories
    """
    try:
        repositories = await github_controller.get_user_repositories(
            user_id=current_user.get("id")
        )
        return {"repositories": repositories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get repositories: {str(e)}")


@router.post("/repositories", response_model=Dict[str, Any])
async def create_github_repository(
    request: GitHubCreateRepoRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create new GitHub repository
    """
    try:
        repository = await github_controller.create_repository(
            request=request,
            user_id=current_user.get("id")
        )
        return repository
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository creation failed: {str(e)}")


@router.get("/repositories/{owner}/{repo}")
async def get_repository_details(
    owner: str,
    repo: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a repository
    """
    try:
        details = await github_controller.get_repository_details(
            owner=owner,
            repo=repo,
            user_id=current_user.get("id")
        )
        return details
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Repository not found: {str(e)}")


@router.get("/repositories/{owner}/{repo}/contents")
async def get_repository_contents(
    owner: str,
    repo: str,
    path: Optional[str] = None,
    branch: str = "main",
    current_user: dict = Depends(get_current_user)
):
    """
    Get repository contents
    """
    try:
        contents = await github_controller.get_repository_contents(
            owner=owner,
            repo=repo,
            path=path,
            branch=branch,
            user_id=current_user.get("id")
        )
        return {"contents": contents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contents: {str(e)}")


@router.post("/deploy", response_model=GitHubDeployResponse)
async def deploy_to_github(
    request: GitHubDeployRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Deploy generated code to GitHub repository
    """
    try:
        result = await github_controller.deploy_code(
            request=request,
            background_tasks=background_tasks,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")


@router.post("/commit")
async def commit_to_github(
    request: GitHubCommitRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Commit code to GitHub repository
    """
    try:
        result = await github_controller.commit_code(
            request=request,
            user_id=current_user.get("id")
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Commit failed: {str(e)}")


@router.post("/pull-request")
async def create_pull_request(
    owner: str,
    repo: str,
    title: str,
    head: str,
    base: str = "main",
    body: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Create pull request
    """
    try:
        pr = await github_controller.create_pull_request(
            owner=owner,
            repo=repo,
            title=title,
            head=head,
            base=base,
            body=body,
            user_id=current_user.get("id")
        )
        return pr
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pull request creation failed: {str(e)}")


@router.get("/branches/{owner}/{repo}")
async def get_repository_branches(
    owner: str,
    repo: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get repository branches
    """
    try:
        branches = await github_controller.get_repository_branches(
            owner=owner,
            repo=repo,
            user_id=current_user.get("id")
        )
        return {"branches": branches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get branches: {str(e)}")


@router.post("/webhook")
async def github_webhook(
    webhook_data: Dict[str, Any]
):
    """
    Handle GitHub webhook events
    """
    try:
        result = await github_controller.handle_webhook(webhook_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook processing failed: {str(e)}")


@router.get("/templates")
async def get_github_templates():
    """
    Get available GitHub repository templates
    """
    try:
        templates = await github_controller.get_available_templates()
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")
