import os,socket
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
import chatlas
from chatlas import UserTurn, AssistantTurn
connect=socket.socket.connect
def local_only(sock,address):
    if isinstance(address,tuple) and address[0] in ('127.0.0.1','::1','localhost'):
        return connect(sock,address)
    raise AssertionError('Teste visual bloqueia rede externa')
class MockChat:
    fail=False
    last_config=None
    def __init__(self,**kwargs):
        self.turns=[]
        type(self).last_config={name:kwargs[name] for name in ('model','base_url')}
    def set_turns(self,turns): self.turns=list(turns)
    def get_turns(self): return self.turns
    def stream(self,prompt,**kwargs):
        if self.fail: raise RuntimeError('Falha simulada')
        self.turns.extend([UserTurn(prompt),AssistantTurn('Resposta simulada para teste visual.')])
        yield 'Resposta simulada '
        yield 'para teste visual.'
with patch.dict(os.environ,{'PYTHON_DOTENV_DISABLED':'1','NVIDIA_API_KEY':'mock-sem-valor-real','NVIDIA_MODEL':'modelo-simulado','NVIDIA_BASE_URL':'https://integrate.api.nvidia.com/v1'}),patch.object(chatlas,'ChatOpenAICompletions',MockChat),patch.object(socket.socket,'connect',local_only):
    default_config={
        'model':'nvidia/nemotron-3.5-lightning-30b-a3b',
        'base_url':'https://integrate.api.nvidia.com/v1',
    }
    for empty_model in ('',' \t '):
        for empty_url in ('',' \t '):
            with patch.dict(os.environ,{'NVIDIA_MODEL':empty_model,'NVIDIA_BASE_URL':empty_url}):
                MockChat.last_config=None
                defaults_app=AppTest.from_file('app.py').run(timeout=30)
                assert not defaults_app.exception and not defaults_app.error
                assert MockChat.last_config==default_config, MockChat.last_config
                assert defaults_app.text[0].value=='Modelo: '+default_config['model']
                defaults_app.chat_input[0].set_value('Teste de configuracao vazia.').run(timeout=30)
                assert not defaults_app.exception and not defaults_app.error
                assert len(defaults_app.session_state.turns)==2
    with patch.dict(os.environ,{'NVIDIA_MODEL':'  modelo-personalizado  ','NVIDIA_BASE_URL':'  https://api.example.test/v1  '}):
        MockChat.last_config=None
        custom_app=AppTest.from_file('app.py').run(timeout=30)
        assert not custom_app.exception and not custom_app.error
        assert MockChat.last_config=={
            'model':'modelo-personalizado',
            'base_url':'https://api.example.test/v1',
        }, MockChat.last_config
    app=AppTest.from_file('app.py').run(timeout=30)
    assert not app.exception and app.title[0].value=='ChatAI'
    assert len(app.chat_input)==1 and len(app.chat_message)==0
    assert app.expander[0].label=='Sobre este projeto'
    app.chat_input[0].set_value('Pergunta sintética.').run(timeout=30)
    assert not app.exception and not app.error and len(app.chat_message)==2
    assert len(app.session_state.turns)==2
    app.run(timeout=30)
    assert len(app.chat_message)==2
    app.chat_input[0].set_value('Segunda pergunta sintética.').run(timeout=30)
    assert len(app.chat_message)==4 and len(app.session_state.turns)==4
    MockChat.fail=True
    app.chat_input[0].set_value('Falha simulada.').run(timeout=30)
    assert not app.exception and len(app.error)==1 and len(app.session_state.turns)==5
print('PASS: modelo/URL vazios ou com espacos usam padroes; configuracao personalizada aparada; estado vazio, entrada, resposta simulada, historico entre reruns, segunda mensagem e erro simulado; sem API real')
