class AppError(Exception):
    code = "APPLICATION_ERROR"
    status_code = 400
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class NotFoundError(AppError):
    code, status_code = "NOT_FOUND", 404
class InvalidReviewToken(AppError):
    code, status_code = "INVALID_REVIEW_TOKEN", 404
class ReviewExpired(AppError):
    code, status_code = "REVIEW_EXPIRED", 410
class ReviewProcessed(AppError):
    code, status_code = "REVIEW_ALREADY_PROCESSED", 409

