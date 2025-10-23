"""
Queue Service
Handles NATS messaging and job queuing
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

import nats
from nats.aio.client import Client as NATS

from app.core.config import get_settings

settings = get_settings()


class QueueService:
    """Service for NATS messaging and job queuing"""
    
    def __init__(self):
        self.nats_url = settings.NATS_URL
        self.stream_name = settings.NATS_STREAM_NAME
        self.consumer_name = settings.NATS_CONSUMER_NAME
        self.nc: Optional[NATS] = None
        self.js = None
        self.consumers = {}
    
    async def connect(self) -> bool:
        """Connect to NATS server"""
        try:
            self.nc = await nats.connect(
                self.nats_url,
                max_reconnect_attempts=settings.NATS_MAX_RECONNECT_ATTEMPTS,
                reconnect_time_wait=settings.NATS_RECONNECT_TIME_WAIT
            )
            
            # Create JetStream context
            self.js = self.nc.jetstream()
            
            # Create stream if it doesn't exist
            await self._create_stream()
            
            return True
            
        except Exception as e:
            print(f"NATS connection failed: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from NATS server"""
        try:
            if self.nc:
                await self.nc.close()
        except Exception as e:
            print(f"NATS disconnection failed: {str(e)}")
    
    async def publish_job(
        self,
        job_type: str,
        payload: Dict[str, Any],
        priority: int = 0,
        delay: Optional[int] = None
    ) -> str:
        """Publish a job to the queue"""
        try:
            if not self.js:
                await self.connect()
            
            job_id = str(uuid.uuid4())
            job_data = {
                "job_id": job_id,
                "job_type": job_type,
                "payload": payload,
                "priority": priority,
                "created_at": datetime.utcnow().isoformat(),
                "delay": delay
            }
            
            subject = f"{self.stream_name}.{job_type}"
            message = json.dumps(job_data).encode()
            
            # Publish with optional delay
            if delay:
                await self.js.publish(
                    subject,
                    message,
                    headers={"delay": str(delay)}
                )
            else:
                await self.js.publish(subject, message)
            
            return job_id
            
        except Exception as e:
            raise Exception(f"Job publishing failed: {str(e)}")
    
    async def subscribe_to_jobs(
        self,
        job_types: List[str],
        handler: Callable[[Dict[str, Any]], None],
        consumer_name: Optional[str] = None
    ) -> str:
        """Subscribe to job processing"""
        try:
            if not self.js:
                await self.connect()
            
            consumer_name = consumer_name or f"{self.consumer_name}_{uuid.uuid4().hex[:8]}"
            
            # Create consumer for each job type
            for job_type in job_types:
                subject = f"{self.stream_name}.{job_type}"
                
                # Create pull consumer
                consumer = await self.js.pull_subscribe(
                    subject,
                    consumer_name,
                    durable=True
                )
                
                self.consumers[consumer_name] = {
                    "consumer": consumer,
                    "job_type": job_type,
                    "handler": handler
                }
            
            # Start processing
            asyncio.create_task(self._process_jobs(consumer_name))
            
            return consumer_name
            
        except Exception as e:
            raise Exception(f"Job subscription failed: {str(e)}")
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status from queue"""
        try:
            # This would typically query a database or cache
            # For now, return a placeholder
            return {
                "job_id": job_id,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Job status retrieval failed: {str(e)}")
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        try:
            # This would typically update job status in database
            # For now, return success
            return True
            
        except Exception as e:
            raise Exception(f"Job cancellation failed: {str(e)}")
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        try:
            if not self.js:
                await self.connect()
            
            # Get stream info
            stream_info = await self.js.stream_info(self.stream_name)
            
            return {
                "stream_name": self.stream_name,
                "total_messages": stream_info.state.messages,
                "total_bytes": stream_info.state.bytes,
                "consumers": stream_info.state.consumers,
                "first_sequence": stream_info.state.first_seq,
                "last_sequence": stream_info.state.last_seq
            }
            
        except Exception as e:
            raise Exception(f"Queue stats retrieval failed: {str(e)}")
    
    async def purge_queue(self, job_type: Optional[str] = None) -> bool:
        """Purge queue messages"""
        try:
            if not self.js:
                await self.connect()
            
            if job_type:
                subject = f"{self.stream_name}.{job_type}"
                await self.js.purge_stream(self.stream_name, filter=subject)
            else:
                await self.js.purge_stream(self.stream_name)
            
            return True
            
        except Exception as e:
            raise Exception(f"Queue purge failed: {str(e)}")
    
    async def create_consumer_group(
        self,
        group_name: str,
        job_types: List[str],
        handler: Callable[[Dict[str, Any]], None]
    ) -> str:
        """Create a consumer group for load balancing"""
        try:
            if not self.js:
                await self.connect()
            
            # Create consumer group
            consumer_name = f"{group_name}_{uuid.uuid4().hex[:8]}"
            
            for job_type in job_types:
                subject = f"{self.stream_name}.{job_type}"
                
                # Create push consumer for group
                consumer = await self.js.subscribe(
                    subject,
                    consumer=consumer_name,
                    durable=True,
                    deliver_group=group_name
                )
                
                self.consumers[consumer_name] = {
                    "consumer": consumer,
                    "job_type": job_type,
                    "handler": handler,
                    "group": group_name
                }
            
            # Start processing
            asyncio.create_task(self._process_jobs(consumer_name))
            
            return consumer_name
            
        except Exception as e:
            raise Exception(f"Consumer group creation failed: {str(e)}")
    
    async def stop_consumer(self, consumer_name: str) -> bool:
        """Stop a consumer"""
        try:
            if consumer_name in self.consumers:
                consumer_info = self.consumers[consumer_name]
                consumer = consumer_info["consumer"]
                
                # Unsubscribe consumer
                await consumer.unsubscribe()
                
                # Remove from consumers
                del self.consumers[consumer_name]
                
                return True
            
            return False
            
        except Exception as e:
            raise Exception(f"Consumer stop failed: {str(e)}")
    
    # Private helper methods
    
    async def _create_stream(self):
        """Create NATS stream if it doesn't exist"""
        try:
            # Check if stream exists
            try:
                await self.js.stream_info(self.stream_name)
                return  # Stream already exists
            except:
                pass  # Stream doesn't exist, create it
            
            # Create stream
            await self.js.add_stream(
                name=self.stream_name,
                subjects=[f"{self.stream_name}.*"],
                retention="workqueue",
                max_age=86400,  # 24 hours
                max_msgs=100000,
                max_bytes=1024 * 1024 * 1024,  # 1GB
                storage="file"
            )
            
        except Exception as e:
            print(f"Stream creation failed: {str(e)}")
    
    async def _process_jobs(self, consumer_name: str):
        """Process jobs from queue"""
        try:
            if consumer_name not in self.consumers:
                return
            
            consumer_info = self.consumers[consumer_name]
            consumer = consumer_info["consumer"]
            handler = consumer_info["handler"]
            
            while True:
                try:
                    # Fetch messages
                    messages = await consumer.fetch(1, timeout=1.0)
                    
                    for msg in messages:
                        try:
                            # Parse job data
                            job_data = json.loads(msg.data.decode())
                            
                            # Process job
                            await handler(job_data)
                            
                            # Acknowledge message
                            await msg.ack()
                            
                        except Exception as e:
                            print(f"Job processing error: {str(e)}")
                            # Negative acknowledge for retry
                            await msg.nak()
                    
                except asyncio.TimeoutError:
                    # No messages, continue
                    continue
                except Exception as e:
                    print(f"Queue processing error: {str(e)}")
                    await asyncio.sleep(1)
                    
        except Exception as e:
            print(f"Job processing failed: {str(e)}")
    
    async def _handle_job_error(
        self,
        job_data: Dict[str, Any],
        error: Exception
    ):
        """Handle job processing errors"""
        try:
            # Log error
            print(f"Job {job_data.get('job_id')} failed: {str(error)}")
            
            # Implement retry logic or dead letter queue
            # This would typically update job status in database
            
        except Exception as e:
            print(f"Error handling failed: {str(e)}")
