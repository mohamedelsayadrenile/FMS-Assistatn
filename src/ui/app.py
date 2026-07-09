from __future__ import annotations

from uuid import uuid4

import httpx
import streamlit as st


CHAT_ENDPOINT = "/chat"
REQUEST_TIMEOUT_SECONDS = 120
WELCOME_MESSAGE = (
    "Welcome to the FMS Assistant. Fill in the details in the sidebar "
    "(Backend URL, JWT, ConversationID, companyId, managerIds), then start chatting below."
)


def parse_manager_ids(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def is_setup_complete(backend_url: str, jwt: str, conversation_id: str, company_id: str, manager_ids: list[str]) -> bool:
    return bool(backend_url and jwt and conversation_id and company_id and len(manager_ids) >= 1)


def backend_url_without_trailing_slash(url: str) -> str:
    return url.rstrip("/")


def send_message(backend_url: str, payload: dict, request_id: str) -> tuple[bool, str]:
    try:
        response = httpx.post(
            f"{backend_url}{CHAT_ENDPOINT}",
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as exc:
        return False, f"Request failed: {exc}"

    if response.is_success:
        try:
            return True, response.json().get("response", "")
        except ValueError:
            return False, f"Non-JSON response: {response.text}"
    return False, f"Backend returned status {response.status_code}: {response.text}"


def main() -> None:
    st.set_page_config(page_title="FMS Assistant", page_icon="🌾", layout="centered")
    st.title("FMS Assistant 🌾")

    if "conversation_id" not in st.session_state:
        st.session_state["conversation_id"] = str(uuid4())

    with st.sidebar:
        st.header("Connection Setup")
        backend_url = st.text_input("Backend URL", value="http://localhost:8000", help="Base URL of the FMS FastAPI server.")
        jwt = st.text_input("JWT", type="password")
        conversation_id = st.text_input("ConversationID", value=st.session_state["conversation_id"])
        company_id = st.text_input("companyId")
        manager_ids_raw = st.text_input("managerIds", help="Comma-separated list of manager IDs.")
        if st.button("New conversation", use_container_width=True):
            st.session_state["conversation_id"] = str(uuid4())
            st.session_state["messages"] = [{"role": "assistant", "content": WELCOME_MESSAGE}]
            st.rerun()

    backend_url = backend_url_without_trailing_slash(backend_url)
    manager_ids = parse_manager_ids(manager_ids_raw)

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": WELCOME_MESSAGE}]

    if not is_setup_complete(backend_url, jwt, conversation_id, company_id, manager_ids):
        st.warning("Please complete all fields in the sidebar to start chatting.")

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    chat_disabled = not is_setup_complete(backend_url, jwt, conversation_id, company_id, manager_ids)
    user_input = st.chat_input("Type a message...", disabled=chat_disabled)

    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        payload = {
            "message": user_input,
            "ConversationID": conversation_id,
            "JWT": jwt,
            "companyId": company_id,
            "managerIds": manager_ids,
        }
        request_id = str(uuid4())
        ok, result = send_message(backend_url, payload, request_id)

        if ok:
            st.session_state["messages"].append({"role": "assistant", "content": result})
            with st.chat_message("assistant"):
                st.markdown(result)
        else:
            st.error(result)


if __name__ == "__main__":
    main()