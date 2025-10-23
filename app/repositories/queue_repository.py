"""
Queue Repository
Handles NATS queue operations
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

import nats
from nats.aio.client import Client as NATS

from app.core.config import get_settings

settings = get_settings()


class QueueRepository:
    """Repository for NATS queue operations"""
    
    def __init__(self):
        self.nats_client = None
        self.js = None
        self._connect()
    
    def _connect(self):
        """Connect to NATS server"""
        try:
            self.nats_client = nats.connect(
                settings.NATS_URL,
                max_reconnect_attempts=settings.NATS_MAX_RECONNECT_ATTEMPTS,
                reconnect_time_wait=settings.NATS_RECONNECT_TIME_WAIT
            )
            self.js = self.nats_client.jetstream()
        except Exception as e:
            print(f"NATS connection failed: {str(e)}")
            self.nats_client = None
    
    def is_connected(self) -> bool:
        """Check if NATS is connected"""
        return self.nats_client is not None
    
    def publish(
        self,
        subject: str,
        data: Any,
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """Publish message to subject"""
        if not self.is_connected():
            return False
        
        try:
            if isinstance(data, (dict, list)):
                message = json.dumps(data).encode()
            else:
                message = str(data).encode()
            
            self.nats_client.publish(subject, message, headers=headers)
            return True
        except Exception:
            return False
    
    def subscribe(
        self,
        subject: str,
        callback: Callable,
        queue: Optional[str] = None
    ) -> bool:
        """Subscribe to subject"""
        if not self.is_connected():
            return False
        
        try:
            if queue:
                self.nats_client.subscribe(subject, queue=queue, cb=callback)
            else:
                self.nats_client.subscribe(subject, cb=callback)
            return True
        except Exception:
            return False
    
    def unsubscribe(self, subject: str) -> bool:
        """Unsubscribe from subject"""
        if not self.is_connected():
            return False
        
        try:
            self.nats_client.unsubscribe(subject)
            return True
        except Exception:
            return False
    
    def close(self):
        """Close NATS connection"""
        if self.nats_client:
            self.nats_client.close()
