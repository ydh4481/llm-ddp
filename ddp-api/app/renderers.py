from django.utils import timezone
from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # 응답 코드 가져오기
        response = renderer_context.get("response", None)
        status_code = response.status_code if response else 200

        # 오류 메시지 추출 (DRF 기본 에러 포맷 대응)
        message = ""
        if isinstance(data, dict) and "error" in data:
            message = data["error"]
            data = None
        else:
            message = "요청이 성공적으로 처리되었습니다."

        # 커스텀 포맷 구성
        response_data = {
            "status": "success" if 200 <= status_code < 400 else "error",
            "message": message,
            "data": data,
            "code": status_code,
            "timestamp": timezone.now().isoformat() + "Z",
        }

        return super().render(response_data, accepted_media_type, renderer_context)
