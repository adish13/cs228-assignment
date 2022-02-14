"""
0: Vertical Car
1: Horizontal Car
2: Mine
3: Red Car
"""


from z3 import *
import sys

def print_steps(m):
	for time in range(timeout):
		answer = []
		for i in range(n):
			for j in range(n):
				val = is_true(m[P[i][j][0][time]]) ^ is_true(m[P[i][j][0][time+1]])
				if val:
					answer=(i, j, "vertical")
		for i in range(n):
			for j in range(n):
				val = is_true(m[P[i][j][1][time]]) ^ is_true(m[P[i][j][1][time+1]])
				if val:
					answer=(i, j, "horizontal")
		for i in range(n):
			for j in range(n):
				val = is_true(m[P[i][j][2][time]]) ^ is_true(m[P[i][j][2][time+1]])
				if val:
					answer=(i, j, "mine")
		for i in range(n):
			for j in range(n):
				val = is_true(m[P[i][j][3][time]]) ^ is_true(m[P[i][j][3][time+1]])
				if val:
					answer=(i, j, "red")
		print(f"{answer[0]},{answer[1]}")


info = []
with open(sys.argv[1]) as f:
    for line in f:
        info.append([int(v) for v in line.strip().split(',')])

n = info[0][0]
timeout = info[0][1]
i0 = int(info[1][0]) # Initial row of the red car

cars = len(info) - 1 # Initial number of cars

P = [[[[Bool(f"P_{i}_{j}_{car_type}_{time}") for time in range(timeout + 1)] for car_type in range(4)] for j in range(n)] for i in range(n)]

positions = []
Fs = []

# Add conditions for the red car
positions.append([info[1][0], info[1][1], 3])
Fs.append(P[info[1][0]][info[1][1]][3][0])

for a in range(2, len(info)): # Iterate from after the red car
	car_type = info[a][0]
	if car_type >= 0 and car_type <= 2:
		i = info[a][1]
		j = info[a][2]
		Fs += [P[info[a][1]][info[a][2]][car_type][0]]
		positions.append([i, j, car_type])

# Encode positions that are not filled
for i in range(n):
	for j in range(n):
		for car_type in range(4):
			if [i,j,car_type] not in positions:
				Fs.append(Not(P[i][j][car_type][0]))


# Every square must have exactly one entry
# \sum p[i][j][k][time] = 1 at for every time
for time in range(timeout + 1):
	for i in range(n):
		for j in range(n):
			temp = []
			for car_type in range(4):
				temp.append(P[i][j][car_type][time])
			Fs.append(PbLe([(x,1) for x in temp], 1))

# Horizontal car at (i, j) implies nothing else at (i, j+1)
for time in range(timeout + 1):
	for i in range(n):
		for j in range(n-1):
			Fs.append(
			Or(Not(P[i][j][1][time]), Not(Or(P[i][j+1][0][time],P[i][j+1][1][time],P[i][j+1][2][time],P[i][j+1][3][time])))
			)

# print(Fs)
# Red Car at (i, j) implies nothing else at (i, j+1)
for time in range(timeout + 1):
	for i in range(n):
		for j in range(n -1):
			Fs.append(
			Or(Not(P[i][j][3][time]), Not(Or(P[i][j+1][0][time],P[i][j+1][1][time],P[i][j+1][2][time],P[i][j+1][3][time])))
			)

# Vertical car at (i, j) implies nothing else at (i+1, j)
for time in range(timeout + 1):
	for i in range(n - 1):
		for j in range(n):
			Fs.append(
			Or(Not(P[i][j][0][time]), Not(Or(P[i+1][j][0][time],P[i+1][j][1][time],P[i+1][j][2][time],P[i+1][j][3][time])))
			)

# No horizontal cars in last column
for time in range(timeout + 1):
	for i in range(n):
		Fs.append(Not(P[i][n-1][1][time]))

# No red cars in last column
for time in range(timeout + 1):
	for i in range(n):
		Fs.append(Not(P[i][n-1][3][time]))

# No vertical cars in last row
for time in range(timeout + 1):
	for j in range(n):
		Fs.append(Not(P[n-1][j][0][time]))

# Vertical car at (i, j) implies no horizontal car and no red car at (i+1, j-1)
for time in range(timeout + 1):
	for i in range(n - 1):
		for j in range(1, n):
			Fs += [  Or(Not(P[i][j][0][time]),And(Not(P[i+1][j-1][1][time]),Not(P[i+1][j-1][3][time])))]
# The mine stays in one place
for time in range(timeout):
	for i in range(n):
		for j in range(n):
			Fs.append(Or(Not(P[i][j][2][time]), P[i][j][2][time + 1]))
			Fs.append(Or(Not(P[i][j][2][time+1]), P[i][j][2][time]))
