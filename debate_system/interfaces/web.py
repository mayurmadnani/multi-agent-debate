"""Streamlit web UI for the debate system."""
from __future__ import annotations

import streamlit as st

# Use absolute imports so the app works when launched via ``streamlit run``
# from the repository root, where relative imports would otherwise fail.
from debate_system.core import build_orchestrator, ConfigManager
from debate_system.utils.logger import setup_logging


def _init_state() -> None:
    if "orchestrator" not in st.session_state:
        config_manager = ConfigManager()
        setup_logging(config_manager.get_logging_config())
        st.session_state.config_manager = config_manager
        st.session_state.orchestrator = build_orchestrator(config_manager=config_manager)
        st.session_state.memory = st.session_state.orchestrator.memory


def _format_transcript(result: dict) -> str:
    lines = [f"Question: {result.get('question','')}", ""]
    for entry in result.get("history", []):
        speaker = entry.get("speaker", "Agent")
        content = entry.get("content", "")
        lines.append(f"[{speaker}] {content}")
    if result.get("summary"):
        lines.append("")
        lines.append(f"Summary: {result['summary']}")
    return "\n".join(lines)


def main() -> None:
    st.set_page_config(page_title="Philosophical Debate", page_icon="🏛️", layout="wide")
    _init_state()

    st.title("🏛️ Multi-Agent Philosophical Debate")

    with st.sidebar:
        st.header("Settings")
        rounds = st.slider("Debate rounds", 1, 5, 2, help="Number of debate rounds between agents")
        enable_summary = st.checkbox("Enable summary", value=True)
        if st.button("Clear memory"):
            st.session_state.memory.clear()
            st.success("Memory cleared")

    question = st.text_input("Enter your philosophical question", placeholder="What is the meaning of life?")

    if st.button("Start Debate", type="primary"):
        if not question:
            st.warning("Please enter a question")
        else:
            with st.spinner("Debating..."):
                result = st.session_state.orchestrator.run_debate(
                    question=question,
                    rounds=rounds,
                    enable_summary=enable_summary,
                )

            if result.get("error"):
                st.error(f"Error: {result['error']}")
            else:
                st.subheader("Debate")
                for entry in result.get("history", []):
                    speaker = entry.get("speaker", "Agent")
                    if speaker.lower() == "user":
                        avatar = "🧑"
                    elif speaker.lower() == "socrates":
                        avatar = "🤔"
                    if str(speaker).lower() == "plato":
                        avatar = "📚"
                    elif str(speaker).lower() == "aristotle":
                        avatar = "⚡"
                    elif str(speaker).lower() == "summary":
                        avatar = "📝"
                    with st.chat_message(name=speaker, avatar=avatar):
                        st.markdown(entry.get("content", ""))

                transcript = _format_transcript(result)
                st.download_button(
                    label="Download transcript",
                    data=transcript,
                    file_name="debate_transcript.txt",
                    mime="text/plain",
                )


if __name__ == "__main__":  # pragma: no cover
    main()
