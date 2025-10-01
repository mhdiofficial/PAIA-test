import os
from typing import Any

import httpx
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

st.set_page_config(page_title="LlamaIndex Chatbot", page_icon="🤖")
st.title("🤖 LlamaIndex Chatbot Tester")

with st.sidebar:
    st.header("Configuration")
    user_id = st.text_input("User ID", value="demo-user")
    provider = st.selectbox("Provider", options=["default", "openai", "gemini"], index=0)
    api_key = st.text_input("API Key", value="", type="password")
    submit_on_enter = st.checkbox("Send on Enter", value=True)

chat_container = st.container()
user_message = st.text_input("Message", value="Hello there!", key="message_input")

if st.button("Send") or (submit_on_enter and user_message and st.session_state.get("enter_pressed")):
    payload: dict[str, Any] = {"user_id": user_id, "message": user_message}
    if provider != "default":
        payload["provider"] = provider

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

    with st.spinner("Contacting chatbot..."):
        try:
            response = httpx.post(f"{API_BASE_URL}/chat", json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - UI feedback only
            st.error(f"Request failed: {exc}")
        else:
            data = response.json()
            chat_container.markdown(f"**Assistant ({data['provider']}):** {data['reply']}")
            st.session_state.setdefault("history", []).append((user_message, data["reply"]))
            if data.get("history"):
                st.subheader("Conversation History")
                for item in data["history"]:
                    st.markdown(f"- **{item['role']}**: {item['content']}")

if submit_on_enter:
    st.session_state["enter_pressed"] = user_message.endswith("\n")
