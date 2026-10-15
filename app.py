import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Privacy-Preserving LLM Pipeline", layout="wide")
st.title("🔒 Privacy-Preserving LLM Pipeline")

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "redacted_text" not in st.session_state:
    st.session_state.redacted_text = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": ..., "content": ...}
if "file_text" not in st.session_state:
    st.session_state.file_text = None

# ---------------------------------------------------------------------------
# Two-column layout
# ---------------------------------------------------------------------------
left_col, right_col = st.columns(2, gap="large")

# ── Left column: file upload + redaction ────────────────────────────────────
with left_col:
    st.header("📄 Document Redaction")

    uploaded_file = st.file_uploader("Upload a .txt contract file", type=["txt"])

    if uploaded_file is not None:
        raw_text = uploaded_file.read().decode("utf-8")
        st.session_state.file_text = raw_text

        st.subheader("Raw Text")
        st.text_area("", value=raw_text, height=300, disabled=True, key="raw_display")

        if st.button("🚫 Redact PII", use_container_width=True):
            with st.spinner("Redacting…"):
                try:
                    resp = requests.post(
                        f"{API_BASE}/redact",
                        json={"text": raw_text},
                        timeout=30,
                    )
                    resp.raise_for_status()
                    st.session_state.redacted_text = resp.json()["redacted_text"]
                except requests.exceptions.ConnectionError:
                    st.error("Could not reach the API. Is `uvicorn main:app` running?")
                except requests.exceptions.HTTPError as e:
                    st.error(f"API error: {e}")

    if st.session_state.redacted_text:
        st.subheader("Redacted Text")
        st.text_area(
            "",
            value=st.session_state.redacted_text,
            height=300,
            disabled=True,
            key="redacted_display",
        )

# ── Right column: chat interface ─────────────────────────────────────────────
with right_col:
    st.header("💬 Ask the LLM")

    if st.session_state.file_text is None:
        st.info("Upload a file on the left to enable the chat.")
    else:
        # Render existing chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_question = st.chat_input("Ask a question about the document…")

        if user_question:
            # Show user message immediately
            st.session_state.chat_history.append(
                {"role": "user", "content": user_question}
            )
            with st.chat_message("user"):
                st.markdown(user_question)

            # Call /chat endpoint
            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/chat",
                            json={
                                "text": st.session_state.file_text,
                                "prompt": user_question,
                            },
                            timeout=120,
                        )
                        resp.raise_for_status()
                        data = resp.json()
                        answer = data["response"]
                        st.markdown(answer)
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": answer}
                        )
                    except requests.exceptions.ConnectionError:
                        err = "Could not reach the API. Is `uvicorn main:app` running?"
                        st.error(err)
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": err}
                        )
                    except requests.exceptions.HTTPError as e:
                        err = f"API error: {e}"
                        st.error(err)
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": err}
                        )

        # Clear chat button
        if st.session_state.chat_history:
            if st.button("🗑️ Clear chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
