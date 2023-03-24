#!/usr/bin/env python3

import sys
import os
import math
import SudokuBoard
import Constraint
import ConstraintNetwork
import BTSolver
import Trail
import time

"""
    Main file that interacts with the user.
"""


def main():
    # Important Variables
    file = ""
    var_sh = ""
    val_sh = ""
    cc = ""

    trail = Trail.Trail()

    #solving optimal combination of hueristics
    cc = "norvigCheck"
    val_sh = "LeastconstriningValue"
    var_sh = "MRVwithTieBreaker"
    sudokudata = userInputs()
    print(sudokudata)

    solver = BTSolver.BTSolver(sudokudata, trail, val_sh, var_sh, cc)
    if cc in ["forwardChecking", "norvigCheck", "tournCC"]:
        solver.checkConsistency()
    solver.solve()

    if solver.hassolution:
        print(solver.getSolution())
        print("Trail Pushes: " + str(trail.getPushCount()))
        print("Backtracks: " + str(trail.getUndoCount()))

    else:
        print("Failed to find a solution")

    return

def userInputs():
  print(
  """
  --------------------------------------------------------------------------------------------------------------------------------------------
  Welcome to the AI Sudoku Solver. Please enter the number of rows per group, columns per group, and number of given values and we'll solve it
  --------------------------------------------------------------------------------------------------------------------------------------------""")
  while True:
    m = input("\n# of rows per cell? ")
    try:
      m = int(m)
      assert m > 0
      break
    except:
      print("not a valid number, plese enter a positive integer.")

  while True:
    n = input("\n# of columns per cell? ")
    try:
      n = int(n)
      assert n > 0
      break
    except:
      print("not a valid number, please enter a positive integer.")
  
  while True:
    p = input("\n# values already given? ")
    try:
      p = int(p)
      assert 0 <= p < (m*n)**2
      break
    except:
      print(f"not a valid number, please enter a positive integer that is smaller than {(m*n)**2}")

  return SudokuBoard.SudokuBoard(m,n,p)

main()
