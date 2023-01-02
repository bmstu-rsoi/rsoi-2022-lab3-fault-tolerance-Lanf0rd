from flask import request, Response
import flask
from database import Data_Base

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.app = flask.Flask(__name__)

        self.app.add_url_rule("/manage/health", view_func = self.get_say_ok)
        self.app.add_url_rule("/api/v1/privilege", view_func = self.get_privilege)
        self.app.add_url_rule("/api/v1/privilege/<ticketUid>", view_func = self.rollback_privilege, methods = ['DELETE'])
        self.app.add_url_rule("/api/v1/buy_by_privilege", view_func = self.buy_by_privilege, methods = ['POST'])
        self.app.add_url_rule("/api/v1/add_privilege", view_func = self.add_privilege, methods = ['POST'])
        
    def run_server(self):
        return self.app.run(host = self.host, port = self.port)
    def get_say_ok(self):
        return "OK"
        
    def get_privilege(self):
        client = request.headers.get("X-User-Name")
        new_db = Data_Base()
        privilege = new_db.get_privilege(client)
        if not(privilege):
            return Response(status = 404)
        return privilege

    def rollback_privilege(self, ticketUid):
        client = request.headers.get("X-User-Name")
        new_db = Data_Base()
        new_db.rollback_privilege(client, ticketUid)
        return Response(status = 204)

    def buy_by_privilege(self):
        client = request.headers.get("X-User-Name")
        ticket_uid = request.headers.get("ticket_uid")
        price = request.headers.get("price")
        datetime = request.headers.get("datetime")
        new_db = Data_Base()
        response_privelege = new_db.buy_by_privilege(client, ticket_uid, price, datetime)
        if response_privelege:
            return response_privelege
        return Response(status = 404)

    def add_privilege(self):
        client = request.headers.get("X-User-Name")
        ticket_uid = request.headers.get("ticket_uid")
        price = int(request.headers.get("price"))
        datetime = request.headers.get("datetime")
        new_db = Data_Base()
        response_privelege = new_db.add_privilege(client, ticket_uid, price, datetime)
        if response_privelege:
            return response_privelege
        return Response(status = 404)



if __name__ == "__main__":

    server_host = "0.0.0.0"
    server_port = 8050

    server = Server(server_host, server_port)
    server.run_server()
