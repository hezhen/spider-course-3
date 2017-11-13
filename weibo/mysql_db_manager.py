import mysql.connector
import hashlib
from mysql.connector import errorcode
from mysql.connector import pooling


class CrawlDatabaseManager:

    DB_NAME = 'weibo_crawl'

    SERVER_IP = 'localhost'

    TABLES = {}
    # create new table, using sql
    TABLES['uids'] = (
        "CREATE TABLE `uids` ("
        "  `index` int(11) NOT NULL AUTO_INCREMENT," # index of queue
        "  `user_id` varchar(32) NOT NULL,"
        "  `status` varchar(11) NOT NULL DEFAULT 'new'," # could be new, downloading and finish
        "  `queue_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,"
        "  `done_time` timestamp NOT NULL DEFAULT 0 ON UPDATE CURRENT_TIMESTAMP,"
        "  PRIMARY KEY (`index`)"
        ") ENGINE=InnoDB")

    TABLES['users'] = (
        "CREATE TABLE `users` ("
        "  `index` int(11) NOT NULL AUTO_INCREMENT," # index of queue
        "  `user_id` varchar(32) NOT NULL,"
        "  `name` varchar(32) NOT NULL,"
        "  `followers_count` int(11) NOT NULL,"
        "  `follow_count` int(32) NOT NULL,"
        "  `description` varchar(64) NOT NULL,"
        "  PRIMARY KEY (`index`)"
        ") ENGINE=InnoDB")

    def __init__(self, max_num_thread):
        # connect mysql server
        try:
            cnx = mysql.connector.connect(host=self.SERVER_IP, user='root', password='amei')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print "Something is wrong with your user name or password"
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print "Database does not exist"
            else:
                print 'Create Error ' + err.msg
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
                print err
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
        self.cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool",
                                                          pool_size=max_num_thread,
                                                          **dbconfig)


    # create databse
    def create_database(self, cursor):
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.DB_NAME))
        except mysql.connector.Error as err:
            print "Failed creating database: {}".format(err)
            exit(1)

    def create_tables(self, cursor):
        for name, ddl in self.TABLES.iteritems():
            try:
                cursor.execute(ddl)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print 'create tables error ALREADY EXISTS'
                else:
                    print 'create tables error ' + err.msg
            else:
                print 'Tables created'


    # insert user into queue
    def enqueue_user(self, user_id, **kwargs):
        con = self.cnxpool.get_connection()
        cursor = con.cursor()
        try:
            add_uid = ("INSERT INTO uids (user_id) VALUES (%s)")
            data_uid = (user_id,)
            cursor.execute(add_uid, data_uid)
            keys = 'user_id'
            values = (user_id,)
            values_stmt = '%s'
            for key in kwargs:
                keys += ', ' + key
                values_stmt += ', %s'
                values += (kwargs[key],)
            add_user_info = ("INSERT INTO users (%s) VALUES ") % (keys)
            add_user_info += '(' + values_stmt + ')'

            cursor.execute(add_user_info, values)
            # commit this transaction, please refer to "mysql transaction" for more info
            con.commit()
        except mysql.connector.Error as err:
            print 'enqueueUrl() ' + err.msg
            return
        finally:
            cursor.close()
            con.close()


    # get an user from queue
    def dequeue_user(self):
        con = self.cnxpool.get_connection()
        cursor = con.cursor(dictionary=True)
        try:
            # use select * for update to lock the rows for read
            query = ("SELECT `index`, `user_id` FROM uids WHERE status='new' ORDER BY `index` ASC LIMIT 1 FOR UPDATE")
            cursor.execute(query)
            if cursor.rowcount is 0:
                return None
            row = cursor.fetchone()
            if row is None:
                return None
            update_query = ("UPDATE uids SET `status`='downloading' WHERE `index`=%d") % (row['index'])
            cursor.execute(update_query)
            con.commit()
            return row
        except mysql.connector.Error as err:
            # print 'dequeueUrl() ' + err.msg
            return None
        finally:
            cursor.close()
            con.close()

    def finish_user(self, index):
        con = self.cnxpool.get_connection()
        cursor = con.cursor()
        try:
            # we don't need to update done_time using time.strftime('%Y-%m-%d %H:%M:%S') as it's auto updated
            update_query = ("UPDATE uids SET `status`='done' WHERE `index`=%d") % (index)
            cursor.execute(update_query)
            con.commit()
        except mysql.connector.Error as err:
            # print 'finishUrl() ' + err.msg
            return
        finally:
            cursor.close()
            con.close()

if __name__ == '__main__':
    dbmanager = CrawlDatabaseManager(10)