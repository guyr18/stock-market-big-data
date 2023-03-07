import os
from sqlalchemy import create_engine, text
from api.DBConfig import DBConfig

targetDir = "Stocks"

try:

    print("Building list of dataset relative files..")
    files = os.listdir(targetDir)
    print("List constructed!")

except Exception:
    print("Could not locate 'Stocks' directory! Terminating..")

numFiles = len(files)

def populateDatabase():

    print("Beginning to populate database..")
    connect_args = {'local_infile': True}
    url = f"{DBConfig.CONNECTOR_SUBSTR}://{DBConfig.DB_USERNAME}:{DBConfig.DB_PWD}@{DBConfig.DB_HOST_IP}/{DBConfig.DB_NAME}"
    engine = create_engine(url, connect_args=connect_args)
    connection = engine.connect()

    for idx in range(numFiles):
        path = files[idx]
        print(f"Reading dataset ({idx + 1}/{numFiles}) at path: {path}")

        # Build history query for LOAD DATA predicate.
        historyQuery = f"""
        LOAD DATA LOCAL INFILE '{targetDir}/{path}'
        INTO TABLE shares
        FIELDS TERMINATED BY ','
        LINES TERMINATED BY '\n'
        IGNORE 1 LINES
        (Date, Open, Close, Low, High, Volume, stock_id)
        """
        
        # Execute.
        connection.execute(text(historyQuery))

        # We need to find the delimiter index (.) in the filename, so that we know
        # the acronym for the current stock.
        delimIndex = 0

        while path[delimIndex] != '.':
            delimIndex += 1

        stockName = path[:delimIndex] # Get stock name which always comes before first '.' character.

        # Call stored procedure to add stock id and name and execute.
        stockQuery = f"CALL trans_sp_add_stock({idx}, '{stockName}');"
        connection.execute(text(stockQuery))
        connection.commit()

    if not connection.closed:
        connection.close()

    print("Database populated!")

populateDatabase()