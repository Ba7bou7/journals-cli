from api import addSeason, getHistory, getCurrentSeason, getTable, addOrder, selectOrder


def PS(postion):
    return postion.title() + " [Help]" + " >>> "

def msg(messages):
    print()
    for message in messages:
        print("  *  " + message.title())
    print()


valid_opts = {
    "calendar" : {
        "table" : "getTable()",
        "order" : "addOrder({})",
        "select" : "selectOrder({})",
    },
    "seasons" : {
        "current" : "getCurrentSeason()",
        "add" : "addSeason()",
        "outcome" : "",
        "history" : "getHistory({})",
    },
}

section = "home"

if __name__ == "__main__" :
    while True:
        if ((cmnd := str(input(PS(section))).lower()) == "") and (section == "home"): break
        elif (cmnd == "") and (section != "home"):
            section = "home"
        else :
            cmnd = cmnd.split()
            if cmnd[0] == "help" or cmnd[0] == "h":
                if section == "home":
                    msg(valid_opts)
                elif section in valid_opts:
                    msg(valid_opts[section])

            elif cmnd[0] == "clear": print("\033c",end="")
            
            elif (section in valid_opts) and (cmnd[0] in valid_opts[section]):
                print()
                if len(cmnd) > 1:
                    exec(valid_opts[section][cmnd[0]].format(cmnd[1:]))
                else:
                    exec(valid_opts[section][cmnd[0]].format(''))
                print()
    
            elif cmnd[0] in valid_opts:
                section = cmnd[0]
    
            else : print("\n !! Command Not Fount !!",end="\n")
