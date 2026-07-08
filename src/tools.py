import logging
from time import perf_counter
from typing import Any

import httpx
from crewai.tools import tool

from src.config import settings
from src.schemas import ChatContext


logger = logging.getLogger(__name__)


def create_create_site_tool(context: ChatContext) -> Any:
    @tool("create_site")
    def create_site(name: str, location: str) -> dict[str, Any]:
        """Create a site in the FMS."""
        payload = {
            "name": name,
            "companyId": context.company_id,
            "location": location,
            "timezone": settings.default_timezone,
            "managerIds": context.manager_ids,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"JWT {context.jwt}",
        }

        logger.info(
            "create_site tool started site creation API call",
            extra={
                "request_id": context.request_id,
                "conversation_id": context.conversation_id,
                "company_id": context.company_id,
                "site_name": name,
                "site_location": location,
                "timezone": settings.default_timezone,
                "manager_count": len(context.manager_ids),
                "url": settings.create_site_url,
                "method": "POST",
                "request_payload": payload,
            },
        )
        start_time = perf_counter()

        try:
            response = httpx.post(
                settings.create_site_url,
                json=payload,
                headers=headers,
                timeout=settings.create_site_timeout_seconds,
            )
        except httpx.HTTPError as exc:
            latency_ms = round((perf_counter() - start_time) * 1000, 2)
            logger.exception(
                "create_site site creation API request failed",
                extra={
                    "request_id": context.request_id,
                    "conversation_id": context.conversation_id,
                    "company_id": context.company_id,
                    "latency_ms": latency_ms,
                    "url": settings.create_site_url,
                    "method": "POST",
                    "request_payload": payload,
                },
            )
            return {
                "success": False,
                "message": "Failed to create site.",
                "error": str(exc),
            }

        try:
            response_data = response.json()
        except ValueError:
            response_data = {"raw_response": response.text}

        latency_ms = round((perf_counter() - start_time) * 1000, 2)

        if response.is_success:
            logger.info(
                "create_site site creation API completed",
                extra={
                    "request_id": context.request_id,
                    "conversation_id": context.conversation_id,
                    "company_id": context.company_id,
                    "status_code": response.status_code,
                    "latency_ms": latency_ms,
                    "site_id": response_data.get("id"),
                    "site_name": response_data.get("name"),
                    "url": settings.create_site_url,
                    "method": "POST",
                    "request_payload": payload,
                    "response_body": response_data,
                },
            )
            return {
                "success": True,
                "site_id": response_data.get("id"),
                "message": "Site created successfully.",
                "site": response_data,
            }

        logger.warning(
            "create_site site creation API returned failure",
            extra={
                "request_id": context.request_id,
                "conversation_id": context.conversation_id,
                "company_id": context.company_id,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "url": settings.create_site_url,
                "method": "POST",
                "request_payload": payload,
                "response_body": response_data,
            },
        )
        return {
            "success": False,
            "status_code": response.status_code,
            "message": "Failed to create site.",
            "details": response_data,
        }

    return create_site
