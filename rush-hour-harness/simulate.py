import sys

info = []
with open(sys.argv[1]) as f:
	for line in f:
		info.append([int(v) for v in line.strip().split(',')])
		
moves = []
with open(sys.argv[2]) as f:
	for line in f:
		moves.append([int(v) for v in line.strip().split(',')])
		
n = info[0][0]
timeout = info[0][1]

if len(moves) > timeout:
	print("timeout violated")

board = [[0 for i in range(n)] for j in range(n)]

red_car = info[1]
red_row = red_car[0]
red_col = red_car[1]

if red_col == n-1:
	print("invalid init")
	sys.exit(0)
	
if red_col == n-2:
	print("trivially sat")
	sys.exit(0)

board[red_row][red_col] = 2
board[red_row][red_col+1] = 2

for car in info[2:]:
	orient = car[0]
	row = car[1]
	col = car[2]
	
	if orient == 0:
		if row == n-1:
			print("invalid init")
			sys.exit(0)
		if board[row][col] + board[row+1][col] != 0:
			print("invalid init")
			sys.exit(0)
		board[row][col] = 1
		board[row+1][col] = 1
		
	elif orient == 1:
		if col == n-1:
			print("invalid init")
			sys.exit(0)
		if board[row][col] + board[row][col+1] != 0:
			print("invalid init")
			sys.exit(0)
		board[row][col] = 2
		board[row][col+1] = 2
		
		if row == red_row and col > red_col:
			print("unsat")
			sys.exit(0)
			
	else:
		if board[row][col] != 0:
			print("invalid init")
			sys.exit(0)
		
		board[row][col] = 3
		
		if row == red_row and col > red_col:
			print("unsat")
			sys.exit(0)

print("Run starting")
for row in board:
	print(row)
			
for i in range(len(moves)):
	row = moves[i][0]
	col = moves[i][1]
	if board[row][col] == 0:
		print("no car there, move {}".format(i))
		sys.exit(0)
	type = board[row][col]
	
	if type == 1 and (row == 0 or row == n-1):
		print("going out of board, move {}".format(i))
		sys.exit(0)
	
	if type == 2 and (col == 0 or col == n-1):
		print("going out of board, move {}".format(i))
		sys.exit(0)
		
	if type == 1:
		if board[row+1][col]*board[row-1][col] != 0:
			print("collision, move {}".format(i))
			sys.exit(0)
			
		if board[row+1][col] + board[row-1][col] != board[row][col]:
			print("absurd, move {}".format(i))
			sys.exit(0)
			
		board[row+1][col], board[row-1][col] =  board[row-1][col], board[row+1][col]
		
	if type == 2:
		if board[row][col+1]*board[row][col-1] != 0:
			print("collision, move {}".format(i))
			sys.exit(0)
			
		if board[row][col+1] + board[row][col-1] != board[row][col]:
			print("absurd, move {}".format(i))
			sys.exit(0)
			
		board[row][col+1], board[row][col-1] =  board[row][col-1], board[row][col+1]
		
	if i == len(moves) -1:
		print("Run completed")
		for row in board:
			print(row)
		
if board[red_row][n-1] != 2:
	print("did not reach target")
	sys.exit(0)
		
# no_hcars = 0
# no_vcars = 0
# no_mine = 0
# for i in range(2,len(info)):
#     if info[i][0] == 0:
#         no_vcars += 1
#     if info[i][0] == 1:
#         no_hcars += 1
#     if info[i][0] == 0:
#     no_hcars = 0
# no_vcars = 0
# no_mine = 0
#         no_mine += 1

# v_cars = [ [ [Int ("vc_{}_{}_{}".format(m,j,x)) for x in range(2)] for j in range(no_vcars)] for m in range(timeout)]    
# h_cars =[ [ [Int ("hc_{}_{}_{}".format(m,j,x)) for x in range(2)] for j in range(no_hcars)] for m in range(timeout)] 
# mines = [ [ [Int ("mine_{}_{}_{}".format(m,j,x)) for x in range(2)] for j in range(no_mine)] for m in range(timeout)] 
# redcar = [ [Int ("rc_{}_{}".format(m,x)) for x in range(2)] for m in range(timeout)]

# vcn=0
# hcn=0
# mn=0

# for i in range(2,len(info)):
#     if info[i][0] == 0:
#         v_cars[0][vcn][0] = info[i][1]
#         v_cars[0][vcn][1] = info[i][2]
#         vcn += 1

#     if info[i][0] == 1:
#         h_cars[0][hcn][0] = info[i][1]
#         h_cars[0][hcn][1] = info[i][2]
#         hcn += 1
#     if info[i][0] == 0:
#         mines[0][mn][0] = info[i][1]
#         mines[0][mn][1] = info[i][2]
#         mn += 1

# redcar[0][0] = info[1][0]
# redcar[0][1] = info[1][1]

# moves = [ [Int ("vc_{}_{}".format(j,m)) for j in range(2*(no_vcars+no_hcars+1))] for m in range(timeout)]    

# freshvar_counter = 0
# def sum_to_one( ls ):
# 	global freshvar_counter
# 	num = len(ls)
# 	aux = []
# 	for i in range(num+1):
# 		aux += [Bool("aux_{}".format(freshvar_counter))]
# 		freshvar_counter += 1
	
# 	F = [Not(aux[0]), aux[num]]
# 	for i in range(num):
# 		F += [Or(Not(aux[i]), Not(ls[i])), Or(Not(aux[i]), aux[i+1]), Or(Not(ls[i]), aux[i+1]), Or(Not(aux[i+1]), aux[i], ls[i])]
# 	return F

# moves_constraints = []
# for i in range(timeout):
#     moves_constraints += sum_to_one(moves[i])    

# moves = []
# for i in ran
# s = Solver()
# s.add()