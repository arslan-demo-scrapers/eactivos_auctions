import logging
import re
import time
from datetime import datetime
from html import unescape

from eactivos_auctions.eactivos_auctions.database.db_connection import DatabaseConnection
from eactivos_auctions.eactivos_auctions.database.db_static import table_schemas, table_name_auction, auction_table_cols
from eactivos_auctions.eactivos_auctions.config.env_config import Config


class DBOperations(DatabaseConnection):
    def __init__(self):
        self.open_sql_connection()
        self.reset_database_table([table_name_auction])
        self.make_database_schema()
        self.scraped_auctions = self.get_scraped_auction_ids(table_name_auction, ['URL'])
        a = 0

    def reset_database_table(self, tables):
        for tab in tables:
            self.sql_conn_cursor.execute(f'DROP TABLE IF EXISTS {tab};')
            self.sql_connection.commit()

    def make_database_schema(self):
        self.sql_conn_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")

        for tb_s in table_schemas:
            self.sql_conn_cursor.execute(tb_s)

    def get_scraped_auction_ids(self, table_name, key_cols, retry_times=0):
        try:
            query = f"SELECT * from {table_name}"
            self.update_mysql_connection()
            self.sql_conn_dict_cursor.execute(query)

            auction_ids = {}

            for r in self.sql_conn_dict_cursor.fetchall():
                auction_ids.setdefault(self.get_record_key(r, key_cols), []).append(r['ID'])

            return auction_ids
        except Exception as e:
            if self.can_retry(f"Exception in get_scraped_auction_ids: \n{e}", retry_times):
                self.get_scraped_auction_ids(table_name, key_cols, retry_times + 1)
                return

    def get_record_key(self, r, cols):
        return "_".join([str(r[k]) for k in auction_table_cols if k in cols]).lower()

    def insert_auction_db(self, item, retry_times=0):
        item['Updated_At'] = self.get_datetime()

        key = self.get_record_key(item, ['URL'])
        if key in self.scraped_auctions and len(self.scraped_auctions[key]) == 1:
            item_id = self.scraped_auctions[key][0]

            update_vals = ["`{}`='{}'".format(k, self.clean_quotes(item[k])) for k in auction_table_cols if k in item]

            query = f"UPDATE {table_name_auction} SET {', '.join(update_vals)} WHERE `ID`={item_id}"
            self.update_record(query, item_id, table_name_auction)

        else:
            query = f"INSERT INTO `{table_name_auction}` ({', '.join(f'`{c}`' for c in auction_table_cols)}) " \
                    f"VALUES({', '.join(['%s'] * len(auction_table_cols))})"

            try:
                self.update_mysql_connection()
                self.sql_conn_cursor.execute(query, tuple([item[k] for k in auction_table_cols]))
                self.sql_connection.commit()
                logging.info(f"Inserted Auction Record into Table `{table_name_auction}`")

            except Exception as e:
                if self.can_retry(f"Exception while inserting auction: \n{e}", retry_times):
                    self.insert_auction_db(item, retry_times + 1)
                    return

    def get_datetime(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def clean_quotes(self, text):
        return re.sub(u"'", u'"', unescape(str(text) or ''))

    def update_record(self, query, item_id, table_name, retry_times=0):
        try:
            self.update_mysql_connection()
            self.sql_conn_cursor.execute(query)
            self.sql_connection.commit()
            print(f"Updated Table `{table_name}` WHERE Record ID = {item_id}")
        except Exception as e:
            if self.can_retry(f"Exception in update_record: \n{e}", retry_times):
                self.update_record(query, item_id, table_name, retry_times + 1)
                return

    def can_retry(self, log, retry_times):
        if retry_times == 2:
            return

        time.sleep(5)
        self.update_mysql_connection()
        print(log)
        return True

    def get_scraped_links(self, tab_name, col_name, retry_times=0):
        try:
            query = f"SELECT `{col_name}` from {tab_name}"
            self.update_mysql_connection()
            self.sql_conn_cursor.execute(query)
            return [r[0] for r in self.sql_conn_cursor.fetchall()]
        except Exception as e:
            if self.can_retry(f"Exception while inserting record: \n{e}", retry_times):
                self.get_scraped_links(retry_times + 1)
                return

    def is_database_created(self):
        self.sql_conn_cursor.execute("SHOW DATABASES")
        for db in self.sql_conn_cursor.fetchall():
            if db == Config.DB_NAME:
                return True
