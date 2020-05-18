import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """0
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        inconsistent_words = []
        for key in self.domains.keys():
            for val in self.domains[key]:
                if key.length != len(val):
                    inconsistent_words.append(val)
            for word in inconsistent_words:
                self.domains[key].remove(word)
            inconsistent_words=[]

        # raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision = False
        inconsistent_values = []
        overlap = self.crossword.overlaps[x,y]
        if overlap is not None:
            for v1 in self.domains[x]:
                flag = False
                for v2 in self.domains[y]:
                    if v2[overlap[1]] == v1[overlap[0]]:  
                        flag = True
                if not flag:
                    inconsistent_values.append(v1)
                    revision = True
            for val in inconsistent_values:
                self.domains[x].remove(val)
        return revision
        # raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            queue = self.generate_arcs()
        else:
            queue = arcs
        while len(queue) is not 0:
            (v1,v2) = queue.pop()
            is_revised = self.revise(v1,v2)
            if is_revised:
                if self.domains[v1] is None:
                    return False
                else:
                    for neighbor in self.crossword.neighbors(v1):
                        if neighbor is not v2:
                            queue.append((neighbor,v1))
        return True  
        # raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment:
                return False
        return True
        # raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for key in assignment.keys():
            if len(assignment[key]) != key.length:
                return False
            for var in self.crossword.neighbors(key):
                if var not in assignment:
                    continue
                overlap = self.crossword.overlaps[key,var]
                if assignment[key][overlap[0]]!= assignment[var][overlap[1]]:
                    return False 
        return True
        
        # raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the  list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        domain = list(self.domains[var])

        neighbor = self.crossword.neighbors(var)

        occurence_neighbor = [0 for i in range(len(domain)) ]
        i = 0
        for val in domain:
            for n in neighbor:
                if val in self.domains[n]:
                    occurence_neighbor[i]+=1
            i+=1
        
        domainx = [val for x,val in sorted(zip(occurence_neighbor,domain))]

        return domainx
        # raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_var =[]
        for var in self.crossword.variables:
            if var not in assignment:
                unassigned_var.append(var)
        min_domain = []
        min_domain.append(unassigned_var[0])
        for var in unassigned_var:
            if len(self.domains[var])<len(self.domains[min_domain[0]]):
                min_domain.clear()
                min_domain.append(var)
            elif len(self.domains[var])== len (self.domains[min_domain[0]]):
                min_domain.append(var)
        
        if len(min_domain) == 1 :
            return min_domain[0]

        max_degree_var = min_domain[0]
        for var in min_domain:
            if self.crossword.neighbors(var) > self.crossword.neighbors(max_degree_var):
                max_degree_var = var

        return max_degree_var
        # raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for val in self.order_domain_values(var,assignment):
            assignment[var] = val
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None :
                    return assignment
            assignment.pop(var)
        return None
        # raise NotImplementedError

    def generate_arcs(self):
        all_arcs = []
        for var in self.crossword.variables:
            neighbors = self.crossword.neighbors(var)
            for neighbor in neighbors:
                if (var,neighbor) not in all_arcs:
                    all_arcs.append((var,neighbor))
        return all_arcs

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
