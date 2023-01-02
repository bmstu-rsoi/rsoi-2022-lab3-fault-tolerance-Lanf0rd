import psycopg2


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
            sql_request = '''CREATE TABLE privilege
                             (
                                 id       SERIAL PRIMARY KEY,
                                 username VARCHAR(80) NOT NULL UNIQUE,
                                 status   VARCHAR(80) NOT NULL DEFAULT 'BRONZE'
                                     CHECK (status IN ('BRONZE', 'SILVER', 'GOLD')),
                                 balance  INT
                             );'''

            cursor.execute(sql_request)
            cursor.execute("insert into privilege (username, status, balance) values (%s, %s, %s)",
                               ("Test Max", "GOLD", 1500))
            
            sql_request = '''CREATE TABLE privilege_history
                             (
                                 id             SERIAL PRIMARY KEY,
                                 privilege_id   INT REFERENCES privilege (id),
                                 ticket_uid     uuid        NOT NULL,
                                 datetime       TIMESTAMP   NOT NULL,
                                 balance_diff   INT         NOT NULL,
                                 operation_type VARCHAR(20) NOT NULL
                                     CHECK (operation_type IN ('FILL_IN_BALANCE', 'DEBIT_THE_ACCOUNT'))
                             );'''
            cursor.execute(sql_request)
            cursor.execute("insert into privilege_history (privilege_id, ticket_uid, datetime, balance_diff, operation_type) values (%s, %s, %s, %s, %s)",
                               (1, "049161bb-badd-4fa8-9d90-87c9a82b0668", "2021-10-08T19:59:19Z", 1500, "FILL_IN_BALANCE"))
            self.connection.commit()
        except:
            self.connection.rollback()
        cursor.close()
        self.connection.close()
        self.connection = False

    def get_privilege(self, client):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        response = False
        try:
            cursor.execute("select balance, status, id from privilege where username = %s;", (client,))
            client_data = cursor.fetchall()[0]
            response = {"balance": client_data[0], "status": client_data[1], "history": []}
            cursor.execute("select datetime, ticket_uid, balance_diff, operation_type from privilege_history where privilege_id = %s;", (client_data[2],))
            client_bonuses = cursor.fetchall()

            for client_bonus in client_bonuses:
                items = dict()
                items["date"] = client_bonus[0]
                items["ticketUid"] = client_bonus[1]
                items["balanceDiff"] = client_bonus[2]
                items["operationType"] = client_bonus[3]
                response["history"].append(items)            
        except:
            self.connection.rollback()
        cursor.close()
        self.connection.close()
        self.connection = False
        return response

    def rollback_privilege(self, client, ticketUid):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        try:
            cursor.execute("select id, balance from privilege where username = %s;", (client,))
            privilege_data = cursor.fetchall()[0]
            cursor.execute("select datetime, balance_diff, operation_type from privilege_history where privilege_id = %s;", (privilege_data[0],))
            history_data = cursor.fetchall()[0]
            if history_data[2] == 'FILL_IN_BALANCE':
                new_balance = max(privilege_data[1] - history_data[1], 0)
                cursor.execute("update privilege set balance = %s where username = %s;", (new_balance, client))
                cursor.execute("insert into privilege_history (privilege_id, ticket_uid, datetime, balance_diff, operation_type) values (%s, %s, %s, %s, %s)",
                               (privilege_data[0], ticketUid, history_data[0], history_data[1], "DEBIT_THE_ACCOUNT"))
            else:
                new_balance = privilege_data[1] + history_data[1]
                cursor.execute("update privilege set balance = %s where username = %s;", (new_balance, client))
                cursor.execute("insert into privilege_history (privilege_id, ticket_uid, datetime, balance_diff, operation_type) values (%s, %s, %s, %s, %s)",
                               (privilege_data[0], ticketUid, history_data[0], history_data[1], "FILL_IN_BALANCE"))
            self.connection.commit()
        except:
            self.connection.rollback()
        cursor.close()
        self.connection.close()
        self.connection = False
        return

    def buy_by_privilege(self, client, ticket_uid, price, datetime):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        response_privelege = False
        try:
            cursor.execute("select id, balance, status from privilege where username = %s;", (client,))
            privilege_data = cursor.fetchall()[0]
            if price <= privilege_data[1]:
                new_balance = privilege_data[1] - price
                balance_diff = price
            else:
                new_balance = 0
                balance_diff = privilege_data[1]
            cursor.execute("update privilege set balance = %s where username = %s;", (new_balance, client))
            cursor.execute("insert into privilege_history (privilege_id, ticket_uid, datetime, balance_diff, operation_type) values (%s, %s, %s, %s, %s)",
                               (privilege_data[0], ticket_uid, datetime, balance_diff, "DEBIT_THE_ACCOUNT"))
            response_privelege = dict(balance = new_balance, status = privilege_data[2])
            self.connection.commit()
        except:
            self.connection.rollback()
        cursor.close()
        self.connection.close()
        self.connection = False
        return response_privelege

    def add_privilege(self, client, ticket_uid, price, datetime):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        response_privelege = False
        try:
            cursor.execute("select id, balance, status from privilege where username = %s;", (client,))
            privilege_data = cursor.fetchall()[0]
            balance_diff = price*0.1
            new_balance = privilege_data[1] + balance_diff
            cursor.execute("update privilege set balance = %s where username = %s;", (new_balance, client))
            cursor.execute("insert into privilege_history (privilege_id, ticket_uid, datetime, balance_diff, operation_type) values (%s, %s, %s, %s, %s)",
                               (privilege_data[0], ticket_uid, datetime, balance_diff, "FILL_IN_BALANCE"))
            response_privelege = dict(balance = new_balance, status = privilege_data[2])
            self.connection.commit()
        except:
            self.connection.rollback()
        cursor.close()
        self.connection.close()
        self.connection = False
        return response_privelege

    def drop_tables(self):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute("drop table privilege_history;")
        cursor.execute("drop table privilege;")
        self.connection.commit()
        cursor.close()
        self.connection.close()
        self.connection = False

    def get_tables_data(self):
        if not(self.connection):
            self.connect()
        cursor = self.connection.cursor()
        cursor.execute("select * from privilege;")
        airports = cursor.fetchall()
        cursor.execute("select * from privilege_history;")
        flights = cursor.fetchall()
        print('\n', airports, '\n')
        print('\n', flights, '\n')
        cursor.close()
        self.connection.close()
        self.connection = False


'''
new_tab = Data_Base()
new_tab.get_tables_data()
new_tab.drop_tables()
'''
