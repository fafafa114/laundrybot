from datetime import datetime
import time
import gspread
import telegram
import threading
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler

chat1 = 123456
token = 'abc'

bot = telegram.Bot(token=token)
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher
sa = gspread.service_account(filename="service_account.json")
sh = sa.open_by_key("")
wks = sh.worksheet("Лист1")

flag = 0

reqs = [
{
  "chatid" : chat1,
  "str" : "abc",
  "req" : [2,0,0,0,1,0,0],
  "offset" : [5,4,3,2],
  "count" : 0
}

]

def set_appointment():
    x = [2,3,5]
    cell = wks.batch_get(['A1:E100'])[0]#0-indexed
    cell.insert(0,[])
    for i in range(len(cell)):
        while len(cell[i])<5:
            cell[i].append("")
    for i in range(0,len(cell)-4):
        b = cell[i][0]
        for j in range(len(b)):
            if b[j].isdigit():
                b=b[j:]
                break
        if len(b) < 10 or b.count(":")!=0 or b.count(".")<2:
            continue
        b = b[:10]
        tim = datetime.strptime(b,"%d.%m.%Y")
        for req in reqs:
            req["count"] = 0
            for coord_y in range(i+5,i,-1):
                for j in x:
                    if cell[coord_y][j-1] == req["str"]:
                        req["count"] += 1
        for req in reqs:
            for offs in req["offset"]:
                coord_y = i + offs
                for j in x:
                    if cell[coord_y][j-1] == "":
                        if req["count"] >= req["req"][tim.weekday()]:
                            continue
                        if wks.update_cell(coord_y,j,req["str"]).get('updatedCells')!=0:
                            bot.sendMessage(chat_id=req["chatid"], text=f"{b} {cell[coord_y][0]} {req['str']} machine{j-1}")
                            req["count"] += 1
                            cell[coord_y][j-1]="ggg"

class myThread (threading.Thread): 
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global flag
        while True:
            if flag:
                set_appointment()
            time.sleep(30)

def fafafa(update: Update, context: CallbackContext):
    bot.sendMessage(chat_id=chat1, text=f'stopped')
    print('fafafa')
    global flag
    flag = 0

def fafa(update: Update, context: CallbackContext):
    bot.sendMessage(chat_id=chat1, text=f'started')
    print('fafa')
    global flag
    flag = 1

def ping(update: Update, context: CallbackContext):
    global flag
    if flag:
        bot.send_message(chat_id=update.effective_chat.id, text="pong")

ping_handler = CommandHandler('ping', ping)
fafa_handler = CommandHandler('fafa',fafa)
fafafa_handler = CommandHandler('fafafa',fafafa)
dispatcher.add_handler(fafa_handler)
dispatcher.add_handler(fafafa_handler)
dispatcher.add_handler(ping_handler)
updater.start_polling()
thread1 = myThread()
thread1.start()
