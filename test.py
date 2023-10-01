x = [1,2,3,1,1,3,1,1]
num_count = {}
# num_count = {
#                 1 : 3,
#                 2 : 0,
#                 3 : 1,
#         }

# output = 4

for i in range(len(x)):
    for j in range(len(x)):
        if x[i] == x[j] and i < j:
            if num_count.get(x[i]):
                num_count[x[i]] = num_count[x[i]] +  [(i,j)]
            else:
                num_count[x[i]] =  [(i,j)]

print(num_count)

c = 0
for values in num_count:
    if values:
        c += len(num_count[values])

print(c)
        
# for num in x:
#     if num in num_count:
#         num_count[num] += 1
#     else:
#         num_count[num] = 1
    
# print(num_count) # { 1: 3, 2: 1, 3: 2 }
# idp = 0
# print(num_count.values())
# for count in num_count.values():
#     idp += (count * (count - 1)) /2 
# print(idp)
