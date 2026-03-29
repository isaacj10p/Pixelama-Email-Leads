class LeadgenException(Exception):
    """Base exception for the lead generation application."""
    pass

class ScraperException(LeadgenException):
    """General error during scraping operations."""
    pass

class RateLimitException(ScraperException):
    """Raised when Instagram rate limits the scraper ('Try Again Later')."""
    pass

class ProxyException(ScraperException):
    """Raised when there are issues with proxy connectivity or rotation."""
    pass

class SMTPVerificationException(LeadgenException):
    """Raised when an error occurs during SMTP email verification."""
    pass

class ClassifierException(LeadgenException):
    """Raised when an error occurs during profile classification."""
    pass

class JobTimeoutException(LeadgenException):
    """Raised when the scheduled job exceeds its maximum allowed time."""
    pass
