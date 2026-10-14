# Chatbot NVIDIA com Streamlit e Chatlas

> Relatório da atividade prática da disciplina **Produtos de GenAI**.

## Informações do projeto


| Item                      | Informação                    |
| ------------------------- | ----------------------------- |
| Link público da aplicação | [http://163.176.92.64/](http://163.176.92.64/) |
| Repositório GitHub        | [marcocanedo2001/ChatAI](https://github.com/marcocanedo2001/ChatAI) |
| IP público da VM          | `163.176.92.64`               |
| Sistema operacional       | `Ubuntu 26.04 LTS`            |
| Arquitetura               | `ARM64`                       |
| Processadores virtuais    | `4 vCPUs`                     |
| Memória total reportada   | aproximadamente `15,6 GiB` (`15948 MiB`) |
| Diretório da aplicação    | `/home/ubuntu/apps/chatai-academico` |
| Serviço da aplicação      | `chatai.service`              |

## Introdução

Modelos de linguagem podem ser incorporados a produtos digitais por meio de APIs, permitindo criar experiências conversacionais sem manter toda a infraestrutura de inferência localmente. Nesta atividade, foi construído um chatbot web que integra uma interface em Streamlit a um modelo disponibilizado pela NVIDIA por meio do Chatlas.

O projeto demonstra, de forma simples e reproduzível, o fluxo completo entre a mensagem enviada pelo usuário, a chamada ao endpoint de inferência e a apresentação progressiva da resposta.

## Objetivo da atividade

O objetivo desta atividade foi desenvolver um produto mínimo de IA generativa preparado para execução local e implantação. A proposta consistiu em construir uma experiência conversacional simples, compatível com os requisitos do exercício e baseada em uma arquitetura leve e reproduzível.

Mais especificamente, a aplicação foi construída para:

- receber mensagens em uma interface web;
- preservar o contexto da conversa durante a sessão;
- consumir a API NVIDIA NIM por meio do Chatlas em uma interface compatível com OpenAI;
- exibir as respostas do modelo em streaming;
- manter credenciais e parâmetros de configuração fora do código-fonte.

## Visão geral da solução

A aplicação utiliza o Streamlit para construir a interface de chat. Os turnos da conversa são armazenados em `st.session_state`, e o histórico completo da sessão é reconstruído a cada rerun para preservar o contexto da conversa.

O Chatlas funciona como camada conversacional e é configurado com a URL base da NVIDIA. Na execução local, o `python-dotenv` carrega as configurações do arquivo `.env`. Na VM, o serviço `systemd` carrega esse arquivo por meio de `EnvironmentFile`. A resposta é recebida em partes e exibida à medida que os tokens chegam.

Fluxo simplificado:

1. o usuário digita uma mensagem;
2. a aplicação carrega os turnos anteriores da sessão;
3. o Chatlas envia o histórico ao endpoint NVIDIA NIM;
4. a resposta é exibida progressivamente;
5. os turnos atualizados são salvos de volta em `st.session_state`.

## Infraestrutura

O projeto foi pensado para execução local e implantação em uma máquina virtual da Oracle Cloud Infrastructure (OCI). A solução exige poucos componentes:

- Python 3.10 ou superior;
- aplicação Streamlit;
- acesso à internet para consultar a API da NVIDIA;
- chave válida da NVIDIA API;
- Nginx como proxy reverso na VM, recebendo as conexões HTTP na porta TCP `80`;
- Streamlit escutando apenas em `127.0.0.1:8501`, acessível pelo Nginx.

A inferência não ocorre na VM. A máquina hospeda apenas a interface e o cliente da API, enquanto o processamento do modelo é realizado pela infraestrutura da NVIDIA.

Na publicação atual, somente a porta `80` precisa ser exposta para acesso à aplicação. A porta `8501` permanece interna; o acesso administrativo por SSH deve ser restrito às origens autorizadas. A URL pública utiliza HTTP, e a configuração de HTTPS está entre as melhorias futuras.

## Modelo escolhido

O modelo configurado para esta entrega é `nvidia/nemotron-3.5-lightning-30b-a3b`, consumido pelo endpoint `https://integrate.api.nvidia.com/v1`. A aplicação envia as mensagens para esse serviço externo e apresenta as respostas na interface, sem executar o modelo na Oracle Cloud.

O nome do modelo é configurável pela variável `NVIDIA_MODEL`, o que permite testar outro modelo compatível sem alterar o código.

## Desenvolvimento

### Arquitetura da aplicação

A aplicação foi desenvolvida como um chatbot web em Streamlit, com uma arquitetura simples baseada em interface, estado de sessão e consumo de API externa. A interface usa `st.chat_message` para apresentar os turnos da conversa e `st.chat_input` para receber novas mensagens. O histórico fica armazenado em `st.session_state`, o que preserva o contexto enquanto a sessão do navegador permanece ativa. Para a comunicação com o modelo, a aplicação cria um cliente `ChatOpenAICompletions` apontando para o endpoint compatível com OpenAI da NVIDIA e exibe as respostas em streaming diretamente na interface.

### Bibliotecas utilizadas

As principais bibliotecas utilizadas no projeto são:

- `streamlit`, responsável pela interface web interativa;
- `chatlas`, utilizado como camada de integração com a API da NVIDIA e gerenciamento da conversa;
- `python-dotenv`, empregado para carregar variáveis de ambiente a partir do arquivo `.env`.

### Estratégia de gerenciamento de credenciais

As credenciais e parâmetros de configuração são mantidos fora do código-fonte por meio de variáveis de ambiente. A aplicação lê as variáveis `NVIDIA_API_KEY`, `NVIDIA_MODEL` e `NVIDIA_BASE_URL`, permitindo alterar credenciais, modelo e endpoint sem modificar a implementação. O arquivo `.env` não é versionado, enquanto o repositório mantém apenas o `.env.example` com a chave vazia e os valores padrão de modelo e endpoint. Em caso de falha de configuração ou de comunicação com a API, a interface apresenta mensagens de erro amigáveis sem expor informações sensíveis.

Na VM, o arquivo `.env` deve pertencer ao usuário `ubuntu` e ter permissão `600`. O serviço carrega as variáveis desse arquivo e define `PYTHON_DOTENV_DISABLED=1` apenas para sua execução, evitando um segundo carregamento pelo `python-dotenv`.

## Implantação

### Processo de publicação na Oracle Cloud

A publicação da aplicação foi realizada em uma máquina virtual Linux na Oracle Cloud Infrastructure (OCI). Após a criação da instância, foram instalados Python, `venv`, `pip` e as dependências do projeto. Em seguida, o repositório foi copiado para a VM, o ambiente virtual foi configurado e as variáveis de ambiente necessárias foram definidas no arquivo `.env`.

O projeto está instalado em `/home/ubuntu/apps/chatai-academico`. O Streamlit escuta no endereço `127.0.0.1`, na porta `8501`, e o Nginx encaminha as requisições recebidas na porta `80` para a aplicação. Assim, o endereço público é `http://163.176.92.64/`, sem a necessidade de informar uma porta no navegador.

Para manter a aplicação em execução após logout ou reinicialização, a VM utiliza o serviço `systemd` `chatai.service`, ativo e habilitado para iniciar com o sistema. Os arquivos reproduzíveis dessa configuração ficam em `deploy/chatai.service` e `deploy/chatai.nginx.conf`.

### Principais desafios encontrados

Os principais desafios estiveram relacionados à operação da aplicação em ambiente real. Foi importante manter o identificador do modelo e o endpoint alinhados à configuração desejada, além de garantir o carregamento correto das credenciais por meio do arquivo `.env`. No serviço da VM, o `EnvironmentFile` concentra essa configuração e evita manter valores duplicados na definição do serviço.

Outro desafio relevante foi assegurar a disponibilidade contínua da interface após a publicação. Como o Streamlit é executado como um processo de aplicação, foi necessário configurar a inicialização automática do serviço na VM e o encaminhamento de requisições pelo Nginx. Em uma implantação pública mais robusta, ainda devem ser considerados HTTPS, controle de acesso, monitoramento e limites de consumo da API.

## Validação da entrega

Em **14 de outubro de 2026**, foram realizadas as seguintes verificações:

- **Serviços e acesso público:** `chatai.service` e Nginx estavam ativos e habilitados para iniciar com o sistema. A página pública retornou HTTP `200`, e o endpoint de saúde do Streamlit respondeu `ok`. No navegador, a interface ChatAI abriu com o campo de mensagem habilitado.
- **Configuração:** as variáveis carregadas pelo processo corresponderam aos valores do `.env`. O arquivo pertencia ao usuário `ubuntu`, com permissão `600`. As requisições públicas a `/.env` e `/.git/config` retornaram HTTP `404`.
- **Testes sem API externa:** os cenários de ausência de chave, histórico de conversa e tratamento de erros passaram no Windows e na VM Oracle. Nos dois ambientes, também passaram os cenários de modelo e URL vazios ou preenchidos apenas com espaços, confirmando o uso dos valores padrão.
- **Inferência real:** às **16h57, no horário de Brasília**, um teste com `AppTest` executado na VM enviou o prompt `Responda apenas com a palavra OK.` à NVIDIA e recebeu `OK`. Esse teste usou limite de 64 tokens, timeout de 45 segundos e nenhuma tentativa adicional; esses limites foram aplicados somente ao teste.

A inferência foi validada pelo teste automatizado na VM. A verificação no navegador público confirmou a abertura da interface, sem envio de uma pergunta pela página durante essa etapa.

## Discussão

A compatibilidade do NVIDIA NIM com o Chatlas reduz o acoplamento da aplicação ao provedor. A integração exige apenas a troca da URL base, da credencial e do identificador do modelo.

O histórico em memória é suficiente para a proposta acadêmica, mas possui limitações: ele não sobrevive ao encerramento da sessão, cresce a cada turno e pode elevar o número de tokens enviados. Em um produto real, seria importante limitar o contexto, resumir mensagens antigas ou usar armazenamento persistente.

## Lições aprendidas

- Uma interface compatível com OpenAI via Chatlas facilita a experimentação entre provedores.
- Variáveis de ambiente ajudam a separar configuração, código e segredos.
- O streaming melhora a percepção de velocidade da aplicação.
- O histórico enviado ao modelo é o que mantém o contexto da conversa.
- Uma aplicação de GenAI envolve também segurança, operação e controle de custos.

## Melhorias futuras

- adicionar um botão para limpar a conversa;
- permitir a escolha do modelo pela interface;
- controlar temperatura e quantidade máxima de tokens;
- limitar ou resumir históricos longos;
- persistir conversas em um banco de dados;
- adicionar autenticação, observabilidade e ampliar a cobertura de testes;
- configurar HTTPS no Nginx;
- empacotar a aplicação com Docker.

## Instruções de instalação e execução local

### 1. Preparar o ambiente

```bash
git clone https://github.com/marcocanedo2001/ChatAI.git
cd ChatAI

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

No Windows PowerShell, crie e ative o ambiente com os comandos abaixo e, em seguida, instale as dependências:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configurar as variáveis

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

No Windows PowerShell, use `Copy-Item .env.example .env`.

Edite `.env` e preencha `NVIDIA_API_KEY` com sua chave:

```dotenv
NVIDIA_API_KEY=
NVIDIA_MODEL=nvidia/nemotron-3.5-lightning-30b-a3b
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
```

Nunca publique o arquivo `.env` ou uma chave real no GitHub.

### 3. Iniciar a aplicação

No Linux ou macOS, com o script do projeto:

```bash
bash scripts/run.sh
```

Ou diretamente com o Streamlit:

```bash
streamlit run app.py
```

Acesse `http://localhost:8501` no navegador.

### 4. Executar os testes locais

Com o ambiente virtual ativo, execute:

```bash
python teste-local.py
python teste-visual.py
```

Os testes usam o `AppTest` do Streamlit e bloqueiam conexões externas. O primeiro verifica o comportamento sem chave configurada. O segundo usa respostas simuladas para verificar a interface, o histórico entre reruns, o tratamento de falhas e a configuração de modelo e URL. Essa verificação inclui valores vazios ou compostos apenas por espaços, que devem usar os padrões da aplicação, e valores personalizados com espaços nas extremidades. Esses testes não consomem a API da NVIDIA e não comprovam a disponibilidade da inferência em produção.

## Instruções resumidas de deploy em VM Oracle Cloud

As instruções abaixo usam o usuário `ubuntu`, o diretório `/home/ubuntu/apps/chatai-academico` e o serviço `chatai.service`, correspondentes à publicação deste projeto.

1. Na lista de segurança ou no Network Security Group da VCN, autorize a entrada TCP na porta `80` para acesso HTTP à aplicação. Restrinja o SSH às origens administrativas e mantenha a porta `8501` sem exposição pública.
2. Acesse a VM por SSH e instale os componentes necessários. Em uma imagem Ubuntu:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip nginx
```

3. Em uma instalação nova, clone o repositório e instale as dependências:

```bash
mkdir -p /home/ubuntu/apps
git clone https://github.com/marcocanedo2001/ChatAI.git /home/ubuntu/apps/chatai-academico
cd /home/ubuntu/apps/chatai-academico
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

4. Crie o `.env` na VM a partir do exemplo, preencha a chave e restrinja suas permissões. Se o arquivo já existir, atualize-o sem sobrescrever a configuração com o exemplo:

```bash
cp .env.example .env
nano .env
chmod 600 .env
```

Também é possível transferir o `.env` local por SSH/SCP para esse diretório. A transferência de credenciais deve ocorrer pelo SSH, e o arquivo não deve ser incluído no GitHub.

5. Se o firewall do sistema estiver ativo, permita o tráfego HTTP e preserve a regra de acesso SSH. No Ubuntu com UFW:

```bash
sudo ufw allow 80/tcp
```

6. Instale a configuração do serviço e inicie a aplicação:

```bash
sudo install -m 644 deploy/chatai.service /etc/systemd/system/chatai.service
sudo systemctl daemon-reload
sudo systemctl enable --now chatai.service
sudo systemctl restart chatai.service
sudo systemctl status chatai.service --no-pager
```

7. Instale o proxy reverso do Nginx. Em uma VM dedicada ao projeto, desative o site padrão para que a configuração da aplicação receba as requisições:

```bash
sudo install -m 644 deploy/chatai.nginx.conf /etc/nginx/sites-available/chatai
sudo ln -sfn /etc/nginx/sites-available/chatai /etc/nginx/sites-enabled/chatai
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
```

8. Verifique os serviços e a resposta HTTP:

```bash
curl --fail http://127.0.0.1:8501/_stcore/health
curl --fail --head http://127.0.0.1/
sudo journalctl -u chatai.service -n 50 --no-pager
```

Acesse `http://163.176.92.64/` no navegador e envie uma mensagem para validar a integração completa com a NVIDIA. A resposta HTTP e o estado do serviço confirmam a disponibilidade da interface; a geração de uma resposta depende também de uma chave válida, do acesso ao modelo e da disponibilidade da API.

Ao alterar o `.env`, reinicie `chatai.service` para que o `systemd` carregue os novos valores. Ao atualizar o código, reinstale as dependências se necessário e reinicie o mesmo serviço.
