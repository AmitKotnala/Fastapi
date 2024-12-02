from typing import Literal
from dataclasses import dataclass


@dataclass
class UserErrors(Exception):
    message: str = "Internal Server Error"
    type: str = "UserErrors"
    log_level: Literal['ERROR', 'CRITICAL', 'INFO', 'WARNING'] = 'ERROR'

    def __str__(self):
        return self.message

@dataclass
class S3Error(UserErrors):
    message: str = 'Error while connecting to S3. Please try again.'
    type: str = 'S3Errors'

@dataclass
class CredentialError(UserErrors):
    message: str = 'Could not validate credentials'
    type: str = 'PermissionDeniedError'
    log_level: Literal['ERROR', 'CRITICAL', 'INFO', 'WARNING'] = 'WARNING'

@dataclass
class InvalidFileError(UserErrors):
    message: str = 'Please upload docx, pptx or xlsx file only.'
    type: str = 'InvalidFileType'
    log_level: Literal['ERROR', 'CRITICAL', 'INFO', 'WARNING'] = 'INFO'

@dataclass
class InvalidDataError(UserErrors):
    message: str = "The given data is invalid please try again with correct data."
    type: str = 'InvalidDataError'
    log_level: Literal['ERROR', 'CRITICAL', 'INFO', 'WARNING'] = 'WARNING'


@dataclass
class PayloadLargeError(UserErrors):
    message: str = "Payload is too large to Process"
    type: str = 'PayloadLargeError'

@dataclass
class PDFErrors(UserErrors):
    message: str = "InternalServerError"

@dataclass
class MicrosoftError(UserErrors):
    message:str = "Unable to parse the file, please reopen and save in Microsoft Office"
    type: str = "MicrosoftError"


@dataclass
class ExternalRequestError(UserErrors):
    message: str = 'Some Error occurred while calling an external API.'
    type: str = 'ExternalRequestError'
    log_level: Literal['ERROR', 'CRITICAL', 'INFO', 'WARNING'] = 'CRITICAL'


@dataclass
class SecureTransferRequestError(ExternalRequestError):
    message: str = 'Some Error occurred while calling an Secure Transfer API.'
    type: str = 'SecureTransferRequestError'
    log_level: Literal['ERROR', 'CRITICAL', 'INFO', 'WARNING'] = 'CRITICAL'

@dataclass
class GDriveError(UserErrors):
    message:str = "Some error occurred while communicating with google drive, please try again."
    type: str = "GDriveError"


@dataclass
class FileConverterError(UserErrors):
    message: str = 'Error in FileConverter'
    type: str = 'FileConverterError'

@dataclass
class SuggestionGenerationError(UserErrors):
    message: str = 'Error occurred while suggestion generation'
    type: str = 'SuggestionGenerationError'
    log_level: Literal['ERROR', 'CRITICAL', 'INFO', 'WARNING'] = 'ERROR'


@dataclass
class WorkspaceError(UserErrors):
	message: str = "Error in api"
	response_code: int = 502
	type: str = 'Workspace Error'
	log_level: Literal['ERROR', 'CRITICAL', 'INFO', 'WARNING'] = 'CRITICAL'