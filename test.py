"""
0: Vertical Car
1: Horizontal Car
2: Mine
3: Red Car
"""


from z3 import *
import sys

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
Ss = []
# Red Car at (i, j) implies nothing else at (i, j+1)
for time in range(timeout + 1):
	for i in range(n):
		for j in range(n -1):
			Fs.append(
			Or(Not(P[i][j][3][time]), Not(Or(P[i][j+1][0][time],P[i][j+1][1][time],P[i][j+1][2][time],P[i][j+1][3][time])))
			)

print(Ss)
# Vertical car at (i, j) implies nothing else at (i+1, j)
Vs = []
for time in range(timeout + 1):
	for i in range(n - 1):
		for j in range(n):
			Fs.append(
			Or(Not(P[i][j][0][time]), Not(Or(P[i+1][j][0][time],P[i+1][j][1][time],P[i+1][j][2][time],P[i+1][j][3][time])))
			)

print(Vs)
# No horizontal cars in last column
for time in range(timeout + 1):
	for i in range(n):
		Fs.append(Not(P[i][n-1][1][time]))

# No red cars in last column
for time in range(timeout + 1):
	Fs.append(Not(P[i0][n-1][3][time]))

Bs = []
# No vertical cars in last row
for time in range(timeout + 1):
	for j in range(n):
		Fs.append(Not(P[n-1][j][0][time]))

print(Bs)
# Vertical car at (i, j) implies no horizontal car and no red car at (i+1, j-1)
Cs = []
for time in range(timeout + 1):
	for i in range(n - 1):
		for j in range(1, n):
			Fs += [  Or(Not(P[i][j][0][time]),And(Not(P[i+1][j-1][1][time]),Not(P[i+1][j-1][3][time])))]
print(Cs)
# The mine stays in one place
Ds = []
for time in range(timeout):
	for i in range(n):
		for j in range(n):
			Fs.append(Or(Not(P[i][j][2][time]), P[i][j][2][time + 1]))
			Fs.append(Or(Not(P[i][j][2][time+1]), P[i][j][2][time]))
print(Ds)
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
    # get satisfying model
    m = s.model()

    # print only if value is true
    # print (sorted ([(d, m[d]) for d in m], key = lambda x: str(x[0]))

    #for i in range(timeout+1):
    #    for j in range(n*n*4):
    #        print(str(P[i][j])+str(m.eval(P[i][j])))


    print("SAT")

else:
    print("UNSAT")
