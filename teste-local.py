from unittest.mock import patch
import os
import socket
from streamlit.testing.v1 import AppTest
import streamlit, chatlas, dotenv

original_connect = socket.socket.connect
def local_only(sock, address):
    if isinstance(address, tuple) and address[0] in ("127.0.0.1", "::1", "localhost"):
        return original_connect(sock, address)
    raise AssertionError("Conexao externa bloqueada neste teste")

def blocked_client(*args, **kwargs):
    raise AssertionError("Cliente NVIDIA nao deve ser construido sem chave")

with patch.dict(os.environ, {"NVIDIA_API_KEY": "", "PYTHON_DOTENV_DISABLED": "1"}), patch.object(socket.socket, "connect", local_only), patch.object(chatlas, "ChatOpenAICompletions", blocked_client):
    app = AppTest.from_file("app.py").run(timeout=30)
    assert not app.exception, app.exception
    assert app.title[0].value == "ChatAI"
    assert len(app.error) == 1
    assert "NVIDIA_API_KEY" in app.error[0].value
    assert len(app.chat_input) == 0
print("PASS: importacoes, titulo, bloqueio sem chave; cliente NVIDIA nao construido; conexoes externas bloqueadas")
