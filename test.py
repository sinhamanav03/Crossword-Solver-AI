from crossword import *
from generate import CrosswordCreator

crossword = Crossword('data\structure0.txt','data\words0.txt')

creator = CrosswordCreator(crossword)

for var in creator.crossword.variables:
    print(creator.domains[var])
    break

for val in creator.domains[var]:
    print(val)
# print(creator.domains)
# # print(crossword.words)
# creator.enforce_node_consistency()
# # arcs = creator.generate_arcs()
# # print(arcs)
# creator.ac3()
# print(creator.domains)

# doma = ['a','b','c']
# x = [2,1,3]
# doma = [y for x,y in sorted(zip(x,doma))]
# print(doma)