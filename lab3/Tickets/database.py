import psycopg2
import uuid


class Data_Base:
    def __init__(self):
        self.connection = False
        self.create_tables()

    def connect(self):
        self.connection = psycopg2.connect(dbname = "postgres",
                                           user = "program",
                                           password = "test",
                                           host = "postgres")


    def create_tables(self):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        try:
            sql_request = '''CREATE TABLE ticket
                             (
                                 id            SERIAL PRIMARY KEY,
                                 ticket_uid    uuid UNIQUE NOT NULL,
                                 username      VARCHAR(80) NOT NULL,
                                 flight_number VARCHAR(20) NOT NULL,
                                 price         INT         NOT NULL,
                                 status        VARCHAR(20) NOT NULL
                                     CHECK (status IN ('PAID', 'CANCELED'))
                             );'''

            cursor.execute(sql_request)
            self.connection.commit()
        except:
            self.connection.rollback()
        cursor.close()
        self.connection.close()
        self.connection = False

    def get_tickets(self, client):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        response = False
        try:
            cursor.execute("select ticket_uid, flight_number, status from ticket where username = %s;", (client,))
            tickets = cursor.fetchall()
            response = []

            for ticket in tickets:
                items = dict()
                items["ticketUid"] = ticket[0]
                items["flightNumber"] = ticket[1]
                items["status"] = ticket[2]
                response.append(items)            
        except:
            self.connection.rollback()
        cursor.close()
        self.connection.close()
        self.connection = False
        return response

    def get_ticket(self, client, ticketUid):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        response = False
        try:
            cursor.execute("select ticket_uid, flight_number, status from ticket where username = %s and ticket_uid = %s;", (client, ticketUid))
            ticket = cursor.fetchall()[0]
            if ticket[0]:
                response = dict()
                response["ticketUid"] = ticket[0]
                response["flightNumber"] = ticket[1]
                response["status"] = ticket[2]    
        except:
            self.connection.rollback()
        cursor.close()
        self.connection.close()
        self.connection = False
        return response

    def delete_ticket(self, client, ticketUid):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        check = False
        try:
            cursor.execute("update ticket set status = 'CANCELED' where username = %s and ticket_uid = %s;", (client, ticketUid))
            self.connection.commit()
            check = True
        except:
            self.connection.rollback()
        cursor.close()
        self.connection.close()
        self.connection = False
        return check

    def create_new_ticket(self, client, flight_number, price):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        ticket_uid = False
        try:
            ticket_uid = str(uuid.uuid4())
            cursor.execute("insert into ticket (ticket_uid, username, flight_number, price, status) values (%s, %s, %s, %s, %s)",
                               (ticket_uid, client, flight_number, price, 'PAID'))
            self.connection.commit()
        except:
            self.connection.rollback()
        cursor.close()
        self.connection.close()
        self.connection = False
        return ticket_uid

    def drop_tables(self):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute("drop table ticket;")
        self.connection.commit()
        cursor.close()
        self.connection.close()
        self.connection = False

    def get_tables_data(self):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute("select * from ticket;")
        tickets = cursor.fetchall()
        print('\n', tickets, '\n')
        cursor.close()
        self.connection.close()
        self.connection = False

'''
new_tab = Data_Base()
new_tab.get_tables_data()
new_tab.drop_tables()
'''







