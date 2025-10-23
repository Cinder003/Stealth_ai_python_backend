"""
Retry Helper
Handles retry logic and exponential backoff
"""

import asyncio
import time
import random
from typing import Callable, Any, Optional, Dict, List, Union
from dataclasses import dataclass
from enum import Enum
import functools
import logging


class RetryStrategy(Enum):
    """Retry strategy enumeration"""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    RANDOM = "random"


@dataclass
class RetryConfig:
    """Retry configuration"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    jitter: bool = True
    backoff_multiplier: float = 2.0
    exceptions: tuple = (Exception,)


@dataclass
class RetryResult:
    """Result of retry operation"""
    success: bool
    result: Any = None
    attempts: int = 0
    total_time: float = 0.0
    last_exception: Optional[Exception] = None
    errors: List[Exception] = None


class RetryHelper:
    """Handles retry logic and exponential backoff"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def retry(
        self,
        func: Callable,
        config: Optional[RetryConfig] = None,
        *args,
        **kwargs
    ) -> RetryResult:
        """Retry a function with the given configuration"""
        if config is None:
            config = RetryConfig()
        
        start_time = time.time()
        errors = []
        
        for attempt in range(config.max_attempts):
            try:
                result = func(*args, **kwargs)
                total_time = time.time() - start_time
                
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempt + 1,
                    total_time=total_time,
                    last_exception=None,
                    errors=errors
                )
            
            except config.exceptions as e:
                errors.append(e)
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == config.max_attempts - 1:
                    # Last attempt failed
                    total_time = time.time() - start_time
                    return RetryResult(
                        success=False,
                        result=None,
                        attempts=attempt + 1,
                        total_time=total_time,
                        last_exception=e,
                        errors=errors
                    )
                
                # Calculate delay for next attempt
                delay = self._calculate_delay(attempt, config)
                
                if delay > 0:
                    self.logger.info(f"Waiting {delay:.2f} seconds before retry...")
                    time.sleep(delay)
        
        # This should never be reached
        return RetryResult(
            success=False,
            result=None,
            attempts=config.max_attempts,
            total_time=time.time() - start_time,
            last_exception=errors[-1] if errors else None,
            errors=errors
        )
    
    async def retry_async(
        self,
        func: Callable,
        config: Optional[RetryConfig] = None,
        *args,
        **kwargs
    ) -> RetryResult:
        """Retry an async function with the given configuration"""
        if config is None:
            config = RetryConfig()
        
        start_time = time.time()
        errors = []
        
        for attempt in range(config.max_attempts):
            try:
                result = await func(*args, **kwargs)
                total_time = time.time() - start_time
                
                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempt + 1,
                    total_time=total_time,
                    last_exception=None,
                    errors=errors
                )
            
            except config.exceptions as e:
                errors.append(e)
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == config.max_attempts - 1:
                    # Last attempt failed
                    total_time = time.time() - start_time
                    return RetryResult(
                        success=False,
                        result=None,
                        attempts=attempt + 1,
                        total_time=total_time,
                        last_exception=e,
                        errors=errors
                    )
                
                # Calculate delay for next attempt
                delay = self._calculate_delay(attempt, config)
                
                if delay > 0:
                    self.logger.info(f"Waiting {delay:.2f} seconds before retry...")
                    await asyncio.sleep(delay)
        
        # This should never be reached
        return RetryResult(
            success=False,
            result=None,
            attempts=config.max_attempts,
            total_time=time.time() - start_time,
            last_exception=errors[-1] if errors else None,
            errors=errors
        )
    
    def retry_decorator(
        self,
        config: Optional[RetryConfig] = None,
        *retry_args,
        **retry_kwargs
    ):
        """Decorator for retrying functions"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self.retry(func, config, *args, **kwargs)
            return wrapper
        return decorator
    
    def retry_async_decorator(
        self,
        config: Optional[RetryConfig] = None,
        *retry_args,
        **retry_kwargs
    ):
        """Decorator for retrying async functions"""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await self.retry_async(func, config, *args, **kwargs)
            return wrapper
        return decorator
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay for the given attempt"""
        if attempt == 0:
            return 0
        
        if config.strategy == RetryStrategy.FIXED:
            delay = config.base_delay
        elif config.strategy == RetryStrategy.EXPONENTIAL:
            delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
        elif config.strategy == RetryStrategy.LINEAR:
            delay = config.base_delay * attempt
        elif config.strategy == RetryStrategy.RANDOM:
            delay = random.uniform(0, config.base_delay * (config.backoff_multiplier ** (attempt - 1)))
        else:
            delay = config.base_delay
        
        # Apply jitter
        if config.jitter:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)
        
        # Cap at max delay
        delay = min(delay, config.max_delay)
        
        return max(0, delay)
    
    def create_retry_config(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        jitter: bool = True,
        backoff_multiplier: float = 2.0,
        exceptions: tuple = (Exception,)
    ) -> RetryConfig:
        """Create a retry configuration"""
        return RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=strategy,
            jitter=jitter,
            backoff_multiplier=backoff_multiplier,
            exceptions=exceptions
        )
    
    def create_exponential_backoff_config(
        self,
        max_attempts: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True
    ) -> RetryConfig:
        """Create an exponential backoff retry configuration"""
        return RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=RetryStrategy.EXPONENTIAL,
            jitter=jitter,
            backoff_multiplier=backoff_multiplier,
            exceptions=(Exception,)
        )
    
    def create_linear_backoff_config(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True
    ) -> RetryConfig:
        """Create a linear backoff retry configuration"""
        return RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=RetryStrategy.LINEAR,
            jitter=jitter,
            backoff_multiplier=1.0,
            exceptions=(Exception,)
        )
    
    def create_fixed_delay_config(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        jitter: bool = True
    ) -> RetryConfig:
        """Create a fixed delay retry configuration"""
        return RetryConfig(
            max_attempts=max_attempts,
            base_delay=delay,
            max_delay=delay,
            strategy=RetryStrategy.FIXED,
            jitter=jitter,
            backoff_multiplier=1.0,
            exceptions=(Exception,)
        )
    
    def create_random_delay_config(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0
    ) -> RetryConfig:
        """Create a random delay retry configuration"""
        return RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=RetryStrategy.RANDOM,
            jitter=True,
            backoff_multiplier=backoff_multiplier,
            exceptions=(Exception,)
        )


