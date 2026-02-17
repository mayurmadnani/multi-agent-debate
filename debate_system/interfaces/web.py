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


def _get_avatar(speaker: str) -> str:
    speaker_l = str(speaker).lower()
    if speaker_l == "user":
        return "🧑"
    elif speaker_l == "socrates":
        return "assets/socrates.png"
    elif speaker_l == "plato":
        return "assets/plato.png"
    elif speaker_l == "aristotle":
        return "assets/aristotle.png"
    elif speaker_l == "summary":
        return "📝"
    else:
        return "🤖"


def main() -> None:
    st.set_page_config(page_title="Philosophical Debate", page_icon="🏛️", layout="wide")
    _init_state()

    st.title("🏛️ Multi-Agent Philosophical Debate")

    with st.sidebar:
        st.header("Settings")
        rounds = st.slider("Debate rounds", 1, 5, 2, help="Number of debate rounds between agents")
        enable_summary = st.checkbox("Enable summary", value=True)
        if st.button("Clear memory", use_container_width=True):
            st.session_state.memory.clear()
            st.success("Memory cleared")

        st.divider()
        st.header("The Philosophers")
        cols = st.columns(3)
        with cols[0]:
            st.image("assets/socrates.png", caption="Socrates")
        with cols[1]:
            st.image("assets/plato.png", caption="Plato")
        with cols[2]:
            st.image("assets/aristotle.png", caption="Aristotle")

    st.markdown("""
    Welcome to the Great Debate. Pose your question and watch the masters engage in philosophical discourse.
    """)

    question = st.text_input("Enter your philosophical question", placeholder="What is the nature of virtue?")

    if st.button("Start Debate", type="primary", use_container_width=True):
        if not question:
            st.warning("Please enter a question")
        else:
            st.subheader("Debate")
            debate_placeholder = st.container()
            
            with st.spinner("The philosophers are deliberating..."):
                stream = st.session_state.orchestrator.stream_debate(
                    question=question,
                    rounds=rounds,
                    enable_summary=enable_summary,
                )
                
                rendered_count = 0
                result = {}
                for result in stream:
                    history = result.get("history", [])
                    for i in range(rendered_count, len(history)):
                        entry = history[i]
                        speaker = str(entry.get("speaker", "Agent"))
                        avatar = _get_avatar(speaker)
                        with debate_placeholder:
                            with st.chat_message(name=speaker, avatar=avatar):
                                content = entry.get("content", "")
                                st.markdown(content.replace("\n", "  \n"))
                    rendered_count = len(history)

            if result.get("error"):
                st.error(f"Error: {result['error']}")
            else:
                transcript = _format_transcript(result)
                st.download_button(
                    label="Download transcript",
                    data=transcript,
                    file_name="debate_transcript.txt",
                    mime="text/plain",
                    use_container_width=True
                )


if __name__ == "__main__":  # pragma: no cover
    main()
