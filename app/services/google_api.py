from aiogoogle import Aiogoogle

from app.core import constants
from app.core.config import settings

SPREADSHEET_BODY = {
    'properties': {'title': '',
                   'locale': constants.LOCALE},
    'sheets': [{
        'properties': {
            'sheetType': constants.SHEET_TYPE,
            'sheetId': constants.SHEET_ID,
            'title': constants.SHEET_TITLE,
            'gridProperties': {
                'rowCount': constants.ROW_COUNT,
                'columnCount': constants.COLUMN_COUNT
            }
        }
    }]
}


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    SPREADSHEET_BODY['properties']['title'] = f'Отчет на {constants.DATETIME}'

    service = await wrapper_services.discover(
        'sheets', constants.SHEETS_VERSION
    )
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=SPREADSHEET_BODY)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover(
        'drive', constants.DRIVE_VERSION
    )
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        projects: list,
        wrapper_services: Aiogoogle
) -> None:
    service = await wrapper_services.discover(
        'sheets', constants.SHEETS_VERSION
    )
    table_values = [
        ['Отчет от', constants.DATETIME],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    for project in projects:
        new_row = [*project]
        table_values.append(new_row)

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='A1:E30',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
