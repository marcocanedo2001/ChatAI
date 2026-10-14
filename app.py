import os

from chatlas import Chat, ChatOpenAICompletions, Turn, UserTurn
from dotenv import load_dotenv
import streamlit as st

DEFAULT_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"
DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"

load_dotenv()

st.set_page_config(page_title="ChatAI", page_icon="💬", layout="centered")
st.markdown(
    """<style>
    .stMainBlockContainer {max-width: 860px; padding-top: 2.5rem;}
    h1 {letter-spacing: -0.035em;}
    [data-testid="stChatMessage"] {border-radius: 16px; padding: 1rem;}
    @media (max-width: 600px) {
        .stMainBlockContainer {padding-top: 1.5rem; padding-left: 1rem; padding-right: 1rem;}
    }
    </style>""",
    unsafe_allow_html=True,
)
st.caption("PROJETO ACADÊMICO · INTELIGÊNCIA ARTIFICIAL")
st.title("ChatAI")
st.write("Uma pergunta, uma ideia, uma conversa.")

api_key = (os.getenv("NVIDIA_API_KEY") or "").strip()
model = (os.getenv("NVIDIA_MODEL") or "").strip() or DEFAULT_MODEL
base_url = (os.getenv("NVIDIA_BASE_URL") or "").strip() or DEFAULT_BASE_URL

with st.expander("Sobre este projeto", expanded=False):
    st.markdown("Chatbot da disciplina **Produtos de GenAI**, desenvolvido com Python, Streamlit e Chatlas.")
    st.caption("As respostas são geradas pela NVIDIA. O histórico permanece nesta sessão.")
    st.text(f"Modelo: {model}")

if "turns" not in st.session_state:
    st.session_state.turns = []

if not api_key:
    st.error(
        "A variável NVIDIA_API_KEY não foi configurada. "
        "Crie o arquivo .env a partir de .env.example e informe sua chave."
    )
    st.stop()


def build_chat() -> Chat:
    chat = ChatOpenAICompletions(
        api_key=api_key,
        base_url=base_url,
        model=model,
    )
    if st.session_state.turns:
        chat.set_turns(st.session_state.turns)
    return chat


def render_turn(turn: Turn) -> None:
    if turn.role == "system" or not turn.text:
        return

    with st.chat_message(turn.role):
        st.markdown(turn.text)


chat = build_chat()

for turn in chat.get_turns():
    render_turn(turn)


if prompt := st.chat_input("O que você gostaria de explorar?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    turns_before = list(chat.get_turns())

    with st.chat_message("assistant"):
        try:
            st.write_stream(chat.stream(prompt, content="text"))
        except Exception:
            st.error(
                "Não foi possível obter uma resposta da API da NVIDIA "
                "via Chatlas. Verifique a chave, o modelo, a URL base e "
                "a conexão e tente novamente."
            )
            st.session_state.turns = [*turns_before, UserTurn(prompt)]
        else:
            st.session_state.turns = chat.get_turns()
