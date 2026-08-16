from typing import Any

import httpx
import pytest

from src import tools


class FakeResponse:
    def __init__(self, status_code: int = 200, json_data: Any = None, text: str = ""):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self) -> Any:
        if self._json_data is None:
            raise ValueError("no json body")
        return self._json_data


class FakeClient:
    def __init__(self, handler, calls: list[dict[str, Any]]):
        self._handler = handler
        self._calls = calls

    async def __aenter__(self) -> "FakeClient":
        return self

    async def __aexit__(self, *_: object) -> bool:
        return False

    async def request(self, method, url, json=None, headers=None):
        self._calls.append({"method": method, "url": url, "json": json, "headers": headers})
        return self._handler(method, url, json)


@pytest.fixture
def http(monkeypatch):
    """Replace the HTTP client with a scripted fake; returns the recorded calls."""

    def install(handler):
        calls: list[dict[str, Any]] = []
        monkeypatch.setattr(
            tools.httpx, "AsyncClient", lambda **_: FakeClient(handler, calls)
        )
        return calls

    return install


async def test_create_site_returns_site_id_and_sends_context(context, http):
    calls = http(lambda *_: FakeResponse(201, {"id": "site-1", "name": "مزارع دينا"}))
    create_site = tools.create_create_site_tool(context).func

    result = await create_site(name="مزارع دينا", location="الاقصر")

    assert result == {
        "success": True,
        "site_id": "site-1",
        "message": "Site created successfully.",
    }
    assert calls[0]["json"] == {
        "name": "مزارع دينا",
        "companyId": "company-1",
        "location": "الاقصر",
        "timezone": "Africa/Cairo",
        "managerIds": ["manager-1"],
    }
    assert calls[0]["headers"]["Authorization"] == "JWT test-jwt"


async def test_network_error_hides_the_exception(context, http):
    def boom(*_):
        raise httpx.ConnectError("failed to resolve fms.test")

    http(boom)
    create_site = tools.create_create_site_tool(context).func

    result = await create_site(name="مزارع دينا", location="الاقصر")

    assert result["success"] is False
    assert result["message"] == tools.FAILURE_MESSAGE
    assert "fms.test" not in str(result)


async def test_api_rejection_does_not_leak_the_response_body(context, http):
    http(lambda *_: FakeResponse(422, {"detail": "companyId must be a valid uuid"}))
    create_site = tools.create_create_site_tool(context).func

    result = await create_site(name="مزارع دينا", location="الاقصر")

    assert result == {"success": False, "message": tools.FAILURE_MESSAGE}
    assert "companyId" not in str(result)
    assert "422" not in str(result)


async def test_non_json_response_is_handled(context, http):
    http(lambda *_: FakeResponse(500, None, text="<html>gateway error</html>"))
    create_site = tools.create_create_site_tool(context).func

    result = await create_site(name="مزارع دينا", location="الاقصر")

    assert result["success"] is False
    assert "gateway" not in str(result)


async def test_get_all_farms_numbers_sites_from_one(context, http):
    http(
        lambda *_: FakeResponse(
            200,
            [
                {"id": "a", "name": "Tanta Farm", "location": "Tanta", "type": "farm"},
                {"id": "b", "name": "مزارع دينا", "location": "الاقصر", "type": "farm"},
            ],
        )
    )
    get_all_farms = tools.create_get_all_farms_tool(context).func

    result = await get_all_farms()

    assert result["success"] is True
    assert [site["number"] for site in result["sites"]] == [1, 2]
    assert result["sites"][1]["name"] == "مزارع دينا"
    assert result["message"] == "Found 2 site(s)."


async def test_create_crop_builds_the_site_specific_url(context, http):
    calls = http(lambda *_: FakeResponse(201, {"farm": {"id": "farm-1"}}))
    create_crop = tools.create_create_crop_tool(context).func

    result = await create_crop(
        site_id="site-1",
        farm_name="قمح الشتوي",
        farm_type="traditional_land",
        initial_data={"crop_type": "قمح", "sowing_date": "2026-03-05"},
    )

    assert result["success"] is True
    assert result["farm_name"] == "قمح الشتوي"
    assert calls[0]["url"] == "https://fms.test/api/sites/site-1/farms"
    assert calls[0]["json"]["farmType"] == "traditional_land"


@pytest.mark.parametrize("farm_type", ["field", "صوبة", "GREENHOUSE"])
async def test_create_crop_rejects_unknown_farm_type_without_calling_the_api(
    context, http, farm_type
):
    calls = http(lambda *_: FakeResponse(201, {}))
    create_crop = tools.create_create_crop_tool(context).func

    result = await create_crop(
        site_id="site-1", farm_name="قمح", farm_type=farm_type, initial_data={}
    )

    assert result["success"] is False
    assert farm_type not in result["message"]
    assert calls == []


async def test_create_task_defaults_options_and_reports_the_title(context, http):
    calls = http(lambda *_: FakeResponse(201, {"data": {"id": "task-1"}}))
    create_task = tools.create_create_task_tool(context).func

    result = await create_task(
        title="ري الأرض",
        description="سجل كمية المياه",
        input_type="number",
        farm_type="traditional_land",
    )

    assert result == {
        "success": True,
        "title": "ري الأرض",
        "message": "Task created successfully.",
    }
    assert calls[0]["json"]["input_config"] == {"options": [""]}


@pytest.mark.parametrize(
    ("input_type", "farm_type"),
    [("text", "traditional_land"), ("number", "orchard")],
)
async def test_create_task_rejects_unknown_values_without_calling_the_api(
    context, http, input_type, farm_type
):
    calls = http(lambda *_: FakeResponse(201, {}))
    create_task = tools.create_create_task_tool(context).func

    result = await create_task(
        title="ري الأرض",
        description="سجل كمية المياه",
        input_type=input_type,
        farm_type=farm_type,
    )

    assert result["success"] is False
    assert calls == []
