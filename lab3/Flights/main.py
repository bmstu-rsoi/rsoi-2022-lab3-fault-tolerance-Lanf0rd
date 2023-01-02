from flask import request, Response
import flask
from database import Data_Base

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.app = flask.Flask(__name__)

        self.app.add_url_rule("/manage/health", view_func = self.get_say_ok)
        self.app.add_url_rule("/api/v1/flights", view_func = self.get_flights)
        self.app.add_url_rule("/api/v1/flight_by_number", view_func = self.get_flight_by_number)

    def run_server(self):
        return self.app.run(host = self.host, port = self.port)
    def get_say_ok(self):
        return "OK"
        
    def get_flights(self):
        param_page = request.args.get("page", default = 0, type = int)
        param_size = request.args.get("size", default = 0, type = int)
        new_db = Data_Base()
        flights = new_db.get_flights(param_page, param_size)
        if not(flights):
            return Response(status = 404)
        return flights

    def get_flight_by_number(self):
        flight_number = request.headers.get("flight_number")
        new_db = Data_Base()
        flight = new_db.get_flight_by_number(flight_number)
        if not(flight):
            return Response(status = 404)
        return flight
        


if __name__ == "__main__":

    server_host = "0.0.0.0"
    server_port = 8060

    server = Server(server_host, server_port)
    server.run_server()
