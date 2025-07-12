from pydantic import BaseModel
from typing import Optional, List

class RecognizeFaceResponse(BaseModel):
    employee_id: Optional[str]
    employee_name: Optional[str]
    confidence: float
    success: bool
    error: Optional[str]

class RegisterEmployeeResponse(BaseModel):
    success: bool
    message: Optional[str]
    error: Optional[str]

class ListEmployeesResponse(BaseModel):
    employees: List[dict]

class DeleteEmployeeResponse(BaseModel):
    success: bool
    message: Optional[str]
    error: Optional[str]

class MarkAttendanceResponse(BaseModel):
    success: bool
    employee_id: Optional[str]
    employee_name: Optional[str]
    timestamp: Optional[str]
