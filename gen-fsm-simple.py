# Finite State Machine Generator for C (simple switch-case variant)
# 
# (c) 2017 by Matthias Arndt <marndt@asmsoftware.de>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE
#
# needs odfpy, python-odf Ubuntu package
#
import ODSReader
import sys
from ODSReader import *
import string
import re

# basic inputs
ods_file = sys.argv[1]
fsm_sheet = sys.argv[2]

# parse .ods file with given sheet
doc = ODSReader(ods_file)
table = doc.getSheet(fsm_sheet)

# generate valid C identifier from given input A-Z a-z 0-9 _
def gen_C_notation(input):
	allow = string.letters + string.digits + '_'
	return re.sub('[^%s]' % allow, '', input)

# function to return uniq entries from a given list as a new list
def uniq(input):
  output = []
  for x in input:
    if x not in output:
      output.append(x)
  return output

# function to output a doxygen header
def doxygen(brief, details):
	output = "/**\n" + " * @brief " + brief +"\n * @details "+details+"\n */\n"
	return output

# generate some constants
prefix = gen_C_notation(fsm_sheet)
c_file = prefix + "_fsm.c"
h_file = prefix + "_fsm.h"

doxygen_entries = []

# find start of data/transition definition - and collect additional Doxygen entries
tpos = 0
while (tpos < len(table)) and table[tpos][0] != "State":
	if table[tpos][0].startswith("@"):
		this_dox = []
		this_dox.append(table[tpos][0])
		this_dox.append(table[tpos][1])
		doxygen_entries.append(this_dox)
	tpos += 1

tpos += 1

# iterate row with transitions to find all states, conditionals and next states
# lists of states, transitions and conditions are created
states = []
trans = []
cond = []
while tpos < len(table):
	this_trans = []
	# collect states and conditions
	current_state = table[tpos][0]
	this_cond = table[tpos][1]
	next_state = table[tpos][2]
	if len(current_state) > 0:
		states.append(current_state)
		this_trans.append(current_state)
	if len(this_cond) > 0:
		cond.append(this_cond)
		this_trans.append(this_cond)
	if len(next_state) > 0:
		states.append(next_state)
		this_trans.append(next_state)

	# only a valid transition if all entries are there
	if len(this_trans) == 3:
		trans.append(this_trans)

	# collect transitions until end of table
	tpos += 1

# create uniques for states and conditions
states = uniq(states)
cond = uniq(cond)

# print summary of data
print("Generated state machine '" + prefix + "'")
if len(doxygen_entries) > 0:
	for i in doxygen_entries:
		print(i[0]+" "+i[1])
print("Available states:")
for i in states:
	print(" - " + gen_C_notation(i))
print("Initial state: "+gen_C_notation(states[0]))
print("Available transitions:")
for i in trans:
	print(gen_C_notation(i[0]) + " --- "+gen_C_notation(i[1])+" ---> "+gen_C_notation(i[2]))

# generate header
f = open(h_file,'w')
f.write("/**\n")
f.write(" * API header for generated statemachine '" + prefix + "'\n")
f.write(" * Finite State Machine Generator for C, see https://github.com/simonsunnyboy/gen-fsm\n")
f.write(" * @file "+h_file+"\n")
if len(doxygen_entries) > 0:
	for i in doxygen_entries:
		f.write(" * "+i[0]+" "+i[1]+"\n")
f.write(" */\n")
f.write("#ifndef " + prefix.upper() + "_H\n#define "+prefix.upper()+"_H\n")
f.write("#include <stdint.h>\n#include <stdbool.h>\n")

f.write("/** @brief enumeration of states for statemachine '" + prefix + "' */\n");
f.write("enum "+prefix+"_states\n{\n");
for i in states:
	f.write(gen_C_notation(i)+",  /**< ... */\n")
f.write(prefix+"_MAX_NR_STATES   /**< ... */\n")
f.write("};\n");

f.write("/* main statemachine: */\n")
main_func = prefix+"_Fsm"
f.write("void "+main_func+"(void);\n")

f.write("/* event functions: */\n")
for i in cond:
	f.write("bool "+prefix+"_Ev_"+gen_C_notation(i)+"(void);\n")

f.write("/* state functions: */\n")
for i in states:
	f.write("void "+prefix+"_Enter_"+gen_C_notation(i)+"(void);\n")
	f.write("void "+prefix+"_Exit_"+gen_C_notation(i)+"(void);\n")
	f.write("void "+prefix+"_In_"+gen_C_notation(i)+"(void);\n")

f.write("#endif\n")
f.write("\n")
f.close()

#generate .c file
f = open(c_file,'w')
f.write("/**\n")
f.write(" * Generated statemachine '" + prefix + "'\n")
f.write(" * Finite State Machine Generator for C, see https://github.com/simonsunnyboy/gen-fsm\n")
f.write(" * @file "+c_file+"\n")
if len(doxygen_entries) > 0:
	for i in doxygen_entries:
		f.write(" * "+i[0]+" "+i[1]+"\n")
f.write(" */\n")
f.write("#include <stdint.h>\n#include <stdbool.h>\n")
f.write("#include \""+h_file+"\"\n\n")

dox_header=doxygen("transition function for finite state machine '" + prefix + "'","Call this function to evaluate conditions to trigger state changes and according behaviour.")
f.write(dox_header)
f.write("void "+main_func+"(void)\n{\n")

# prolog for initialisation
f.write("static uint8_t st = "+gen_C_notation(states[0])+";\n")
f.write("static bool inited = false;\n")
f.write("/* ensure init function for initial state is called: */\n")
f.write("if(inited == false)\n{\n"+prefix+"_Enter_"+gen_C_notation(states[0])+"();\n")
f.write("inited = true;\n}\n")

# state handler
f.write("/* transition handling by entry state: */\n")
f.write("switch(st)\n{\n")
# iterate states
for i in states:
	f.write("case "+gen_C_notation(i)+":\n");
	f.write(prefix+"_In_"+gen_C_notation(i)+"();\n")

	# iterate transitions for this state
	f.write("/* transitions from state '"+gen_C_notation(i)+"' to others: */\n")
	for t in trans:
		if(t[0] == i):
			f.write("if (" +prefix+"_Ev_"+gen_C_notation(t[1]) + "() == true)\n")
			f.write("{\n");
			f.write(prefix+"_Exit_"+gen_C_notation(i)+"();\n")
			f.write("st = "+gen_C_notation(t[2])+";\n")
			f.write(prefix+"_Enter_"+gen_C_notation(t[2])+"();\n")
			f.write("}\nelse\n");

	f.write("{\n/* no state change */\n}\n");
	f.write("break;\n");

# final clause
f.write("default:\n/* nothing to do */\nbreak;\n};");

f.write("return;\n }\n");
f.write("\n");
f.close()

