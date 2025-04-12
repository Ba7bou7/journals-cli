from package import db_path
from datetime import datetime, timedelta
import sqlite3

db = sqlite3.connect(db_path)
cursor = db.cursor()

season_columns = [
    'balance',
    'daily_loss',
    'overall_loss',
    'trading_session',
    'spot',
    'positions_size',
    'max_orders',
    'stopLoss_range',
    'takeProfit_range',
    'risk_reward_ratio',
    'expire_date'
]

cursor.execute('''
CREATE TABLE IF NOT EXISTS seasons (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    balance REAL NOT NULL,
    daily_loss REAL NOT NULL,
    overall_loss REAL NOT NULL,
    trading_session TEXT NOT NULL,
    spot TEXT NOT NULL,
    positions_size REAL NOT NULL,
    max_orders INT NOT NULL,
    stopLoss_range TEXT NOT NULL,
    takeProfit_range TEXT NOT NULL,
    risk_reward_ratio TEXT NOT NULL,
    expire_date DATE NOT NULL
)''')

order_columns = [
    'position',
    'entre_method',
    'entre_conditions',
    'status',
    'profit_or_loss',
    'emotion',
    'breaking_rules',
    'notes_about_the_trade'
]

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    position TEXT NOT NULL,
    entre_method TEXT NOT NULL,
    entre_conditions TEXT NOT NULL,
    status TEXT NOT NULL,
    profit_or_loss REAL NOT NULL,
    emotion TEXT NOT NULL,
    breaking_rules TEXT NOT NULL,
    notes_about_the_trade TEXT NOT NULL
)''')

db.commit()
db.close()

days = ['Monday','Tuesday','Wednesday','Thursday','Friday']


def addRow(table_name, columns, values):
    try:
        db = sqlite3.connect(db_path)
        cursor = db.cursor()
        
        columns_str = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(values))
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        cursor.execute(query, values)
        
        db.commit()
        
    except sqlite3.Error as e:
        print(f"Error occurred: {e}")

    finally:
        if db: db.close()
    

def getList(table,columns="*"):
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    if type(columns) == list:
        columns_str = ", ".join(columns)
        cursor.execute(f'SELECT {columns_str} FROM {table}')
    else:
        cursor.execute(f'SELECT {columns} FROM {table}')
    
    List = cursor.fetchall()
    db.close()
    return List


def seasonCheck(result=bool):
    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    query = "SELECT * FROM seasons ORDER BY id DESC LIMIT 1"
    cursor.execute(query)
    last_row = cursor.fetchone()
    db.close()

    if last_row != None:
        expire_date = last_row[-1].split('-')
        today_date = datetime.now().strftime("%d-%m-%Y").split('-')
        check = True
        for i in range(3):
            check = check and (int(today_date[i]) <= int(expire_date[i]))

        if result is bool: return check
        elif result is tuple: return (last_row[1], last_row[-1])
    else: return False


def getTable():
    if seasonCheck():
        start_date, end_date = seasonCheck(tuple)
        start_date = datetime.strptime(start_date, "%d-%m-%Y")
        end_date = datetime.strptime(end_date, "%d-%m-%Y")
        
        weeks = [
            ['','','','',''],
        ]
        
        orders = getList("orders",["date","profit_or_loss"])
        for order in orders:
            order_date, order_PL = order
            order_date = order_date.split()
            day = order_date[0]
            date = datetime.strptime(order_date[1],"%d-%m-%Y")

            week = start_date
            if (start_date <= date <= end_date):
                if (week <= date < (week + timedelta(days=7))):
                    for i in range(len(days)):
                        if day == days[i]:
                            if type(weeks[-1][i]) is str:
                                weeks[-1][i] = float(0)
                            if type(order_PL) is float:
                                weeks[-1][i] += order_PL
                            weeks[-1][i] = round(weeks[-1][i], 2)
                else:
                    week = week + timedelta(days=7)
                    weeks.append(['']*5)
                    if (week <= date < (week + timedelta(days=7))):
                        for i in range(len(days)):
                            if day == days[i]:
                                if type(weeks[-1][i]) is str:
                                    weeks[-1][i] = float(0)
                                if type(order_PL) is float:
                                    weeks[-1][i] += order_PL
                                weeks[-1][i] = round(weeks[-1][i], 2)

        print('        | ', end='')
        for col in days:
            print(col, end=' | ')
        print()
        for i,row in enumerate(weeks):
            print(f' Week {i+1} | ', end='')
            for col in range(len(row)):
                print(str(row[col]) + ' '*(len(days[col])-len(str(row[col]))), end=' | ')
            print()
    else:
        print("-!- There is No Current Season -!-")


def addOrder(selector=None):
    if seasonCheck():
        today_day = datetime.now().strftime("%A")
        
        if selector is not None and len(selector) == 1:
            db = sqlite3.connect(db_path)
            cursor = db.cursor()
            today = datetime.now().strftime("%A %d-%m-%Y")
            query = f"SELECT id, date, position FROM orders WHERE date = '{today}';"
            cursor.execute(query)
    
            orders = cursor.fetchall()
            order_id, order_date, position_type = orders[int(selector[0])-1]
            print(" -+- "+position_type.title()+" Order "+selector[0]+" at "+order_date+" -+- ")
            for col in ['status','profit_or_loss']:
                while True:
                    if (value := input(col.title() + " : ")) != "":
                        break
                update = f"UPDATE orders SET {col} = ? WHERE id = ?;"
                cursor.execute(update,(value, order_id))
            db.commit()
            db.close()
        
        elif today_day in days:
            values = []
            print("-*- Adding New Order -*-")
            for col in order_columns:
                if col not in ['entre_conditions','breaking_rules','notes_about_the_trade']:
                    if col not in ['status','profit_or_loss']:
                        while True:
                            if (value := input(col.title() + " : ")) != "":
                                break
                    else:
                        value = ''
                
                elif col == 'entre_conditions':
                    long_str = []
                    while (value := input(" - ")) != "":
                        long_str.append(value)
                    value = '|'.join(long_str)
                
                elif col == 'breaking_rules':
                    long_str = []
                    print(col.title() + " :")
                    while (value := input(" - ")) != "":
                        long_str.append(value)
                    value = '|'.join(long_str)
                
                elif col == 'notes_about_the_trade':
                    print(col.title() + " :")
                    value = input("--> ")
    
                values.append(value)
            
            addRow("orders", ["date"]+order_columns, [datetime.now().strftime('%A %d-%m-%Y')]+values)
        
        else:
            print(f"-!- No Trading Session on {today_day} -!-")
    else:
        print("-!- There is No Current Season -!-")


def selectOrder(args=None):
    if seasonCheck():
        db = sqlite3.connect(db_path)
        cursor = db.cursor()
        if args is None:
            today = datetime.now().strftime("%A %d-%m-%Y")
            query = f"SELECT date, position FROM orders WHERE date = '{today}';"
            cursor.execute(query)
            
            orders = cursor.fetchall()
            
            for i, order in enumerate(orders):
                order_date, position_type = order
                print(" -#- ["+str(i+1)+"] - "+position_type.title()+" Order at "+order_date+" -#- ")
    
        elif 1 <= len(args) <= 4:
            query = '''SELECT 
                date,
                position,
                entre_method,
                entre_conditions,
                status,
                profit_or_loss,
                emotion,
                breaking_rules,
                notes_about_the_trade
            FROM orders ;'''
            cursor.execute(query)
            orders = cursor.fetchall()
            
            selected = []
            
            start_date, end_date = seasonCheck(tuple)
            start_date = datetime.strptime(start_date, "%d-%m-%Y")
            end_date = datetime.strptime(end_date, "%d-%m-%Y")
            
            for order in orders:
                order = list(order)
                date = datetime.strptime(order[0].split()[1],"%d-%m-%Y")
                if (start_date <= date <= end_date):
                    selected.append(order)
                    if len(args) > 1 and "week" in args and args[args.index("week")+1].isdigit():
                        week = start_date + timedelta(days=(7*(int(args[args.index("week")+1])-1)))
                        if not(week <= date < (week + timedelta(days=7))) and order in selected:
                            selected.remove(order)
            
                    if len(args) > 0 and any(arg.title() in days for arg in args):
                        selector_day = next((arg.title() for arg in args if arg.title() in days), None)
                        for order in selected:
                            day = order[0].split()[0]
                            if day != selector_day and order in selected:
                                selected.remove(order)
            
            if len(args) > 1 and "week" in args and args[args.index("week")+1].isdigit():
                del args[args.index("week")+1]
                del args[args.index("week")]
            if len(args) > 0 and any(arg.title() in days for arg in args):
                args.remove(next((arg for arg in args if arg.title() in days), None))

            if len(args) == 1 and args[0].isdigit():
                order_date = selected[int(args[0])-1].pop(0)
                print(" -*- Order "+args[0]+" at "+order_date+" -*-")
                for col, val in zip(order_columns,selected[int(args[0])-1]):
                    if col not in ['entre_conditions','breaking_rules','notes_about_the_trade']:
                        print(col.title()+" : "+str(val))
    
                    elif col == 'entre_conditions':
                        long_str = val.split('|')
                        for line in long_str:
                            print(" - "+line)
        
                    elif col == 'breaking_rules':
                        long_str = val.split('|')
                        print(col.title() + " :")
                        for line in long_str:
                            print(" - "+line)
        
                    elif col == 'notes_about_the_trade':
                        print(col.title() + " :")
                        print("--> "+val)
            
            elif len(args) == 0:
                for i, order in enumerate(selected):
                    order_date = order[0]
                    position_type = order[1]
                    print(" -#- ["+str(i+1)+"] - "+position_type.title()+" Order at "+order_date+" -#- ")
    
            else:
                param = ", ".join(args)
                print(f" -!- Wrong parameters : {param} -!-")
        
        db.close()
    
    else:
        print("-!- There is No Current Season -!-")


def addSeason():
    values = []
    print("-*- Adding New Season -*-")
    for col in season_columns:
        while True:
            if (value := input(col.title() + " : ")) != "":
                break
        values.append(value)

    addRow("seasons", ["date"]+season_columns, [datetime.now().strftime("%d-%m-%Y")]+values)


def getHistory(filtered=["date"]):
    seasons = getList('seasons',filtered)
    print("-*- Season History -*-")
    for season in seasons:
        display = " - Season "
        display += " | ".join(season)
        print(display)

def getCurrentSeason():
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    columns_str = ", ".join(season_columns)
    query = f"SELECT {columns_str} FROM seasons ORDER BY id DESC LIMIT 1"
    cursor.execute(query)
    
    last_row = cursor.fetchone()
    db.close()

    if seasonCheck():
        print("-*- Current Season -*-")
        for var,item in zip(season_columns,last_row):
            print(var.title()+" : "+str(item))
    else:
        print("-!- There is No Current Season -!-")

def outcome():
    if seasonCheck():
        db = sqlite3.connect(db_path)
        cursor = db.cursor()
        query = "SELECT date, profit_or_loss FROM orders ;"
        cursor.execute(query)
        orders = cursor.fetchall()
        
        start_date, end_date = seasonCheck(tuple)
        start_date = datetime.strptime(start_date, "%d-%m-%Y")
        end_date = datetime.strptime(end_date, "%d-%m-%Y")
        
        new_balance = 0
        total_orders = 0

        for order in orders:
            date = datetime.strptime(order[0].split()[1],"%d-%m-%Y")
            if (start_date <= date <= end_date):
                total_orders += 1
                new_balance += order[1]

        query = "SELECT balance FROM seasons ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        balance = cursor.fetchone()[0]
        
        print(" -$- New Balance :",balance+new_balance,"-$-")
        print(" -$- Total Orders :",total_orders,"-$-")

        db.close()

    else :
        print("-!- There is No Current Season -!-")

outcome()
