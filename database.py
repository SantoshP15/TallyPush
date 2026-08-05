import pyodbc

from config import (
    SERVER,
    DATABASE,
    TRUSTED_CONNECTION
)


def get_connection():

    conn = pyodbc.connect(

        f"""
        DRIVER={{ODBC Driver 17 for SQL Server}};
        SERVER={SERVER};
        DATABASE={DATABASE};
        Trusted_Connection={TRUSTED_CONNECTION};
        """

    )

    return conn

def get_last_alterid(table_name):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT ISNULL(MAX(AlterID),0)
        FROM {table_name}
        """
    )

    alterid = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return alterid