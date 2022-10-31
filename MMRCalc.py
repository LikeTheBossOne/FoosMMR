import os
from datetime import date
from os.path import exists

class Game:
    team1: 'list[str]' # Team 1 is always winning team
    team2: 'list[str]'
    
    def __init__(self, team1: 'list[str]', team2: 'list[str]'):
        self.team1 = team1
        self.team2 = team2
    
class Player:
    name: str
    wins: int
    totalGames: int
    elo: int
    
    def __init__(self, name):
        self.name = name
        self.wins = 0
        self.totalGames = 0
        self.elo = 1000

def GetInput() -> 'tuple[set[str],list[Game]]':
    allPlayers: set[str] = set()
    games: list[Game] = []
    
    # sort input numerically
    filepaths = os.listdir("./input")
    fileOrderMap: dict[int,str] = {}
    fileInts: list[int] = []
    for filepath in filepaths:
        filename = os.path.basename(filepath).split('.')[0]
        fileInt: int
        try:
            fileInt = int(filename)
            fileOrderMap[fileInt] = "input/" + filepath
            fileInts.append(fileInt)
        except:
            print("input file: \"" + filepath + "\" should have name convertable to int. skipping")
    fileInts.sort()
    fileNames: list[str] = []
    for fileInt in fileInts:
        fileNames.append(fileOrderMap[fileInt])
    
    for filename in fileNames:
        if filename.endswith(".txt"):
            lines = []
            with open(filename, 'r') as inFile:
                lines = inFile.readlines()
                for line in lines:
                    players = line.strip().split(',')
                    playerCount = len(players)
                    if playerCount % 2 == 1:
                        print("invalid input: \"" + line + "\" in file: \"" + filename)
                        print("ignoring game")
                        continue
                    team1 = []
                    team2 = []
                    for idx, player in enumerate(players):
                        if idx < playerCount / 2:
                            team1.append(player)
                        else:
                            team2.append(player)
                        if not player in allPlayers:
                            allPlayers.add(player)
                            print("Adding player: \"" + player + "\"")
                    games.append(Game(team1, team2))
                
    return (allPlayers, games)

def GetStartingElos(playerDict: 'dict[str,Player]'):
    if not exists('startingElo.txt'):
        return
    
    lines = []
    with open('startingElo.txt') as startingEloFile:
        lines = startingEloFile.readlines()
        
    for line in lines:
        line = line.strip()
        if line.startswith("//"):
            continue
        
        columns = line.split(',')
        
        if len(columns) != 2:
            print('startingElo.txt columns are invalid')
            continue
        
        playerName = columns[0]
        if playerName not in playerDict:
            playerDict[playerName] = Player(playerName)
            print('Adding player from startingElo.txt: \"' + playerName + '\"')
        
        playerDict[playerName].elo = int(columns[1])

def AverageTeamElo(teamElos: 'list[Player]'):
    total = 0
    for player in teamElos:
        total += player.elo
    return total / len(teamElos)

def Probability(me: int, opponent: int):
    return 1.0 * 1.0 / (1 + 1.0 * pow(10, 1.0 * (opponent - me) / 400))

def EloFunc1v1(me: Player, opponent: Player, result: bool) -> int:
    K = 50
    probIWin = Probability(me.elo, opponent.elo)
    
    if result:
        return me.elo + K * (1 - probIWin)
    else:
        return me.elo + K * (0 - probIWin)

def EloFunc2v2(myTeam: 'list[Player]', opponentTeam: 'list[Player]', result: bool) -> 'list[int]':
    K = 50
    S = 0.6 # Percentage that my own rating should factor into elo gain
    
    opponentTeamElo = AverageTeamElo(opponentTeam)
    
    teamPlayersWinProb = []
    for player in myTeam:
        teamPlayersWinProb.append(Probability(player.elo, opponentTeamElo))
    probMyTeamWins = Probability(AverageTeamElo(myTeam), opponentTeamElo)
    
    outElos = []
    if result:
        for idx, player in enumerate(myTeam):
            outElos.append(player.elo + K * (1 - (S * teamPlayersWinProb[idx] + (1 - S) * probMyTeamWins)))
    else:
        for idx, player in enumerate(myTeam):
            outElos.append(player.elo + K * (0 - (S * teamPlayersWinProb[idx] + (1 - S) * probMyTeamWins)))
    return outElos

def BuildPlayerHistory(players: 'set[str]', gameHistory: 'list[Game]') -> 'dict[str,Player]':
    playersDict: dict[str,Player] = {}
    for player in players:
        playersDict[player] = Player(player)
    GetStartingElos(playersDict)
    
    for game in gameHistory:
        if len(game.team1) == 1:
            winner = game.team1[0]
            loser = game.team2[0]
            winnerNewElo = EloFunc1v1(playersDict[winner], playersDict[loser], True)
            loserNewElo = EloFunc1v1(playersDict[loser], playersDict[winner], False)
            
            # Update Elo and stats
            playersDict[winner].totalGames += 1
            playersDict[winner].wins += 1
            playersDict[winner].elo = winnerNewElo
            
            playersDict[loser].totalGames += 1
            playersDict[loser].elo = loserNewElo
        else:
            winnersNewElos = EloFunc2v2([playersDict[game.team1[0]], playersDict[game.team1[1]]], [playersDict[game.team2[0]], playersDict[game.team2[1]]], True)
            losersNewElos = EloFunc2v2([playersDict[game.team2[0]], playersDict[game.team2[1]]], [playersDict[game.team1[0]], playersDict[game.team1[1]]], False)
            
            # Update Elo and stats
            for idx, winnerElo in enumerate(winnersNewElos):
                winner = game.team1[idx]
                playersDict[winner].totalGames += 1
                playersDict[winner].wins += 1
                playersDict[winner].elo = winnerElo
            for idx, loserElo in enumerate(losersNewElos):
                loser = game.team2[idx]
                playersDict[loser].totalGames += 1
                playersDict[loser].elo = loserElo
                
    return playersDict

def Output(playerDict: 'dict[str,Player]'):
    originalOutPath =  "output\\" + date.today().strftime("%Y_%m_%d")
    outPath = originalOutPath + ".txt"
    count = 1
    while exists(outPath):
        outPath = originalOutPath + "_" + str(count) + ".txt"
        count += 1
    
    with open(outPath, 'w') as outFile:
        for playerName, player in playerDict.items():
            outFile.write(playerName + ", " + str(player.elo) + ", " + str(player.wins) + ", " + str(player.totalGames) + "\n")

def main():
    players, games = GetInput()
    
    playerDict = BuildPlayerHistory(players, games)
    Output(playerDict)
    
    
if __name__=="__main__":
    main()