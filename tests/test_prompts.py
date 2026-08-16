"""Guards the rule that the assistant never shows internals to a farm owner.

Internal identifiers and enum values are legitimate inside a قاموس line — that is how the
agent learns which Arabic word maps to which value — but nowhere else in the instructions.
"""

import re

import pytest

from src import agents


ARABIC = re.compile(r"[؀-ۿ]")

# Values sent to the API that the user must never be shown on their own.
INTERNAL_VALUES = [
    "greenhouse",
    "traditional_land",
    "trees",
    "string",
    "number",
    "image",
    "checkbox",
    "select",
]

# Field and payload names the previous prompts taught the model to say out loud.
BANNED = [
    "farm_type",
    "input_type",
    "site_id",
    "initial_data",
    "initialData",
    "initialNumber",
    "farmAge",
    "Allowed values",
    '{"crop_type"',
]


@pytest.fixture(scope="module")
def backstories(context) -> dict[str, str]:
    return {
        "intent": agents.create_intent_agent().backstory,
        "site": agents.create_site_agent(context).backstory,
        "farm": agents.create_farm_agent(context).backstory,
        "task": agents.create_task_agent(context).backstory,
    }


def test_every_agent_carries_the_privacy_rules(backstories):
    for name, backstory in backstories.items():
        assert agents.PRIVACY_RULES in backstory, name


@pytest.mark.parametrize("banned", BANNED)
def test_field_names_never_appear_in_the_instructions(backstories, banned):
    for name, backstory in backstories.items():
        assert banned not in backstory, f"{banned!r} leaked into the {name} agent"


@pytest.mark.parametrize("value", INTERNAL_VALUES)
def test_internal_values_only_appear_next_to_their_arabic_label(backstories, value):
    pattern = re.compile(rf"\b{re.escape(value)}\b")
    for name, backstory in backstories.items():
        for line in backstory.splitlines():
            if pattern.search(line):
                assert ARABIC.search(line), (
                    f"{value!r} appears in the {name} agent without an Arabic label: {line!r}"
                )


def test_the_choices_are_offered_in_arabic(backstories):
    for label in ("صوبة", "أرض مكشوفة", "أشجار"):
        assert label in backstories["farm"]
        assert label in backstories["task"]
    for label in ("إجابة مكتوبة", "رقم", "صورة", "علامة صح أو غلط", "اختيار من قائمة"):
        assert label in backstories["task"]


def test_agents_are_told_not_to_re_ask_for_known_details(backstories):
    for name, backstory in backstories.items():
        assert "never ask for it twice" in backstory.lower(), name


def test_date_handling_is_only_given_to_the_agent_that_collects_dates(backstories):
    assert "DATE:" in backstories["farm"]
    for name in ("intent", "site", "task"):
        assert "DATE:" not in backstories[name], name


def test_the_crop_payload_shape_lives_in_the_tool_description_not_the_prompt(context):
    create_crop = agents.create_create_crop_tool(context)

    assert "initial_data" in create_crop.description
    assert "initial_data" not in agents.create_farm_agent(context).backstory
