from z3 import *
import sys

info = []
with open(sys.argv[1]) as f:
    for line in f:
        info.append([int(v) for v in line.strip().split(',')])

n = info[0][0]
timeout = info[0][1]
i0 = int(info[1][0])

cars = len(info) - 1
no_hcars = 0
no_vcars = 0
no_mine = 0
for i in range(2,len(info)):
    if info[i][0] == 0:
        no_vcars += 1
    if info[i][0] == 1:
        no_hcars += 1
    if info[i][0] == 0:
        no_hcars = 0
    else:
        no_mine += 1

#timeout = 1

# defining the initial variables
P = [[Bool ("P_{}_{}".format(i,j)) for i in range(n*n*4)] for j in range(timeout+1)]
# P[(4*n*i)+(4*j)+ t ] means car of type t is in cell (i,j) 
# t = 3 red car, rest all same as question

array_indices = []

Fs = []
Fs += [ P[0][(4*n*info[1][0]) + (4*info[1][1]) + 3] ]
array_indices.append((4*n*info[1][0]) + (4*info[1][1]) + 3)

# Encode already filled positions
for a in range(2,len(info)):
    k = info[a][0]
    if k >= 0 and k <= 2:
        Fs += [P[0][(4*n*info[a][1]) + (4*info[a][2]) + k]]
        array_indices.append((4*n*info[a][1]) + (4*info[a][2]) + k)
#print(Fs)

for x in range(n*n*4):
    if x not in array_indices:
        Fs += [Not(P[0][x])]

# Encode for i,j  \sum_k x_i_j_k = 1
# each square must have exactly one entry
for k in range(timeout+1):
    for i in range(n):
        for j in range(n):
            Fs += [PbLe([(x,1) for x in P[k][4*n*i + 4*j: 4*n*i+4*j + 4: 1]],1)]


# horizontal car at (i,j) implies nothing else at (i,j+1)
for k in range(timeout+1):
    for i in range(n):
        for j in range(n-1):
            Fs += [Or(Not(P[k][4*n*i+4*j+1]), 
            And( Not(P[k][4*n*i+4*(j+1)+0]),Not(P[k][4*n*i+4*(j+1)+1]),Not(P[k][4*n*i+4*(j+1)+2]),Not(P[k][4*n*i+4*(j+1)+3])) )]

# red car at (i,j) implies nothing else at (i,j+1)
for k in range(timeout+1):
    for i in range(n):
        for j in range(n-1):
            Fs += [Or(Not(P[k][4*n*i+4*j+3]),
            And( Not(P[k][4*n*i+4*(j+1)+0]),Not(P[k][4*n*i+4*(j+1)+1]),Not(P[k][4*n*i+4*(j+1)+2]),Not(P[k][4*n*i+4*(j+1)+3])) )]

# vertical car at (i,j) implies nothing else car at (i+1,j)
for k in range(timeout+1):
    for i in range(n-1):
        for j in range(n):
            Fs += [Or(Not(P[k][4*n*i+4*j+0]),
            And(Not(P[k][4*n*(i+1)+4*j+0]),Not(P[k][4*n*(i+1)+4*j+1]),Not(P[k][4*n*(i+1)+4*j+2]),Not(P[k][4*n*(i+1)+4*j+3]))  )    ]

# No horizontal cars in last column 
for k in range(timeout+1):
    for i in range(n):
        Fs += [Not(P[k][4*n*i+4*(n-1)+1])]

# No red cars in last column 
for k in range(timeout+1):
    for i in range(n):
        Fs += [Not(P[k][4*n*i+4*(n-1)+3])]

# No vertical cars in last row 
for k in range(timeout+1):
    for j in range(n):
        Fs += [Not(P[k][4*n*(n-1)+4*j+0])]

# vertical car at (i,j) implies no horizontal car  and no red car at (i+1,j-1)
for k in range(timeout+1):
    for i in range(n-1):
        for j in range(1,n):
            Fs += [  Or(Not(P[k][4*n*i+4*j]),And(Not(P[k][4*n*(i+1)+4*(j-1)+1]),Not(P[k][4*n*(i+1)+4*(j-1)+3])))]

#for k in range(timeout+1):
#    for j in range(n-1):
#        for i in range(1,n):
#            Fs += [  Or(Not(P[k][4*n*i+4*j]),And(Not(P[k][4*n*(i-1)+4*(j+1)+1]),Not(P[k][4*n*(i-1)+4*(j+1)+3])))]

# The mine stays at the same place
for k in range(timeout):
    for i in range(n):
        for j in range(n):
            Fs += [Or(Not(P[k][4*n*i+4*j+2]),P[k+1][4*n*i+4*j+2])]
            Fs += [Or(P[k][4*n*i+4*j+2],Not(P[k+1][4*n*i+4*j+2]))]

