import happybase
import time

class HBaseManager:

    config = {
        'BATCH_SIZE':1000
    }

    def __init__(self, host='localhost', namespace='crawler', table_name='html'):
        """ Connect to HBase server.
        This will use the host, namespace, table name, and batch size as defined in
        the global variables above.
        """
        self.conn = happybase.Connection(host = host,
            table_prefix = namespace,
            table_prefix_separator = ":")
        self.conn.open()
        self.table = self.conn.table(table_name)
        self.batch = self.table.batch(batch_size = self.config['BATCH_SIZE'])

    def append_page_content(self, url, family, col, content):
        """ Insert a row into HBase.
        Write the row to the batch. When the batch size is reached, rows will be
        sent to the database.
        Rows have the following schema:
            [ id, keyword, subcategory, type, township, city, zip, council_district,
              opened, closed, status, origin, location ]
        """
        self.table.put(url, { '%s:%s' % (family,col) : content } )

    def append_page_content(self, url, batchdata):
        """ Insert a row into HBase.
        Write the row to the batch. When the batch size is reached, rows will be
        sent to the database.
        Rows have the following schema:
            [ id, keyword, subcategory, type, township, city, zip, council_district,
              opened, closed, status, origin, location ]
        """
        self.table.put(url, batchdata )

    def close(self):
        self.conn.close()