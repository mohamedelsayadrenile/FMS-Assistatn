import logging
from time import perf_counter
from typing import Any

import httpx
from crewai.tools import tool

from src.core.config import settings
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


def create_get_all_farms_tool(context: ChatContext) -> Any:
    @tool("get_all_farms")
    def get_all_farms() -> dict[str, Any]:
        """List all the user's sites in the FMS, each with a number, id, name, location, and type."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"JWT {context.jwt}",
        }
        url = settings.get_sites_url

        logger.info(
            "get_all_farms tool started sites listing API call",
            extra={
                "request_id": context.request_id,
                "conversation_id": context.conversation_id,
                "company_id": context.company_id,
                "url": url,
                "method": "GET",
            },
        )
        start_time = perf_counter()

        try:
            response = httpx.get(
                url,
                headers=headers,
                timeout=settings.api_timeout_seconds,
            )
        except httpx.HTTPError as exc:
            latency_ms = round((perf_counter() - start_time) * 1000, 2)
            logger.exception(
                "get_all_farms sites listing API request failed",
                extra={
                    "request_id": context.request_id,
                    "conversation_id": context.conversation_id,
                    "company_id": context.company_id,
                    "latency_ms": latency_ms,
                    "url": url,
                    "method": "GET",
                },
            )
            return {
                "success": False,
                "message": "Failed to list sites.",
                "error": str(exc),
            }

        try:
            response_data = response.json()
        except ValueError:
            response_data = {"raw_response": response.text}

        latency_ms = round((perf_counter() - start_time) * 1000, 2)

        if response.is_success:
            sites = response_data if isinstance(response_data, list) else []
            numbered_sites = [
                {
                    "number": index + 1,
                    "id": site.get("id"),
                    "name": site.get("name"),
                    "location": site.get("location"),
                    "type": site.get("type"),
                }
                for index, site in enumerate(sites)
            ]
            logger.info(
                "get_all_farms sites listing API completed",
                extra={
                    "request_id": context.request_id,
                    "conversation_id": context.conversation_id,
                    "company_id": context.company_id,
                    "status_code": response.status_code,
                    "latency_ms": latency_ms,
                    "site_count": len(numbered_sites),
                    "url": url,
                    "method": "GET",
                    "response_body": response_data,
                },
            )
            return {
                "success": True,
                "sites": numbered_sites,
                "message": f"Found {len(numbered_sites)} site(s).",
            }

        logger.warning(
            "get_all_farms sites listing API returned failure",
            extra={
                "request_id": context.request_id,
                "conversation_id": context.conversation_id,
                "company_id": context.company_id,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "url": url,
                "method": "GET",
                "response_body": response_data,
            },
        )
        return {
            "success": False,
            "status_code": response.status_code,
            "message": "Failed to list sites.",
            "details": response_data,
        }

    return get_all_farms


def create_create_crop_tool(context: ChatContext) -> Any:
    @tool("create_crop")
    def create_crop(
        site_id: str,
        farm_name: str,
        farm_type: str,
        initial_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Create a new crop/farm under an existing site in the FMS.

        farm_type must be one of: "traditional_land", "greenhouse", or "trees".
        initial_data depends on farm_type:
        - For "traditional_land" or "greenhouse":
            {"crop_type": "<str>", "sowing_date": "<ISO date>",
             "area": {"value": "<str>", "unit": "<str>"}}
        - For "trees":
            {"tree_species": "<str>", "planting_date": "<ISO date>",
             "number_of_trees": <int or str>, "area": {"value": "<str>", "unit": "<str>"}}
        """
        if farm_type not in ("traditional_land", "greenhouse", "trees"):
            message = (
                f"Invalid farm_type '{farm_type}'. "
                "Allowed values: traditional_land, greenhouse, trees."
            )
            logger.warning(
                "create_crop tool rejected invalid farm_type",
                extra={
                    "request_id": context.request_id,
                    "conversation_id": context.conversation_id,
                    "company_id": context.company_id,
                    "site_id": site_id,
                    "farm_name": farm_name,
                    "farm_type": farm_type,
                },
            )
            return {"success": False, "message": message}

        payload = {
            "farm_name": farm_name,
            "farmType": farm_type,
            "location": "",
            "initialData": initial_data,
            "initialNumber": "null",
            "farmAge": "null",
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"JWT {context.jwt}",
        }
        url = settings.create_farm_url_template.format(siteId=site_id)

        logger.info(
            "create_crop tool started farm creation API call",
            extra={
                "request_id": context.request_id,
                "conversation_id": context.conversation_id,
                "company_id": context.company_id,
                "site_id": site_id,
                "farm_name": farm_name,
                "farm_type": farm_type,
                "url": url,
                "method": "POST",
                "request_payload": payload,
            },
        )
        start_time = perf_counter()

        try:
            response = httpx.post(
                url,
                json=payload,
                headers=headers,
                timeout=settings.api_timeout_seconds,
            )
        except httpx.HTTPError as exc:
            latency_ms = round((perf_counter() - start_time) * 1000, 2)
            logger.exception(
                "create_crop farm creation API request failed",
                extra={
                    "request_id": context.request_id,
                    "conversation_id": context.conversation_id,
                    "company_id": context.company_id,
                    "site_id": site_id,
                    "latency_ms": latency_ms,
                    "url": url,
                    "method": "POST",
                    "request_payload": payload,
                },
            )
            return {
                "success": False,
                "message": "Failed to create crop/farm.",
                "error": str(exc),
            }

        try:
            response_data = response.json()
        except ValueError:
            response_data = {"raw_response": response.text}

        latency_ms = round((perf_counter() - start_time) * 1000, 2)

        if response.is_success:
            logger.info(
                "create_crop farm creation API completed",
                extra={
                    "request_id": context.request_id,
                    "conversation_id": context.conversation_id,
                    "company_id": context.company_id,
                    "site_id": site_id,
                    "status_code": response.status_code,
                    "latency_ms": latency_ms,
                    "farm_id": response_data.get("farm", {}).get("id")
                    if isinstance(response_data, dict)
                    else None,
                    "url": url,
                    "method": "POST",
                    "request_payload": payload,
                    "response_body": response_data,
                },
            )
            return {
                "success": True,
                "message": "Farm created successfully.",
                "farm": response_data,
            }

        logger.warning(
            "create_crop farm creation API returned failure",
            extra={
                "request_id": context.request_id,
                "conversation_id": context.conversation_id,
                "company_id": context.company_id,
                "site_id": site_id,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "url": url,
                "method": "POST",
                "request_payload": payload,
                "response_body": response_data,
            },
        )
        return {
            "success": False,
            "status_code": response.status_code,
            "message": "Failed to create crop/farm.",
            "details": response_data,
        }

    return create_crop
