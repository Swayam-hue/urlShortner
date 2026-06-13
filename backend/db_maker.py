import mysql.connector

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "@Swayam2005",
    database = "urlshortner"
)

mycursor = mydb.cursor()

# mycursor.execute("CREATE DATABASE URLSHORTNER")

# mycursor.execute("CREATE TABLE urlTable (longURL varchar(255), shortCode varchar(255))")