import time
import psutil
import traceback
import structlog
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional, Callable, get_type_hints
from pydantic import BaseModel, ValidationError
import inspect
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

LOG_LEVEL = int(os.getenv("LOG_LEVEL", 10))

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVEL),  # INFO level
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class ExecutionResult(BaseModel):
    """Standard response format for decorated functions"""
    result: Any = None
    status: str  # "success" or "error"
    errors: Optional[List[str]] = None
    execution_time: float
    memory_usage: Dict[str, int]
    cpu_usage: float
    timestamp: str
    function_name: str


def monitor_function(
    validate_input: bool = True,
    validate_output: bool = True,
    log_execution: bool = True,
    log_level: str = "INFO",
    return_raw_result: bool = False
):
    """
    Multi-purpose decorator that provides:
    - Execution timing
    - Memory and CPU monitoring
    - Exception handling
    - Pydantic input/output validation
    - Structured logging
    
    Args:
        validate_input: Enable input validation using type hints
        validate_output: Enable output validation using type hints
        log_execution: Enable structured logging
        log_level: Log level for successful executions
        return_raw_result: If True, return original result on success, 
                          structured format only on error
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize monitoring
            start_time = time.time()
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss
            cpu_before = process.cpu_percent()
            
            # Get function signature for validation
            sig = inspect.signature(func)
            type_hints = get_type_hints(func)
            
            errors = []
            result = None
            status = "success"
            
            try:
                # Input validation
                if validate_input and type_hints:
                    try:
                        # Bind arguments to parameters
                        bound_args = sig.bind(*args, **kwargs)
                        bound_args.apply_defaults()
                        
                        # Validate each parameter
                        for param_name, param_value in bound_args.arguments.items():
                            if param_name in type_hints:
                                expected_type = type_hints[param_name]
                                # Skip validation for complex types that aren't BaseModel
                                if (isinstance(expected_type, type) and 
                                    issubclass(expected_type, BaseModel)):
                                    try:
                                        if not isinstance(param_value, expected_type):
                                            expected_type(**param_value if isinstance(param_value, dict) else param_value.__dict__)
                                    except ValidationError as e:
                                        errors.append(f"Input validation failed for {param_name}: {str(e)}")
                                        
                    except Exception as e:
                        errors.append(f"Input validation error: {str(e)}")
                
                # Execute the function if no input validation errors
                if not errors:
                    result = func(*args, **kwargs)
                    
                    # Output validation
                    if validate_output and 'return' in type_hints:
                        return_type = type_hints['return']
                        if (isinstance(return_type, type) and 
                            issubclass(return_type, BaseModel)):
                            try:
                                if not isinstance(result, return_type):
                                    return_type(**result if isinstance(result, dict) else result.__dict__)
                            except ValidationError as e:
                                errors.append(f"Output validation failed: {str(e)}")
                                status = "error"
                else:
                    status = "error"
                    
            except Exception as e:
                errors.append(f"Execution error: {str(e)}")
                errors.append(f"Traceback: {traceback.format_exc()}")
                status = "error"
                result = None
            
            # Calculate metrics
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Memory monitoring
            memory_after = process.memory_info().rss
            memory_peak = memory_after  # Simplified - could use memory_info().peak_rss on some systems
            
            # CPU monitoring (get current usage)
            cpu_after = process.cpu_percent()
            cpu_usage = max(cpu_before, cpu_after)  # Use the higher value
            
            # Create structured result
            execution_result = ExecutionResult(
                result=result,
                status=status,
                errors=errors if errors else None,
                execution_time=execution_time, # in seconds
                memory_usage={
                    "before": memory_before,
                    "after": memory_after,
                    "peak": memory_peak,
                    "delta": memory_after - memory_before
                },
                cpu_usage=cpu_usage,
                timestamp=datetime.now().isoformat(),
                function_name=func.__name__
            )
            
            # Structured logging
            if log_execution:
                log_data = execution_result.model_dump()
                
                if status == "success":
                    if log_level.upper() == "DEBUG":
                        logger.debug("Function executed successfully", **log_data)
                    else:
                        logger.info("Function executed successfully", **log_data)
                else:
                    logger.error("Function execution failed", **log_data)
            
            # Return format based on configuration
            if return_raw_result and status == "success":
                return result
            else:
                return execution_result.model_dump()
                
        return wrapper
    return decorator

