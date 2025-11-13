import os

from dotenv import load_dotenv

load_dotenv()

SMITHERY_API_KEY = os.getenv('SMITHERY_API_KEY')

MCP_SERVERS_CONFIG = {
    'Google Calendar' : {
        'url': f'https://server.smithery.ai/@goldk3y/google-calendar-mcp/mcp?api_key={SMITHERY_API_KEY}',
        'transport': 'streamable_http',
    },
}


#MCP_SERVERS_CONFIG = {
#    'mcpServers': {
#        'google-calendar-mcp': {
#            'transport': 'stdio', 
#            'command': 'cmd',
#            'args': [
#                "/c",
#                "npx",
#                "-y",
#                "@smithery/cli@latest",
#                "run",
#                "@goldk3y/google-calendar-mcp",
#                "--key",
#                "{CLIENTE_SECRET_KEY}", 
#                "--profile",
#                "ok-armadillo-RdhQje"
#            ]
#        }
#    } 
#}