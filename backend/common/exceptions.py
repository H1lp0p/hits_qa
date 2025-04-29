from fastapi import status
from fastapi.responses import JSONResponse

class CustomException(Exception):
    message = "Internal error"
    code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def response(self):
        return JSONResponse(
            status_code=self.code,
            content=self.message
        )

class TaskNotFound(CustomException):
    message = "task not found"
    code = status.HTTP_404_NOT_FOUND

class PaginationError(CustomException):
    message = "incorrect pagination data"
    code = status.HTTP_400_BAD_REQUEST