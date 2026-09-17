"""Small standard-library HTTP surface for the garage automation twist."""

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

from parking_garage import ParkingGarage, ParkingGarageError, Vehicle


def parse_datetime(value: str | None) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00")) if value else datetime.now()
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


class GarageAPI:
    def __init__(self, garage: ParkingGarage | None = None) -> None:
        self.garage = garage or ParkingGarage()

    def clock(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        now = parse_datetime(payload.get("now"))
        return {"now": now.isoformat(), "closed": self.garage.auto_close_overdue(now)}

    def rate_card(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {"rate_card": self.garage.import_rate_card(payload)}

    def transfer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ticket = self.garage.transfer_session(payload["from_plate"], payload["to_plate"])
        return {
            "ticket_id": ticket.ticket_id,
            "license_plate": ticket.license_plate,
            "spot_id": ticket.spot.spot_id,
            "entry_time": ticket.entry_time.isoformat(),
        }

    def check_in(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ticket = self.garage.check_in(
            Vehicle(payload["license_plate"], payload.get("vehicle_type", "standard")),
            parse_datetime(payload.get("entry_time")),
        )
        return {
            "ticket_id": ticket.ticket_id,
            "license_plate": ticket.license_plate,
            "spot_id": ticket.spot.spot_id,
            "spot_type": ticket.spot.spot_type,
            "entry_time": ticket.entry_time.isoformat(),
        }

    def check_out(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        plate = payload["license_plate"]
        exit_time = parse_datetime(payload.get("exit_time"))
        fee = self.garage.check_out(plate, exit_time)
        return {"license_plate": str(plate).strip().upper(), "fee": fee, "exit_time": exit_time.isoformat()}


def make_handler(api: GarageAPI):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            routes = {
                "/clock": api.clock,
                "/rate-card": api.rate_card,
                "/transfer": api.transfer,
                "/check-in": api.check_in,
                "/check-out": api.check_out,
            }
            route = routes.get(self.path)
            if route is None:
                self._send(404, {"error": "Not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length) or b"{}")
                self._send(200, route(payload))
            except (KeyError, ValueError, TypeError, json.JSONDecodeError, ParkingGarageError) as exc:
                self._send(400, {"error": str(exc)})

        def _send(self, status: int, payload: Dict[str, Any]) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args: Any) -> None:
            return

    return Handler


def serve(host: str = "127.0.0.1", port: int = 8001) -> None:
    api = GarageAPI()
    HTTPServer((host, port), make_handler(api)).serve_forever()


if __name__ == "__main__":
    serve()