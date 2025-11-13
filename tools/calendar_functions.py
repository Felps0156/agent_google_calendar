from datetime import datetime
from API.google_auth import get_calendar_service

CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']

service = get_calendar_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


def cria_calendario(
        calendar_name,
        timezone: str = "America/Sao_Paulo"
):
    calendar_name = {
        'summary': calendar_name,
        'timeZone': timezone
    }
    response = service.calendars().insert(body=calendar_name).execute()
    calendar_id = response.get('id')
    return calendar_id

def listar_calendarios(
        max_capacity=200
):
    if isinstance(max_capacity, str):
        max_capacity = int(max_capacity)

    all_calendars = []
    all_calendars_cleaned = []
    next_page_token = None
    capacity_tracker = 0

    while True:
        calendar_list = service.calendarList().list(
            maxResults=min(200, max_capacity - capacity_tracker),
            pageToken=next_page_token
        ).execute()
        calendars = calendar_list.get('items', [])
        all_calendars.extend(calendars)
        capacity_tracker += len(calendars)
        if capacity_tracker >= max_capacity:
            break
        next_page_token = calendar_list.get('nextPageToken')
        if not next_page_token:
            break

    for calendar in all_calendars:
        all_calendars_cleaned.append(
            {
                'id': calendar['id'],
                'name': calendar['summary'],
                'description': calendar.get('description', ''),
                'primary': calendar.get('primary', False),
                'time_zone': calendar.get('timeZone'),
                'etag': calendar.get('etag'),
                'access_role': calendar.get('accessRole')
            })

    return all_calendars_cleaned

def listar_eventos_calendario(
        calendar_id='primary',
        max_capacity=20,
        time_min=None,
        time_max=None,
        show_deleted=False):
    if isinstance(max_capacity, str):
        max_capacity = int(max_capacity)

    all_events = []
    next_page_token = None
    capacity_tracker = 0

    while True:
        events_list = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=min(250, max_capacity - capacity_tracker),
            pageToken=next_page_token,
            showDeleted=show_deleted
        ).execute()

        events = events_list.get('items', [])
        all_events.extend(events)
        capacity_tracker += len(events)
        if capacity_tracker >= max_capacity:
            break
        next_page_token = events_list.get('nextPageToken')
        if not next_page_token:
            break
    # Process and return the events
    processed_events = []
    for event in all_events:
        processed_event = {
            'id': event.get('id'),
            'summary': event.get('summary'),
            'description': event.get('description'),
            'start': event.get('start'),
            'end': event.get('end'),
            'status': event.get('status'),
            'creator': event.get('creator'),
            'organizer': event.get('organizer'),
            'attendees': event.get('attendees'),
            'location': event.get('location'),
            'hangoutLink': event.get('hangoutLink'),
            'conferenceData': event.get('conferenceData'),
            'recurringEventId': event.get('recurringEventId')
        }
        processed_events.append(processed_event)
    return processed_events

def criar_evento_programado(
        start: str,
        end: str,
        calendar_id='primary',
        timezone: str = "America/Sao_Paulo",
        summary: str | None = None,
        description: str | None = None,
        location: str | None = None,
        attendees: list | None = None,
        send_notifications: bool = True,
) -> str:
    if service is None:
        return "Não é possível comunicar com o Serviço de Calendário Google."

    # datetime validation
    try:
        datetime.fromisoformat(start)
    except Exception:
        return "A hora de início do evento não está no formato ISO/RFC3339"

    try:
        datetime.fromisoformat(end)
    except Exception:
        return "A hora de fim do evento não está no formato ISO/RFC3339"

    event = {
        "start": {"dateTime": start, "timeZone": timezone},
        "end": {"dateTime": end, "timeZone": timezone},
    }

    for key, value in zip(
            ["summary", "description", "location"], [summary, description, location]
    ):
        if value is not None:
            event[key] = value

    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]

    try:
        event = service.events().insert(calendarId=calendar_id, body=event,
                                        sendNotifications=send_notifications).execute()
        return f"Evento criado com sucesso com o id {event.get('id')}"
    except Exception as e:
        return f"Falha na execução da ferramenta `criar_evento_programado`. Erro: {e}"

def excluir_evento(
        event_id: str,
        send_notifications: bool = True,
        calendar_id: str = 'primary'
) -> str:
    try:
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendNotifications=send_notifications
        ).execute()
        return f"Evento (ID: {event_id}) excluído com sucesso."

    except Exception as e:
        return f"Erro ao deletar evento do calendário. ID Evento: {event_id} - Mensagem de Erro:\n{str(e)}"

def atualizar_evento(
        event_id: str,
        calendar_id: str = 'primary',
        start: str | None = None,
        end: str | None = None,
        timezone: str | None = None,
        summary: str | None = None,
        description: str | None = None,
        location: str | None = None,
):
    if service is None:
        return "Não é possível comunicar com o Serviço de Calendário Google."

    updates = {}
    updated_parameters = set()

    if start is not None:
        try:
            datetime.fromisoformat(start)
        except Exception:
            return "A hora de início do evento não está no formato ISO/RFC3339"
        updates['start'] = {}
        updates['start']['dateTime'] = start
        updated_parameters.add("start")

    if end is not None:
        try:
            datetime.fromisoformat(end)
        except Exception:
            return "A hora de fim do evento não está no formato ISO/RFC3339"
        updates['end'] = {}
        updates['end']['dateTime'] = end
        updated_parameters.add("end")

    if timezone is not None:
        if "start" not in updates:
            updates["start"] = {}
        updates['start']['timeZone'] = timezone
        updated_parameters.add("start")

        if "end" not in updates:
            updates["end"] = {}
        updates['end']['timeZone'] = timezone
        updated_parameters.add("end")

    for key, value in zip(
            ["summary", "description", "location"], [summary, description, location]
    ):
        if value is not None:
            updates[key] = value
            updated_parameters.add(key)

    updated_parameters = ",".join(updated_parameters)
    try:
        _ = service.events().patch(calendarId=calendar_id, eventId=event_id, body=updates).execute()
        return f"O evento com o id {event_id} foi atualiza com as informações: [{''.join(updated_parameters)}] "
    except Exception as e:
        return f"Falha na execução da atualização. Erro: {e}"