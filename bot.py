from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
driver_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/chromedriver.exe"
brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

option = webdriver.ChromeOptions()
option.binary_location = brave_path
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="test"
)
sql = mydb.cursor()
# Command Handlers. Usually take two arguments: bot and update.

sql.execute(
    "CREATE TABLE IF NOT EXISTS user (chat_id INT SIGNED PRIMARY KEY,username VARCHAR(40),password VARCHAR(40))")


def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="Welcome to Attendance bot!!\nSend \n'/username + username'\n'/password + password'\nto store Id and password for future use\n/attendance to get attendance")


def username(update, context):
    com = "INSERT IGNORE INTO user (chat_id, username) VALUES (%s, %s)"
    val = (update.message.chat_id, str(context.args[0]))
    sql.execute(com, val)
    mydb.commit()
    context.bot.send_message(
        chat_id=update.message.chat_id, text="Username saved")


def password(update, context):
    com = f"UPDATE IGNORE user SET password=%s WHERE chat_id =%s"
    val = (str(context.args[0]), update.message.chat_id)
    sql.execute(com, val)
    mydb.commit()
    context.bot.send_message(
        chat_id=update.message.chat_id, text="Password saved")


def attendance(update, context):
    chat_id = update.message.chat_id
    sql.execute(f"SELECT * FROM user WHERE chat_id ={chat_id}")
    myresult = sql.fetchall()
    print(myresult)
    if len(myresult) == 0:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Username and Password not found\nSend \n'/username + username'\n'/password + password' to store Id and password for future use")
    elif myresult[0][1] == None:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Username not found\nSend \n'/username + username' to store Id and password for future use")
    elif myresult[0][2] == None:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Password not found\nSend'\n'/password + password' to store Id and password for future use")
    else:
        uname = myresult[0][1]
        pword = myresult[0][2]
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Please wait while I check your attendance")
        # Create new Instance of Chrome
        browser = webdriver.Chrome(executable_path=driver_path, options=option)
        browser.get("http://erp.ncuindia.edu/Welcome_iie.aspx")
        username = browser.find_element_by_id("tbUserName")
        username.send_keys(uname)
        pas = browser.find_element_by_id("tbPassword")
        pas.send_keys(pword)
        pas.send_keys(Keys.RETURN)
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "aAttandance"))
            )
            aten = browser.find_element_by_id(
                "aAttandance").get_attribute("href")
            browser.get(aten)
            try:
                element = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[@id='aspnetForm']/div[3]/div/div/div[2]/div/div/section/div/div[2]/table/tbody/tr"))
                )
                tr = len(browser.find_elements_by_xpath(
                    "//*[@id='aspnetForm']/div[3]/div/div/div[2]/div/div/section/div/div[2]/table/tbody/tr"))

                before_xpath = "//*[@id='aspnetForm']/div[3]/div/div/div[2]/div/div/section/div/div[2]/table/tbody/tr["
                aftertd_xpath = "]/td"
                data = ""
                for t_tr in range(1, tr):
                    finalxpath = before_xpath + str(t_tr) + aftertd_xpath
                    cell_text = browser.find_elements_by_xpath(finalxpath)
                    data = data+cell_text[1].text+"--"+cell_text[6].text+"\n\n"
            except:
                pass
        except:
            pass
        browser.quit()
        # send the link back
        context.bot.send_message(
            chat_id=update.message.chat_id, text=data)


def main():
    # Create updater and pass in Bot's auth key.
    updater = Updater(
        token='xxxxxxxxxxxxxxxxxxxxxxx', use_context=True)
    # Get dispatcher to register handlers
    dispatcher = updater.dispatcher
    # answer commands
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('username', username))
    dispatcher.add_handler(CommandHandler('password', password))
    dispatcher.add_handler(CommandHandler('attendance', attendance))
    # start the bot
    updater.start_polling()
    # Stop
    updater.idle()


if __name__ == '__main__':
    main()
