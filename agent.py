import asyncio

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

import sqlite3
#from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.messages import HumanMessage

from langchain_mcp_adapters.client import MultiServerMCPClient
from tools.calendar_tools import list_upcoming_events, create_calendar_event, search_calendar_events, update_calendar_event, delete_calendar_event
#from tools.calendar_tools import criar_calendario_tool, listar_calendarios_tool, listar_eventos_calendario_tool, criar_evento_programado_tool,excluir_evento_tool,atualizar_evento_tool

from API.mcp_servers import MCP_SERVERS_CONFIG

async def main():
    model = ChatGoogleGenerativeAI(
        model='gemini-2.5-flash',
    )

    #mcp_client = MultiServerMCPClient(MCP_SERVERS_CONFIG)
    #tools = await mcp_client.get_tools()

    #conexao = sqlite3.connect("db.sqlite", check_same_thread=False)
    #memory = AsyncSqliteSaver.from_conn_string("db.sqlite")
    memory = MemorySaver()

    prompt = """
    Você é um agente organizador de serviços no Google Calendar, seja gentil, educado e atenda o cliente da forma que for pedida
    Você tem acesso a ferramentas para interagir com o calendário do usuário.
    Use suas ferramentas para responder o usuário.
    """

    tools = [
        list_upcoming_events,
        create_calendar_event,
        search_calendar_events,
        update_calendar_event,
        delete_calendar_event
        ]

    #tools = [
    #    criar_calendario_tool,
    #    listar_calendarios_tool,
    #    listar_eventos_calendario_tool,
    #    criar_evento_programado_tool,
    #    excluir_evento_tool,
    #    atualizar_evento_tool,
    #]
    
    agent_executor = create_agent(
        model=model,
        tools=tools,
        system_prompt=prompt,
        checkpointer=memory,
    )
    
    config = {'configurable': {'thread_id': '1'}}

    print("Agente de Calendário pronto. (Na primeira execução, o navegador abrirá para autenticação do Google).")
    
    while True:   
        input_text = input('Digite: ')
        if input_text.lower() == 'sair':
            break
            
        # Correção 1: Usar HumanMessage
        input_message = HumanMessage(content=input_text)
        
        try:
            print("---")
            # Correção 2: Usar 'astream_events' (como antes)
            async for event in agent_executor.astream_events(
                {'messages': [input_message]}, config, stream_mode='values', version="v1"
            ):
                kind = event["event"]
                
                # Correção 3: O bloco para lidar com a saída do Gemini 2.5
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    content = chunk.content
                    
                    if content:
                        # Se for string (modelos antigos)
                        if isinstance(content, str):
                            print(content, end="", flush=True)
                        # Se for lista (Gemini 2.5 Pro)
                        elif isinstance(content, list):
                            for part in content:
                                if isinstance(part, dict) and part.get("type") == "text":
                                    print(part.get("text", ""), end="", flush=True)
                
                # (Opcional) Manter os logs de ferramentas
                elif kind == "on_tool_call":
                    tool_call = event["data"]
                    print(f"\n[Chamando ferramenta: {tool_call['name']} com args {tool_call['args']}]", flush=True)
                elif kind == "on_tool_end":
                    tool_output = event['data']['output']
                    print(f"\n[Resultado da ferramenta: {str(tool_output)[:200]}...]", flush=True)

            print("\n---\n")

        except Exception as e:
            print(f"Ocorreu um erro no stream do agente: {e}")

if __name__ == "__main__":
    asyncio.run(main())