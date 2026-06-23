from fastapi import HTTPException, status

class FileTooLargeException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 20MB limit."
        )

class InvalidFileTypeException(HTTPException):
    def __init__(self, allowed_types: str):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed types are: {allowed_types}"
        )
