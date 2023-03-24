import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time
import random
from collections import defaultdict


class BTSolver:
    '''
    BTSolver class using backtracking with a consistencyCheck function, a variable selection hueristic, and a value selection huerestic 
    in order to attempt to solve the given sudoku board (represented as ConstraintNetwork)
    '''

    def __init__(self, gb, trail, val_sh, var_sh, cc):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc


    # Basic consistency check, no propagation done
    def assignmentsCheck(self):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True
    
    '''
    Norvig check used for consistency and constraint checking
    Will check if any neighbors of an assigned value have that value, and will remove it.
    Will also check if any value in a constraint has only one possible variable it can be assigned to, and assigns it.
    Will call updateneighbors recursively at it assigned values to variables with domain 1.
    Returns a dictionary of modified values, and a boolean stating whether it is valid assignment or not
    '''
    def norvigCheck(self):
        #keeps track of which variables were assigned in the function
        assignedDict = dict()

        check_list = self.network.getVariables()

        for modified in check_list:
            if not modified.isAssigned():
                continue
            
            if not self.updateNeighbors(modified,assignedDict):
                return (assignedDict,False)

        #each unit is a row, column or block
        for unit in self.network.getConstraints():
            countDict = dict()

            #for each block in the respective unit, if not assigned then add all its possible values
            #to the counterDict
            conCount = 0
            for variable in unit.vars:
                if variable.isAssigned():
                    continue
                conCount += 1
                
                for value in variable.getValues():
                    if value in countDict:
                        countDict[value][0] += 1
                        countDict[value][1].append(variable)
                    else:
                      countDict[value] = [1,[variable]]

            #checking if there is a variable that isn't in any square in the constraint
            if len(countDict) < conCount:
                return (assignedDict,False)
            
            #checking if there is a value that can be only in on square, assigns it
            for value, (occurence,variables) in countDict.items():
                if occurence != 1:
                    continue
                
                #assigning  value to the variable
                assigned = variables[0]
                self.trail.push(assigned)
                assigned.assignValue(value)
                assignedDict[assigned] = value

                self.updateNeighbors(assigned,assignedDict)

        return (assignedDict, True)

    '''
    Updates the neighbors of an assigned variable, passing assignedDict by reference so it persists through all calls
    '''
    def updateNeighbors(self, variable,assignedDict):
        
        neighbors = self.network.getNeighborsOfVariable(variable)
        assigned_val = variable.getAssignment()

        #checks all neighbors for same value as assigned variable
        for neighbor in neighbors:
            if neighbor.isAssigned():
                continue
            
            #removes value from neighbor's domain
            if assigned_val in neighbor.getValues():
                self.trail.push(neighbor)
                neighbor.removeValueFromDomain(assigned_val)
            
            #if only one value left in neighbor's domain, then assign it and recursively call updateneighbors again
            if neighbor.size() == 1:
                neighbor.assignValue(neighbor.getValues()[0])
                assignedDict[neighbor] = neighbor.getAssignment()
                if not self.updateNeighbors(neighbor,assignedDict):
                    return False
            
            #return early if invalid configuration found
            if neighbor.size() == 0:
                return False
        
        return True


    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable(self):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
    MAD: Minimum remaining values with degree tiebreaker.
    Returns the list of all the variables with the smallest amount of values left, using degree as a tiebreaker.
    """

    def MRVwithTieBreaker(self):

        # return a list of all the variables with the smallest domain
        checklist = self.network.getVariables()
        smallest_domain_length = float("inf")


        small_list_domains = []
        for var in checklist:
            if var.isAssigned():
                continue
            
            #if variable found with smaller amount of values left, make a new list with it in it
            if len(var.getValues()) < smallest_domain_length:
                small_list_domains = [var]
                smallest_domain_length = len(var.getValues())
            #if vairable with equally smallest, add to list
            elif len(var.getValues()) == smallest_domain_length:
                small_list_domains.append(var)

        #taking degree counts of the list of the variables with the smallest domain as a tiebreaker
        degree_counts = [0]*len(small_list_domains)

        for index, candidate in enumerate(small_list_domains):
            #counts unassigned neighbors only
            for c_neighbor in self.network.getNeighborsOfVariable(candidate):
                if not c_neighbor.isAssigned():
                    degree_counts[index] += 1

        #case of no more variables left
        if not degree_counts: return [None]

        #filters out those that don't have the max degree count
        max_degree = max(degree_counts)
        return_list = []
        for i in range(len(degree_counts)):
            if degree_counts[i] == max_degree:
                return_list.append(small_list_domains[i])

        return return_list


    # Default Value Ordering
    def getValuesInOrder(self, v):
        values = v.domain.values
        return sorted(values)

    """
    LCV: Least constrining Value hueristic. Chooses the value of the current selected variable that would affect the least number
    of other neighbors.
    """

    def getValuesLCVOrder(self, v):

        degree_dict = defaultdict(int)

        for value in v.getValues():

            degree_dict[value]

            for n in self.network.getNeighborsOfVariable(v):
                if value in n.getValues():
                    degree_dict[value] += 1

        return sorted(degree_dict.keys(), key=lambda x: degree_dict[x])

    """
    Backtracking search algorithm
    """
    def solve(self, time_left=600):
        if time_left <= 60:
            return -1

        start_time = time.time()
        if self.hassolution:
            return 0

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if (v == None):
            # Success
            self.hassolution = True
            return 0

        # Attempt to assign a value
        for i in self.getNextValues(v):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push(v)

            # Assign the value
            v.assignValue(i)

            # Propagate constraints, check consistency, recur
            if self.checkConsistency():
                elapsed_time = time.time() - start_time
                new_start_time = time_left - elapsed_time
                if self.solve(time_left=new_start_time) == -1:
                    return -1

            # If this assignment succeeded, return
            if self.hassolution:
                return 0

            # Otherwise backtrack
            self.trail.undo()

        return 0

    def checkConsistency(self):
        return self.norvigCheck()[1]


    def selectNextVariable(self):
        return self.MRVwithTieBreaker()[0]


    def getNextValues(self, v):
        return self.getValuesLCVOrder(v)

    def getSolution(self):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)