# Convenience functions
def retry(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    exceptions: tuple = (Exception,),
    *args,
    **kwargs
) -> RetryResult:
    """Convenience function for retrying a function"""
    helper = RetryHelper()
    config = helper.create_retry_config(
        max_attempts=max_attempts,
        base_delay=base_delay,
        strategy=strategy,
        exceptions=exceptions
    )
    return helper.retry(func, config, *args, **kwargs)


async def retry_async(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    exceptions: tuple = (Exception,),
    *args,
    **kwargs
) -> RetryResult:
    """Convenience function for retrying an async function"""
    helper = RetryHelper()
    config = helper.create_retry_config(
        max_attempts=max_attempts,
        base_delay=base_delay,
        strategy=strategy,
        exceptions=exceptions
    )
    return await helper.retry_async(func, config, *args, **kwargs)


def retry_decorator(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying functions"""
    helper = RetryHelper()
    config = helper.create_retry_config(
        max_attempts=max_attempts,
        base_delay=base_delay,
        strategy=strategy,
        exceptions=exceptions
    )
    return helper.retry_decorator(config)


def retry_async_decorator(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying async functions"""
    helper = RetryHelper()
    config = helper.create_retry_config(
        max_attempts=max_attempts,
        base_delay=base_delay,
        strategy=strategy,
        exceptions=exceptions
    )
    return helper.retry_async_decorator(config)
