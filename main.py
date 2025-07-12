from decorator import monitor_function
from pydantic import BaseModel
from datetime import datetime
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(override=True)

VALIDATE_INPUT = os.environ.get("VALIDATE_INPUT", True)
VALIDATE_OUTPUT = os.environ.get("VALIDATE_OUTPUT", True)
LOG_EXECUTION = os.environ.get("LOG_EXECUTION", True)
RETURN_RAW_RESULT = os.environ.get("RAW_RESULT", False)

# Example usage and test models
class UserInput(BaseModel):
    name: str
    age: int
    email: str


class UserOutput(BaseModel):
    id: int
    name: str
    age: int
    email: str
    created_at: str


# Example decorated function
@monitor_function(
    validate_input=VALIDATE_INPUT,
    validate_output=VALIDATE_OUTPUT,
    log_execution=LOG_EXECUTION,
    return_raw_result=RETURN_RAW_RESULT
)
def create_user(user_data: UserInput) -> UserOutput:
    """Example function that creates a user"""
    # Simulate some processing
    time.sleep(0.1)
    
    # Simulate user creation
    return UserOutput(
        id=12345,
        name=user_data.name,
        age=user_data.age,
        email=user_data.email,
        created_at=datetime.now().isoformat()
    )


# Example with error handling
@monitor_function(
    validate_input=VALIDATE_INPUT,
    validate_output=VALIDATE_OUTPUT,
    log_execution=LOG_EXECUTION,
    return_raw_result=RETURN_RAW_RESULT
)
def divide_numbers(a: float, b: float) -> float:
    """Example function that might raise an exception"""
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return a / b


# Example usage
if __name__ == "__main__":
    # Test successful execution
    # print("=== Testing successful execution ===")
    user_input = UserInput(name="John Doe", age=30, email="john@example.com")
    result = create_user(user_input)
    # print(f"Result: {result}")
    
    # print("\n=== Testing error handling ===")
    error_result = divide_numbers(10, 0)
    # print(f"Error Result: {error_result}")
    
    # print("\n=== Testing input validation error ===")
    try:
        # This should fail validation
        invalid_user = {"name": "John", "age": "thirty", "email": "invalid"}
        result = create_user(invalid_user)
        # print(f"Validation Result: {result}")
    except Exception as e:
        print(f"Exception: {e}")