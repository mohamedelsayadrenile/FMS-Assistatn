from typing import Any

import httpx
from crewai.tools import tool

from src.config import settings
from src.schemas import ChatContext


def create_create_crop_tool(context: ChatContext) -> Any:
    @tool("create_crop")
    def create_crop(name: str) -> dict[str, Any]:
        """Create a crop in the FMS. Currently creates the required site as the first crop-creation step."""
        payload = {
            "name": name,
            "companyId": context.company_id,
            "type": settings.default_site_type,
            "location": settings.default_site_location,
            "timezone": settings.default_timezone,
            "managerIds": context.manager_ids,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"JWT {context.jwt}",
        }

        try:
            response = httpx.post(
                settings.create_site_url,
                json=payload,
                headers=headers,
                timeout=settings.create_site_timeout_seconds,
            )
        except httpx.HTTPError as exc:
            return {
                "success": False,
                "message": "Failed to create site while creating crop.",
                "error": str(exc),
            }

        try:
            response_data = response.json()
        except ValueError:
            response_data = {"raw_response": response.text}

        if response.is_success:
            return {
                "success": True,
                "site_id": response_data.get("id"),
                "message": "Site created successfully as the first crop creation step.",
                "site": response_data,
            }

        return {
            "success": False,
            "status_code": response.status_code,
            "message": "Failed to create site while creating crop.",
            "details": response_data,
        }

    return create_crop
