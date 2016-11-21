import requests

roles_dict = dict(tank=[''], support=[''], dps=[''])
roles_dict["tank"] = ["D.Va", "Reinhardt", "Roadhog", "Winston", "Zarya", "Mei"]
roles_dict["support"] = ["Ana", "Lucio", "Mercy", "Symmetra", "Zenyatta"]
roles_dict["dps"] = ["Genji", "McCree", "Pharah", "Reaper", "Soldier: 76", "Tracer", "Bastion", "Hanzo", "Junkrat", "Torbjorn", "Widowmaker"]
valid_heroes = []
valid_heroes += roles_dict["tank"]
valid_heroes += roles_dict["support"]
valid_heroes += roles_dict["dps"]
comp_time_mult = 4  # the multiplier competitive hours get when determining stats


def removeFromLists(item, listOfLists):
    for aList in listOfLists:
        if item in aList:
            aList.remove(item)


def fixHeroName(name):
    """Fixes the unicode is Lucio's and Torbjorn's names"""
    if name == 'L&#xFA;cio':
        name = 'Lucio'
    if name == 'Torbj&#xF6;rn':
        name = 'Torbjorn'
    return str(name)


def getFromSite(site):
    """Returns the json from the given site"""
    response = requests.get(site)
    data = response.json()
    return data


def interpretPlaytime(dataString):
    """Returns the playtime as int in minutes"""
    if dataString[0] == '-':
        return 0
    spacePostion = dataString.index(' ')
    number = int(dataString[0:spacePostion])
    if dataString[spacePostion+1] == "h":
        return number*60
    else:
        return number


def playtimeString(minutes):
    hours = int(minutes / 60)
    minutes = minutes % 60
    output = ""
    if hours != 0:
        output += str(hours)
        output += "h"
    if minutes != 0 and hours != 0:
        output += ", "
    if minutes != 0:
        output += str(minutes)
        output += "m"
    if hours+minutes == 0:
        output += "--"
    return output


class Player:
    def __init__(self, name, region):
        self.name = name
        self.region = region
        self.mainRole = ""
        self.rank = ""
        self.tankValue = 0
        self.supportValue = 0
        self.dpsValue = 0
        self.totalValue = 0
        self.heroValues = {}
        self.orderedHeros = []
        self.siteComp = "https://api.lootbox.eu/pc/" + region + "/"+name+"/competitive/heroes"
        self.siteQuick = "https://api.lootbox.eu/pc/"+ region + "/"+name+"/quickplay/heroes"
        def setRoleValues(self, site, mult):
            data = getFromSite(site)
            for row in data:
                heroName = fixHeroName(row['name'])
                playtime = interpretPlaytime(row['playtime']) * mult
                if heroName in valid_heroes:
                    if heroName in roles_dict["tank"]:
                        self.tankValue += playtime
                    elif heroName in roles_dict["support"]:
                        self.supportValue += playtime
                    elif heroName in roles_dict["dps"]:
                        self.dpsValue += playtime
                    self.totalValue += playtime
                    if(heroName not in self.heroValues.keys()):
                        self.heroValues[heroName] = 0
                    else:
                        self.heroValues[heroName] += playtime
        setRoleValues(self, self.siteComp, comp_time_mult)
        setRoleValues(self, self.siteQuick, 1)
        self.tankValue = (float(self.tankValue)/float(self.totalValue))*100
        self.supportValue = (float(self.supportValue)/float(self.totalValue))*100
        self.dpsValue = (float(self.dpsValue)/float(self.totalValue))*100
        x = self.heroValues.items()
        newX = []
        for i in x:
            a = [i[1], i[0]]
            newX.append(a)
        newX = sorted(newX)
        newX.reverse()
        for i in newX:
            self.orderedHeros.append(i[1])
# nameList = ["Rubot42-1450", "Sarduin-1737"]
# nameDict = {}
# roles: tank, support, dps
# loading data from site
# create dictionary to hold character rating
# print(roles_dict)
# player1 = Player("Rubot42-1450", "us")
# print(player1.name)
# print("tank:    " + str(player1.tankValue) + "%")
# print("support: " + str(player1.supportValue) + "%")
# print("dps:     " + str(player1.dpsValue) + "%")


def teamComposer(team, region, tankNum, supportNum, dpsNum):
    if ((tankNum + supportNum + dpsNum) != 6):
        return "Team Composition Does not add up to 6"
    outputString=""
    player0 = Player(team[0], region)
    player1 = Player(team[1], region)
    player2 = Player(team[2], region)
    player3 = Player(team[3], region)
    player4 = Player(team[4], region)
    player5 = Player(team[5], region)
    playerList = [player0, player1, player2, player3, player4, player5]
    tankDict = {}
    tankList = []
    supportDict = {}
    supportList = []
    dpsDict = {}
    dpsList = []
    nameList = []
    for playerClass in playerList:
        nameList.append(playerClass)
        tankDict[playerClass.tankValue] = playerClass
        tankList.append(playerClass.tankValue)
        supportDict[playerClass.supportValue] = playerClass
        supportList.append(playerClass.supportValue)
        dpsDict[playerClass.dpsValue] = playerClass
        dpsList.append(playerClass.dpsValue)
    tankList.sort()
    tankList.reverse()
    supportList.sort()
    supportList.reverse()
    dpsList.sort()
    dpsList.reverse()
    def percentToName(aList, aDict):
        newList = []
        for i in aList:
            newList.append(aDict[i])
        return newList
    tankList = percentToName(tankList, tankDict)
    supportList = percentToName(supportList, supportDict)
    dpsList = percentToName(dpsList, dpsDict)

    supportList = supportList[0:supportNum]
    for i in supportList:
        removeFromLists(i, [tankList, dpsList])
    tankList = tankList[0:tankNum]
    for i in tankList:
        removeFromLists(i, [dpsList])
    dpsList = dpsList[0:dpsNum]
    teamComp = {}
    teamComp["tank"] = tankList
    teamComp["support"] = supportList
    teamComp["dps"] = dpsList
    # return teamComp
    for role in teamComp:
        outputString += (role.upper() + ":\n")
        for playerClass in teamComp[role]:
            outputString += (playerClass.name + "\n")
            topHeros = []
            for i in playerClass.orderedHeros:
                if(i in roles_dict[role]):
                    topHeros.append(i)
                    if(len(topHeros) >= 3):
                        break
            for i in range(3):
                outputString += ("\t" + str(i+1) + ") " + topHeros[i] + "\n")
            outputString += "\n"
    return outputString
teamRegion = "us"
team1 = ["Rubot42-1450", "Sarduin-1737", "Invis-1846", "nak-11167", "StormForge-11532", "Unk-11683"]
print(teamComposer(team1, teamRegion, 2, 2, 2))
