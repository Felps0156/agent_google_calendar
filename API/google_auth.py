import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDS_PATH = "cliente_secret.json" 
TOKEN_PATH = "token.json"


def get_calendar_service():
   """
   Autentica com a API do Google Calendar e retorna o objeto 'service'.
   Lida com o fluxo OAuth2, criando/atualizando token.json.
   """
   creds = None
   
   if os.path.exists(TOKEN_PATH):
       try:
           creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
       except Exception as e:
           print(f"Erro ao carregar token.json: {e}. Re-autenticando...")
           creds = None
           
   if not creds or not creds.valid:
       if creds and creds.expired and creds.refresh_token:
           try:
               creds.refresh(Request())
           except Exception as e:
               print(f"Erro ao atualizar token: {e}")
               print("Token revogado ou inválido. Por favor, autorize novamente.")
               if os.path.exists(TOKEN_PATH):
                   os.remove(TOKEN_PATH) 
               creds = None
       
       if not creds:
           if not os.path.exists(CREDS_PATH):
               raise FileNotFoundError(
                   f"Arquivo de credenciais não encontrado: {CREDS_PATH}. "
                   "Faça o download do JSON no Google Cloud Console e renomeie-o."
               )
           flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
           creds = flow.run_local_server(port=0)
           
       with open(TOKEN_PATH, "w") as token:
           token.write(creds.to_json())

   try:
       service = build("calendar", "v3", credentials=creds)
       print("Serviço do Google Calendar criado com sucesso!")
       return service
   except HttpError as error:
       print(f"Ocorreu um erro ao construir o serviço: {error}")
       return None
   except Exception as e:
       print(f"Um erro inesperado ocorreu: {e}")
       return None

# def create_service(client_secret_file, api_name, api_version, scopes):
#     """
#     Cria o serviço da API do Google, lidando com a autenticação.
#     """
#     creds = None

#     if os.path.exists(TOKEN_PATH):
#         try:
#             creds = Credentials.from_authorized_user_file(TOKEN_PATH, scopes)
#         except ValueError as e:
#             print(f"Erro ao carregar token.json: {e}")
#             print("Tentando re-autenticar...")
#             creds = None 

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             try:
#                 creds.refresh(Request())
#             except Exception as e:
#                 print(f"Erro ao atualizar o token expirado: {e}")
#                 creds = None 
        
#         if not creds or not creds.valid:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 client_secret_file, scopes
#             )
#             creds = flow.run_local_server(port=0)
        
#         with open(TOKEN_PATH, 'w') as token:
#             token.write(creds.to_json())

#     try:
#         service = build(api_name, api_version, credentials=creds)
#         print(f'Serviço "{api_name}" (versão "{api_version}") criado com sucesso.')
#         return service
#     except HttpError as error:
#         print(f'Ocorreu um erro ao construir o serviço: {error}')
#         return None
#     except Exception as e:
#         print(f'Ocorreu um erro inesperado: {e}')
#         return None

# if __name__ == "__main__":
#     service = create_service()
    
#     if service:
#         try:
#             now = datetime.datetime.utcnow().isoformat() + "Z"  
#             print("\nBuscando os próximos 5 eventos...")
            
#             events_result = (
#                 service.events()
#                 .list(
#                     calendarId="primary",
#                     timeMin=now,
#                     maxResults=5,
#                     singleEvents=True,
#                     orderBy="startTime",
#                 )
#                 .execute()
#             )
#             events = events_result.get("items", [])

#             if not events:
#                 print("Nenhum evento encontrado nos próximos dias.")
#             else:
#                 print("Próximos eventos:")
#                 for event in events:
#                     start = event["start"].get("dateTime", event["start"].get("date"))
#                     print(f"- {start} | {event['summary']}")
        
    