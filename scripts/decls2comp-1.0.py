#!/usr/bin/python3

# Converts a .decls file with comparability numbers to a file which is
# organized by variable comparability sets at each program point.
# This helps out with automating regression tests of DynComp.

# Created on 2005-05-13 by Philip J. Guo
# MIT CSAIL Program Analysis Group

# Input: .decls file with comparability numbers

# Output: A file which lists the comparability sets of all relevant
# variables at each program point, alphabetically sorted and separated
# by spaces.  All program points are also sorted by alphabetical
# order. Output is written to stdout by default

# Usage: ./decls2comp.py input.decls 'no-hashcodes' [optional]
# Running this with the 'no-hashcodes' string as the 2nd arg results
# in the tool ignoring all variables of rep. type 'hashcode' or
# 'hashcode[]', etc...

# Prog pt name
# All variable names in one comp set
# All variable names in another comp set
# ...
# <blank line>

# Input:

# DECLARE
# ..add():::ENTER
# a
# int # isParam=true
# int
# 1
# b
# int # isParam=true
# int
# 1
# c
# int # isParam=true
# int
# 2
# d
# int # isParam=true
# int
# -1

# Output:

# ..add():::ENTER
# a b
# c
# -1: d

# NOTE (2005-09-08): No longer does this anymore:
# Prints out a '-1: ' prefix in front of the special comparability set
# with a number of -1

# 2006-01-18: Added support for "INTERMEDIATE DECLARE" keyword
#             for the --dyncomp-print-inc option

import sys

# Note: Lackwit produces comparability numbers for arrays in the
# following format: '9[10]' - we are going to ignore what is between
# the brackets so we will treat it as '9'
import re

LWArrayRExp = re.compile("\[.\]")

ignoreHashcodes = False

if (len(sys.argv) == 3) and sys.argv[2] == "no-hashcodes":
    ignoreHashcodes = True

# If 'no-hashcodes' option is on, then ignore all variables whose
# rep. type is hashcode
hashcodeRE = re.compile("hashcode.*")


f = open(sys.argv[1], "r")

# Break each program point declaration up into separate lists.
# Program points are separated by "DECLARE" statements
# Key: program point name
# Value: list of all strings following program point
allPpts = {}

tempAllPpts = []  # Temporary before placing in allPpts

isIntermediate = 0

for line in f.readlines():
    line = line.strip()

    if line == "DECLARE":
        tempAllPpts.append([])  # Start a new list
        isIntermediate = 0
    elif line == "INTERMEDIATE DECLARE":
        tempAllPpts.append([])  # Start a new list
        isIntermediate = 1
    elif line != "" and line[0] != "#":  # Don't add blank lines & comments
        if len(tempAllPpts) > 0:
            tempAllPpts[-1].append(line)  # Append line to the latest entry


# Init allPpts from tempAllPpts
for pptList in tempAllPpts:
    # Allow duplicates by appending numeric indices onto program point
    # name
    index = 1

    pptName = pptList[0]

    # There is already an entry
    if pptList[0] in allPpts:
        # Try appending numbers until there isn't an entry
        found = 1
        while found:
            pptName = pptList[0] + " (" + str(index) + ")"
            if pptName not in allPpts:
                break
            index += 1

    allPpts[pptName] = pptList[1:]

# Alphabetically sort the program points
sortedPptKeys = sorted(list(allPpts.keys()))

# Process each PPT
for pptName in sortedPptKeys:
    v = allPpts[pptName]
    i = 0
    var2comp = {}  # Key: variable name, Value: comparability number

    # All info. about variables at a program point come in sets of 4
    # lines. e.g.
    #
    # a
    # int # isParam=true
    # int
    # 1
    while i < len(v):
        curRepType = v[i + 2]
        curComp = v[i + 3]

        if (not ignoreHashcodes) or (not hashcodeRE.match(curRepType)):
            isArrayMatch = LWArrayRExp.search(curComp)
            if isArrayMatch:
                var2comp[v[i]] = curComp[: isArrayMatch.start()]
            else:
                var2comp[v[i]] = curComp

        i += 4

    # Now we can do the real work of grouping variables together
    # in comparability sets based on their numbers
    sortedVars = sorted(list(var2comp.keys()))

    print(pptName)

    while len(sortedVars) > 0:
        varName = sortedVars[0]

        #        if var2comp[varName] == '-1': # Remember that everything is a string
        #            print '-1:', varName,
        #        else:
        print(varName, end=" ")

        compNum = var2comp[varName]

        if compNum:
            del var2comp[varName]

            sortedVars = sorted(list(var2comp.keys()))

            for otherVar in sortedVars:
                if var2comp[otherVar] == compNum:
                    print(otherVar, end=" ")
                    del var2comp[otherVar]
        print()

        # Update sortedVars after deleting the appropriate entries
        # from var2comp
        sortedVars = sorted(list(var2comp.keys()))

    print()