"""
Encoding the Moves Now
"""
for time in range(timeout):
	moves = []

	# Vertical Movement
	# Vertically Upwards
	for i in range(1, n-1):
		for j in range(n):
			moves.append(And(Not(P[i][j][0][time+1]), P[i][j][0][time], P[i-1][j][0][time+1]))
	
	# Vertically Downwards
	for i in range(n-2):
		for j in range(n):
			moves.append(And(Not(P[i][j][0][time+1]), P[i][j][0][time], P[i+1][j][0][time+1]))
	
	# Horizontal Movement (Horizontal Car)
	# Horizontally leftwards
	for i in range(n):
		for j in range(1, n-1):
			moves.append(And(Not(P[i][j][1][time+1]), P[i][j][1][time], P[i][j-1][1][time+1]))

	# Horizontally rightwards
	for i in range(n):
		for j in range(n-2):
			moves.append(And(Not(P[i][j][1][time+1]), P[i][j][1][time], P[i][j+1][1][time+1]))

	
	# Horizontal Movement (Red Car)
	# Horizontally leftwards
	for i in range(n):
		for j in range(1, n-1):
			moves.append(And(Not(P[i][j][3][time+1]), P[i][j][3][time], P[i][j-1][3][time+1]))

	# Horizontally rightwards
	for i in range(n):
		for j in range(n-2):
			moves.append(And(Not(P[i][j][3][time+1]), P[i][j][3][time], P[i][j+1][3][time+1]))
	
	Fs.append(PbEq([(x,1) for x in moves],1))

# For Horizontal
for time in range(1, timeout + 1):
	for i in range(n):
		for j in range(1, n-2):
			Fs.append(Or(Not(P[i][j][1][time]), P[i][j-1][1][time-1], P[i][j][1][time-1], P[i][j+1][1][time-1]))
		Fs.append(Or(Not(P[i][0][1][time]), P[i][1][1][time-1], P[i][0][1][time-1]))
		if (n >= 3):
			Fs.append(Or(Not(P[i][n-2][1][time]), P[i][n-3][1][time-1], P[i][n-2][1][time-1]))

# For Red Car
for time in range(1, timeout + 1):
	for i in range(n):
		for j in range(1, n-2):
			Fs.append(Or(Not(P[i][j][3][time]), P[i][j-1][3][time-1], P[i][j][3][time-1], P[i][j+1][3][time-1]))
		Fs.append(Or(Not(P[i][0][3][time]), P[i][1][3][time-1], P[i][0][3][time-1]))
		if (n >= 3):
			Fs.append(Or(Not(P[i][n-2][3][time]), P[i][n-3][3][time-1], P[i][n-2][3][time-1]))


for time in range(1, timeout + 1):
	for j in range(n):
		for i in range(1, n-2):
			Fs.append(Or(Not(P[i][j][0][time]), P[i-1][j][0][time-1], P[i][j][0][time-1], P[i+1][j][0][time-1]))
		Fs.append(Or(Not(P[0][j][0][time]), P[1][j][0][time-1], P[0][j][0][time-1]))
		if (n >= 3):
			Fs.append(Or(Not(P[n-2][j][0][time]), P[n-3][j][0][time-1], P[n-2][j][0][time-1]))

# # Total number of cars is constant
# for time in range(timeout+1):
# 	temp = []
# 	for i in range(n):
# 		for j in range(n):
# 			for car_type in range(4):
# 				temp.append(P[i][j][car_type][time])
# 	Fs.append(PbEq([(x,1) for x in temp], cars))


# Vertical Car
for time in range(timeout):
	for j in range(n):
		for i in range(1, n-2):
			Fs.append(Or(Not(P[i][j][0][time]), P[i+1][j][0][time+1], P[i][j][0][time+1], P[i-1][j][0][time+1]))
		Fs.append(Or(Not(P[0][j][0][time]), P[0][j][0][time+1], P[1][j][0][time+1]))
		if (n >= 3):
			Fs.append(Or(Not(P[n-2][j][0][time]), P[n-3][j][0][time+1], P[n-2][j][0][time+1]))

for time in range(timeout):
	for i in range(n):
		for j in range(1, n-2):
			Fs.append(Or(Not(P[i][j][1][time]), P[i][j+1][1][time+1], P[i][j][1][time+1], P[i][j-1][1][time+1]))
		Fs.append(Or(Not(P[i][0][1][time]), P[i][0][1][time+1], P[i][1][1][time+1]))
		if (n >= 3):
			Fs.append(Or(Not(P[i][n-2][1][time]), P[i][n-3][1][time+1], P[i][n-2][1][time+1]))

for time in range(timeout):
	for i in range(n):
		for j in range(1, n-2):
			Fs.append(Or(Not(P[i][j][3][time]), P[i][j+1][3][time+1], P[i][j][3][time+1], P[i][j-1][3][time+1]))
		Fs.append(Or(Not(P[i][0][3][time]), P[i][0][3][time+1], P[i][1][3][time+1]))
		if (n >= 3):
			Fs.append(Or(Not(P[i][n-2][3][time]), P[i][n-3][3][time+1], P[i][n-2][3][time+1]))



# Goal Clause
temp = []
for time in range(timeout+1):
	temp.append(P[i0][n-2][3][time])

Fs.append(PbGe([(x,1) for x in temp],1))

s = Solver()
s.add(Fs)
# check sat value
result = s.check()

if result == sat:
	m = s.model()
	#print("SAT")
	print_steps(m)
	# for k in range(timeout+1):
	# 	for i in range(n):
	# 		for j in range(n):
	# 			for l in range(4):
	# 				print(str(P[i][j][l][k])+str(m.eval(P[i][j][l][k])))

else:
    print("UNSAT")
