from abc import ABC, abstractmethod

import structlog

logger = structlog.get_logger(__name__)


class EmailService(ABC):
    """
    Abstraction over outbound transactional email. `auth_service` depends on
    this interface, not on a concrete provider — swapping in SES/SendGrid/
    Postmark for production means adding one adapter here, never touching
    `services/auth_service.py`.
    """

    @abstractmethod
    async def send_verification_email(self, to_email: str, verification_url: str) -> None: ...

    @abstractmethod
    async def send_password_reset_email(self, to_email: str, reset_url: str) -> None: ...


class ConsoleEmailService(EmailService):
    """
    Default implementation: writes the email to structured logs instead of
    an SMTP relay. This is intentional, not a stub — the architecture's tech
    stack does not specify a transactional email provider, and logging the
    outbound message (including the actionable link) keeps registration and
    password reset fully functional in local/staging without requiring
    third-party credentials. Swap for an SES/SendGrid adapter in production
    by implementing `EmailService` and changing the binding in
    `services/auth_service.py`'s constructor call.
    """

    async def send_verification_email(self, to_email: str, verification_url: str) -> None:
        logger.info("email.verification_sent", to=to_email, url=verification_url)

    async def send_password_reset_email(self, to_email: str, reset_url: str) -> None:
        logger.info("email.password_reset_sent", to=to_email, url=reset_url)
