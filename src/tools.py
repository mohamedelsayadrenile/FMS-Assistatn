import logging
from time import perf_counter
from typing import Any, NamedTuple

import httpx
from crewai.tools import tool

from src.core.config import settings
from src.schemas import ChatContext


logger = logging.getLogger(__name__)

FARM_TYPES = ("traditional_land", "greenhouse", "trees")
INPUT_TYPES = ("string", "number", "image", "checkbox", "select")

# Tool results are read by the agent, never by the user, so they carry the recovery
# instruction with them instead of an error the agent might echo verbatim.
FAILURE_MESSAGE = (
    "The request did not go through. Apologise to the user briefly in Egyptian Arabic and ask "
    "them to try again in a moment. Never show this text, any error detail, or any status code."
)


def rejected_message(what: str) -> str:
    return (
        f"Unrecognised {what}. Ask the user again in Egyptian Arabic, offering the choices by "
        "their Arabic names. Never show this text or any English value."
    )


class ApiResult(NamedTuple):
    ok: bool
    data: Any


async def api_call(
    context: ChatContext,
    tool_name: str,
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
) -> ApiResult:
    """Call an FMS endpoint, log the full exchange, and report only success plus body."""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"JWT {context.jwt}",
    }
    log_context: dict[str, Any] = {
        "request_id": context.request_id,
        "conversation_id": context.conversation_id,
        "company_id": context.company_id,
        "url": url,
        "method": method,
    }
    if payload is not None:
        log_context["request_payload"] = payload

    logger.info(f"{tool_name} API call started", extra=log_context)
    start_time = perf_counter()

    try:
        async with httpx.AsyncClient(timeout=settings.api_timeout_seconds) as client:
            response = await client.request(method, url, json=payload, headers=headers)
    except httpx.HTTPError:
        logger.exception(
            f"{tool_name} API call request failed",
            extra={**log_context, "latency_ms": _latency_ms(start_time)},
        )
        return ApiResult(False, None)

    try:
        response_data = response.json()
    except ValueError:
        response_data = {"raw_response": response.text}

    log_context |= {
        "latency_ms": _latency_ms(start_time),
        "status_code": response.status_code,
        "response_body": response_data,
    }

    if response.is_success:
        logger.info(f"{tool_name} API call completed", extra=log_context)
        return ApiResult(True, response_data)

    logger.warning(f"{tool_name} API call returned failure", extra=log_context)
    return ApiResult(False, response_data)


def _latency_ms(start_time: float) -> float:
    return round((perf_counter() - start_time) * 1000, 2)


def create_create_site_tool(context: ChatContext) -> Any:
    @tool("create_site")
    async def create_site(name: str, location: str) -> dict[str, Any]:
        """Create a site in the FMS."""
        payload = {
            "name": name,
            "companyId": context.company_id,
            "location": location,
            "timezone": settings.default_timezone,
            "managerIds": context.manager_ids,
        }
        result = await api_call(
            context, "create_site", "POST", settings.create_site_url, payload
        )
        if not result.ok:
            return {"success": False, "message": FAILURE_MESSAGE}

        site_id = result.data.get("id") if isinstance(result.data, dict) else None
        return {
            "success": True,
            "site_id": site_id,
            "message": "Site created successfully.",
        }

    return create_site


def create_get_all_farms_tool(context: ChatContext) -> Any:
    @tool("get_all_farms")
    async def get_all_farms() -> dict[str, Any]:
        """List all the user's sites in the FMS, each with a number, id, name, location, and type."""
        result = await api_call(context, "get_all_farms", "GET", settings.get_sites_url)
        if not result.ok:
            return {"success": False, "message": FAILURE_MESSAGE}

        sites = result.data if isinstance(result.data, list) else []
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
        return {
            "success": True,
            "sites": numbered_sites,
            "message": f"Found {len(numbered_sites)} site(s).",
        }

    return get_all_farms


def create_create_crop_tool(context: ChatContext) -> Any:
    @tool("create_crop")
    async def create_crop(
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
        if farm_type not in FARM_TYPES:
            logger.warning(
                "create_crop tool rejected invalid farm_type",
                extra={
                    "request_id": context.request_id,
                    "conversation_id": context.conversation_id,
                    "farm_name": farm_name,
                    "farm_type": farm_type,
                },
            )
            return {"success": False, "message": rejected_message("farm kind")}

        payload = {
            "farm_name": farm_name,
            "farmType": farm_type,
            "location": "",
            "initialData": initial_data,
            "initialNumber": "null",
            "farmAge": "null",
        }
        url = settings.create_farm_url_template.format(siteId=site_id)
        result = await api_call(context, "create_crop", "POST", url, payload)
        if not result.ok:
            return {"success": False, "message": FAILURE_MESSAGE}

        return {
            "success": True,
            "farm_name": farm_name,
            "message": "Farm created successfully.",
        }

    return create_crop


def create_create_task_tool(context: ChatContext) -> Any:
    @tool("create_task")
    async def create_task(
        title: str,
        description: str,
        input_type: str,
        farm_type: str,
        options: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new task-type in the FMS.

        input_type must be one of: "string", "number", "image", "checkbox", or "select".
        farm_type must be one of: "greenhouse", "traditional_land", or "trees".
        options is a list of choice strings and is only required when input_type is
        "select"; it is ignored for all other input types.
        """
        if input_type not in INPUT_TYPES:
            logger.warning(
                "create_task tool rejected invalid input_type",
                extra={
                    "request_id": context.request_id,
                    "conversation_id": context.conversation_id,
                    "title": title,
                    "input_type": input_type,
                },
            )
            return {"success": False, "message": rejected_message("answer kind")}

        if farm_type not in FARM_TYPES:
            logger.warning(
                "create_task tool rejected invalid farm_type",
                extra={
                    "request_id": context.request_id,
                    "conversation_id": context.conversation_id,
                    "title": title,
                    "farm_type": farm_type,
                },
            )
            return {"success": False, "message": rejected_message("farm kind")}

        payload = {
            "title": title,
            "description": description,
            "input_type": input_type,
            "farm_type": farm_type,
            "input_config": {"options": options or [""]},
        }
        result = await api_call(
            context, "create_task", "POST", settings.create_task_url, payload
        )
        if not result.ok:
            return {"success": False, "message": FAILURE_MESSAGE}

        return {"success": True, "title": title, "message": "Task created successfully."}

    return create_task