for k in range(timeout):
    moves = []
    # Vertical Moves
    for i in range(n-2):  
        for j in range(n):
            #temp = If(P[k][4*n*i+4*j], And(Not(P[k+1][4*n*i+4*j]), P[k+1][4*n*(i+1)+4*j]), Not(And(Not(P[k+1][4*n*i+4*j]), P[k+1][4*n*(i+1)+4*j])))
            temp = And(P[k][4*n*i+4*j], And(Not(P[k+1][4*n*i+4*j]), P[k+1][4*n*(i+1)+4*j]))
            moves.append(temp)
    for i in range(1, n-1):  
        for j in range(n):
            # temp = If(P[k][4*n*i+4*j], And(Not(P[k+1][4*n*i+4*j]), P[k+1][4*n*(i-1)+4*j]), Not(And(Not(P[k+1][4*n*i+4*j]), P[k+1][4*n*(i-1)+4*j])))
            temp = And(P[k][4*n*i+4*j], And(Not(P[k+1][4*n*i+4*j]), P[k+1][4*n*(i-1)+4*j]))
            moves.append(temp)

    # Horizontal Moves
    for i in range(n):  
        for j in range(n-2):
            #temp = If(P[k][4*n*i+4*j+1], And(Not(P[k+1][4*n*i+4*j+1]), P[k+1][4*n*i+4*(j+1)+1]), Not(And(Not(P[k+1][4*n*i+4*j+1]), P[k+1][4*n*i+4*(j+1)+1])))
            temp = And(P[k][4*n*i+4*j+1], And(Not(P[k+1][4*n*i+4*j+1]), P[k+1][4*n*i+4*(j+1)+1]))
            moves.append(temp)

    for i in range(n):
        for j in range(1, n - 1):  
            #temp = If(P[k][4*n*i+4*j+1], And(Not(P[k+1][4*n*i+4*j+1]), P[k+1][4*n*i+4*(j-1)+1]), Not(And(Not(P[k+1][4*n*i+4*j+1]), P[k+1][4*n*i+4*(j-1)+1])))
            temp = And(P[k][4*n*i+4*j+1], And(Not(P[k+1][4*n*i+4*j+1]), P[k+1][4*n*i+4*(j-1)+1]))
            moves.append(temp)

    # For the red car
    for i in range(n):
        for j in range(n-2):
            # temp = If(P[k][4*n*i+4*j+3], And(Not(P[k+1][4*n*i+4*j+3]), P[k+1][4*n*i+4*(j+1)+3]), Not(And(Not(P[k+1][4*n*i+4*j+3]), P[k+1][4*n*i+4*(j+1)+3])))
            temp = And(P[k][4*n*i+4*j+3], And(Not(P[k+1][4*n*i+4*j+3]), P[k+1][4*n*i+4*(j+1)+3]))
            moves.append(temp)

    for i in range(n):
        for j in range(1, n - 1):  
            #temp = If(P[k][4*n*i+4*j+3], And(Not(P[k+1][4*n*i+4*j+3]), P[k+1][4*n*i+4*(j-1)+3]), Not(And(Not(P[k+1][4*n*i+4*j+3]), P[k+1][4*n*i+4*(j-1)+3])))
            temp = And(P[k][4*n*i+4*j+3], And(Not(P[k+1][4*n*i+4*j+3]), P[k+1][4*n*i+4*(j-1)+3]))
            moves.append(temp)
    Fs += [PbEq([(x, 1) for x in moves], 1)]
    #temp = And(P[0][4*n*1+4*0+3], And(Not(P[0+1][4*n*1+4*0+3]), P[0+1][4*n*1+4*(0+1)+3]))
    #print(Fs)


#for k in range(timeout + 1):
#	temp = [ ]
#	for i in range(4 * n * n):
#		temp.append(P[k][i])
#	Fs.append(PbEq([(x,1) for x in temp], cars))

#for k in range(timeout):
#	temp = []
#	for i in range(4 * n * n):
#		temp.append(Xor(P[k][i], P[k + 1][i]))
#	Fs.append(PbEq([(x,1) for x in temp], 2))



#Goal Clause
temp = []
for k in range(timeout+1):
    temp.append(P[k][4*n*i0+4*(n-2)+3])

Fs += [PbGe([(x,1) for x in temp], 1)]



s = Solver()
s.add(Fs)
# check sat value
result = s.check()

if result == sat:
    # get satisfying model
    m = s.model()

    # print only if value is true
    # print (sorted ([(d, m[d]) for d in m], key = lambda x: str(x[0]))

    for i in range(timeout+1):
        for j in range(n*n*4):
            print(str(P[i][j])+str(m.eval(P[i][j])))

    # xor_list = []
    # for i in range(1,timeout+1):
    #     xor = []
    #     for j in range(n*n*4):
    #         xor.append( is_true(m[P[i][j]])^ is_true(m[P[i-1][j]])) 
    #     print(xor)
    #     xor_list.append(xor)

    # print(xor_list)
    # y = False
    # x = True
    # print(x^y)
    # print(is_true(m[P[1][35]]))
    print("SAT")

else:
    print("UNSAT")
