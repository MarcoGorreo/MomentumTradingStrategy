possible_allocation_combinations_long = list(zip([round((i*0.10),2) for i in range(1,10)],[round((1 - i*0.10),2) for i in range(1,10)]))
possible_allocation_combinations_short = list(zip([round((i*0.10),2) for i in range(10,1,-1)],[round((1 - (i*0.10)),2) for i in range(10,1,-1)]))
test = [(i[1],i[0]) for i in possible_allocation_combinations_long]

print(possible_allocation_combinations_long)
print(possible_allocation_combinations_short)
print(test)