# FoosMMR
Foosball MMR for the boys

## How To Run
- Fill input Dir with .txt files with ascending integer names corresponding to order of games played (i.e. 0.txt -> 1.txt -> 2.txt)
- Files should have 1 game per line, with the winning team being the first of 2 players, or the first 2 of 4 players. In the example below:  
__b__ beat __f__ and then __se & st__ beat __b & f__. etc..  
```
b,f
se,st,b,f
b,se
b,st
st,f,b,se
```
- To run, simply run the batch file. This only works on work PCs. Unlucky otherwise :D
- Output files will be filled into the output Dir. These are given the name of the date they were created, followed by an ascending number if multiple files were done on the same date. These are in the format `<player>, <elo>, <wins>, <totalGames>`

0.txt EX)
```
b, 1016.4282617770239, 3, 5
st, 1014.0942452472536, 2, 3
f, 982.9144948106042, 1, 3
se, 986.5632437159359, 1, 3
```
