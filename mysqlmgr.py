import mysql.connector
import hashlib
from mysql.connector import errorcode


class MysqlMgr:

    DB_NAME = 'wx'

    SERVER_IP = 'localhost'

    TABLES = {}
    # create new table, using sql
    TABLES['wxbiz'] = (
        "CREATE TABLE `wxbiz` ("
        "  `index` int(11) NOT NULL AUTO_INCREMENT," # index of queue
        "  `biz` varchar(32) NOT NULL UNIQUE,"
        "  `name` varchar(32) NOT NULL DEFAULT '',"
        "  PRIMARY KEY (`index`)"
        ") ENGINE=InnoDB")

    TABLES['urls'] = (
        "CREATE TABLE `urls` ("
        "  `index` int(11) NOT NULL AUTO_INCREMENT," # index of queue
        "  `url` varchar(128) NOT NULL UNIQUE,"
        "  `md5` varchar(16) NOT NULL,"
        "  `biz` varchar(32) NOT NULL,"
        "  `status` varchar(11) NOT NULL DEFAULT 'new'," # could be new, downloading and finish
        "  `queue_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,"
        "  `done_time` timestamp NOT NULL DEFAULT 0 ON UPDATE CURRENT_TIMESTAMP,"
        "  PRIMARY KEY (`index`),"
        "  UNIQUE KEY `md5` (`md5`)"
        ") ENGINE=InnoDB")


    def __init__(self, max_num_thread):
        # connect mysql server
        try:
            cnx = mysql.connector.connect(host=self.SERVER_IP, user='root', password='amei')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print('Create Error ' + err.msg)
            exit(1)

        cursor = cnx.cursor()

        # use database, create it if not exist
        try:
            cnx.database = self.DB_NAME
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                # create database and table
                self.create_database(cursor)
                cnx.database = self.DB_NAME
                self.create_tables(cursor)
            else:
                print(err)
                exit(1)
        finally:
            cursor.close()
            cnx.close()

        dbconfig = {
            "database": self.DB_NAME,
            "user":     "root",
            "password": "amei",
            "host":     self.SERVER_IP,
        }
        self.cnxpool = mysql.connector.connect(pool_name="mypool",
                                                          pool_size=max_num_thread,
                                                          **dbconfig)


    # create databse
    def create_database(self, cursor):
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.DB_NAME))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)

    def create_tables(self, cursor):
        for name, ddl in self.TABLES.items():
            try:
                cursor.execute(ddl)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print('create tables error ALREADY EXISTS')
                else:
                    print('create tables error ' + err.msg)
            else:
                print('Tables created')


    def enqueue_biz(self, biz, name):
        con = mysql.connector.connect(pool_name="mypool")
        cursor = con.cursor()
        try:
            add_url = ("INSERT INTO wxbiz (biz, name) VALUES (%s, %s)")
            data_url = ( biz, name)
            cursor.execute(add_url, data_url)
            # commit this transaction, please refer to "mysql transaction" for more info
            con.commit()
        except mysql.connector.Error as err:
            # print 'enqueueUrl() ' + err.msg
            return
        finally:
            cursor.close()
            con.close()

    def all_biz(self):
        con = mysql.connector.connect(pool_name="mypool")
        cursor = con.cursor()
        try:
            query = ("SELECT biz FROM wxbiz")
            cursor.execute(query)
            if cursor.rowcount is 0:
                return None
            rows = cursor.fetchall()
            return rows
        except mysql.connector.Error as err:
            # print 'enqueueUrl() ' + err.msg
            return None
        finally:
            cursor.close()
            con.close()

    # put an url into queue
    def enqueue_url(self, url, biz):
        con = mysql.connector.connect(pool_name="mypool")
        cursor = con.cursor()
        try:
            add_url = ("INSERT INTO urls (url, md5, biz) VALUES (%s, %s, %s)")
            data_url = (url, hashlib.md5(url).hexdigest(), biz)
            cursor.execute(add_url, data_url)
            # commit this transaction, please refer to "mysql transaction" for more info
            con.commit()
        except mysql.connector.Error as err:
            # print 'enqueueUrl() ' + err.msg
            return
        finally:
            cursor.close()
            con.close()


    # get an url from queue
    def dequeue_url(self, biz):
        con = mysql.connector.connect(pool_name="mypool")
        cursor = con.cursor(dictionary=True)
        try:
            # use select * for update to lock the rows for read
            query = ("SELECT `index`, `url`, `biz` FROM urls WHERE status='new' AND biz='" + biz + "' ORDER BY `index` ASC LIMIT 1 FOR UPDATE")
            cursor.execute(query)
            if cursor.rowcount is 0:
                return None
            row = cursor.fetchone()
            update_query = ("UPDATE urls SET `status`='downloading' WHERE `index`=%d") % (row['index'])
            cursor.execute(update_query)
            con.commit()
            return row
        except mysql.connector.Error as err:
            # print 'dequeueUrl() ' + err.msg
            return None
        finally:
            cursor.close()
            con.close()

    def finish_url(self, index):
        con = mysql.connector.connect(pool_name="mypool")
        cursor = con.cursor()
        try:
            # we don't need to update done_time using time.strftime('%Y-%m-%d %H:%M:%S') as it's auto updated
            update_query = ("UPDATE urls SET `status`='done' WHERE `index`=%d") % (index)
            cursor.execute(update_query)
            con.commit()
        except mysql.connector.Error as err:
            # print 'finishUrl() ' + err.msg
            return
        finally:
            cursor.close()
            con.close()
