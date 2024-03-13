from fastapi import Request
from sqlalchemy.orm import Session
from datetime import datetime
from models import Log


class DatabaseMiddleware:
    def __init__(self, session: Session):
        self.session = session

    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        log_data = {
            "timestamp": datetime.utcnow(),
            "request_form": str(request.url),
            "status_code": str(response.status_code),
            "level": "INFO",
        }
        if 300 < response.status_code < 400:
            log_data["redirect_to"] = str(response.headers["location"])
            log_data["message"] = "Redirect successful"
        elif response.status_code >= 400:
            log_data["level"] = "ERROR"
            log_data["message"] = "Redirect failed"

        log_entry = Log(**log_data)
        self.session.add(log_entry)
        self.session.commit()

        return response
