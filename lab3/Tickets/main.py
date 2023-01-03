from flask import request, Response
import flask
from database import Data_Base

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.app = flask.Flask(__name__)

        self.app.add_url_rule("/manage/health", view_func = self.get_say_ok)
        self.app.add_url_rule("/api/v1/tickets", view_func = self.get_tickets)
        self.app.add_url_rule("/api/v1/tickets/<ticketUid>", view_func = self.get_tickets_by_id)
        self.app.add_url_rule("/api/v1/tickets/<ticketUid>", view_func = self.delete_tickets_by_id, methods = ['DELETE'])
        self.app.add_url_rule("/api/v1/rollback_ticket/<ticketUid>", view_func = self.rollback_ticket, methods = ['DELETE'])
        self.app.add_url_rule("/api/v1/ticket", view_func = self.create_new_ticket, methods = ['POST'])

    def run_server(self):
        return self.app.run(host = self.host, port = self.port)
    def get_say_ok(self):
        return "OK"
        
    def get_tickets(self):
        client = request.headers.get("X-User-Name")
        new_db = Data_Base()
        tickets = new_db.get_tickets(client)
        if tickets:
            return tickets
        return Response(status = 404)

    def get_tickets_by_id(self, ticketUid):
        client = request.headers.get("X-User-Name")
        new_db = Data_Base()
        ticket = new_db.get_ticket(client, ticketUid)
        if ticket:
            return ticket
        return Response(status = 404)

    def delete_tickets_by_id(self, ticketUid):
        client = request.headers.get("X-User-Name")
        new_db = Data_Base()
        check = new_db.delete_ticket(client, ticketUid)
        if check:
            return Response(status = 204)
        return Response(status = 404)

    def create_new_ticket(self):
        client = request.headers.get("X-User-Name")
        flight_number = request.headers.get("flight_number")
        price = int(request.headers.get("price"))
        new_db = Data_Base()
        ticket_uid = new_db.create_new_ticket(client, flight_number, price)
        if ticket_uid:
            return {'uid': ticket_uid}
        return Response(status = 404)

    def rollback_ticket(self, ticketUid):
        client = request.headers.get("X-User-Name")
        new_db = Data_Base()
        check = new_db.rollback_ticket(client, ticketUid)
        if check:
            return Response(status = 204)
        return Response(status = 404)




if __name__ == "__main__":

    server_host = "0.0.0.0"
    server_port = 8070

    server = Server(server_host, server_port)
    server.run_server()
