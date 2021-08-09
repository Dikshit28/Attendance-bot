from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import dbcrud as db

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
#DRIVER PATH IS CHROMEDRIVER PATH
driver_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/chromedriver.exe"
#BRAVE PATH IS LOCATION OF ANY BROWSER'S .EXE FILE
brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

option = webdriver.ChromeOptions()
option.binary_location = brave_path
option.add_argument('--headless')
option.add_argument('--disable-gpu')

# Command Handlers. Usually take two arguments: bot and update.

def start(update, context):
    context.bot.send_message(chat_id=update.message.chat_id,text="Welcome to Attendance bot!!\nSend \n'/username username'\n'/password password'\nto store Id and password for future use\n/attendance to get attendance")


def username(update, context):
    val = [update.message.chat_id, str(context.args[0])]
    db.update_username(val[0],val[1])
    context.bot.send_message(
        chat_id=update.message.chat_id, text="Username saved")


def password(update, context):
    val = [update.message.chat_id,str(context.args[0])]
    db.update_password(val[0], val[1])
    context.bot.send_message(
        chat_id=update.message.chat_id, text="Password saved")


def attendance(update, context):
    chat_id = update.message.chat_id
    myresult =db.get_details(chat_id)
    print(myresult)
    if myresult[0] == None and myresult[1] == None:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Username and Password not found\nSend \n'/username + username'\n'/password + password' to store Id and password for future use")
    elif myresult[0] == None:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Username not found\nSend \n'/username + username' to store Id and password for future use")
    elif myresult[1] == None:
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Password not found\nSend'\n'/password + password' to store Id and password for future use")
    else:
        uname = myresult[0]
        pword = myresult[1]
        context.bot.send_message(
            chat_id=update.message.chat_id, text="Please wait while I check your attendance")
        # Create new Instance of Chrome
        try:
            browser = webdriver.Chrome(executable_path=driver_path, options=option)
            browser.get("https://erp.ncuindia.edu/Welcome_iie.aspx")
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
                check=True
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
                    check=True
                except:
                    check=False
            except:
                check=False
            browser.quit()
        except:
            check=False
        if check==False:
            if db.get_attendance(chatid=chat_id) == None:
                data= "Process failed"
            else:
                data = "Process failed\nSending the last saved attendance\n\n"+db.get_attendance(chatid=chat_id)
        else:    
            db.update_attendance(chat_id, data)
        # send the link back
        context.bot.send_message(
            chat_id=update.message.chat_id, text=data)


def main():
    # Create updater and pass in Bot's auth key.
    updater = Updater(
        token='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', use_context=True)
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
