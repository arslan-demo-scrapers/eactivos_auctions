from eactivos_auctions.eactivos_auctions.config.env_config import Config

table_name_auction = "table_eactivos_auctions"

auction_table_cols = [
    'Auction_ID', 'Name', 'Location', 'Category', 'Appraisal_Amount', 'Auction_Value',
    'Minimum_Bid', 'Highest_Bid', 'Has_Started', 'Start_Date', 'End_Date', 'Finca', 'Registro',
    'Management_Costs', 'Expenses', 'Characteristics', 'Description', 'Complete_Description',
    'Image_Links', 'Document_Links', 'Downloaded_File_Paths', 'URL',
]

table_schemas = [
    f"""
    CREATE TABLE IF NOT EXISTS `{Config.DB_NAME}`.`{table_name_auction}` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Auction_ID` VARCHAR(500) NULL,
    `Name` TEXT NOT NULL,
    `Location` TEXT NULL,
    `Category` VARCHAR(500) NULL,
    `Appraisal_Amount` VARCHAR(100) NULL,
    `Auction_Value` VARCHAR(100) NULL,
    `Minimum_Bid` VARCHAR(100) NULL,
    `Highest_Bid` VARCHAR(100) NULL,
    `Management_Costs` VARCHAR(100) NULL,
    `Expenses` TEXT NULL,
    `Has_Started` VARCHAR(10) NULL,
    `Start_Date` VARCHAR(100) NULL,
    `End_Date` VARCHAR(100) NULL,
    `Registro` VARCHAR(500) NULL,
    `Finca` VARCHAR(500) NULL,
    `Description` TEXT NULL,
    `Characteristics` TEXT NULL,
    `Complete_Description` TEXT NULL,
    `Image_Links` TEXT NULL,
    `Document_Links` TEXT NULL,
    `Downloaded_File_Paths` TEXT NULL,
    `URL` VARCHAR(1000) NULL,
    `Updated_At` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    `Created_At` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
     PRIMARY KEY (`ID`));
    """,
]
