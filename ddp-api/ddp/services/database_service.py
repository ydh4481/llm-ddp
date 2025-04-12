import json
from typing import Tuple

from ddp.utils.mysql_connector import MySQLConnector


def validate_and_check_connection(connection_info_str: str) -> Tuple[bool, str]:
    """
    문자열로 된 JSON connection_info를 파싱하고,
    실제 DB 연결 테스트를 수행합니다.

    Args:
        connection_info_str (str): JSON string 형태의 접속 정보

    Returns:
        Tuple[bool, str]: (성공 여부, 메시지)
    """
    if not connection_info_str:
        return False, "No connection info provided"

    try:
        connection_info = json.loads(connection_info_str)
    except json.JSONDecodeError:
        return False, "Invalid JSON format in connection_info"

    try:
        connected = MySQLConnector.check_connection(connection_info)
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

    if not connected:
        return False, "Failed to connect to the database"

    return True, "Connection successful"
