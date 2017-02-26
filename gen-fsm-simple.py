# needs odfpy, python-odf Ubuntu package
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

# generate valid C identifier from given input a-z 0-9 _
def gen_C_notation(input):
	allow = string.letters + string.digits + '_'
	return re.sub('[^%s]' % allow, '', input)

# function to return uniq entries into a list
def uniq(input):
  output = []
  for x in input:
    if x not in output:
      output.append(x)
  return output

# generate some constants
prefix = gen_C_notation(fsm_sheet)
c_file = prefix + ".c"
h_file = prefix + ".h"

print(" Prefix: " + prefix)

# find start of data/transition definition
tpos = 0
while (tpos < len(table)) and table[tpos][0] != "State":
	tpos += 1

tpos += 1

print tpos

# iterate row with transitions to find all states, conditionals and next states
states = []
trans = []
cond = []
while tpos < len(table):
	this_trans = []
	# collect states and conditions
	current_state = table[tpos][0]
	next_state = table[tpos][2]
	this_cond = table[tpos][1]
	if len(current_state) > 0:
		states.append(current_state)
		this_trans.append(current_state)
	if len(next_state) > 0:
		states.append(next_state)
		this_trans.append(next_state)
	# collect condition
	if len(this_cond) > 0:
		cond.append(this_cond)
		this_trans.append(this_cond)

	# only a valid transition if all entries are there
	if len(this_trans) == 3:
		trans.append(this_trans)

	# collect transitions until end of table
	tpos += 1

# create uniques for states and conditions
states = uniq(states)
cond = uniq(cond)

# generate header
f = open(h_file,'w')
f.write("/* API header for generated statemachine '" + prefix + "' */\n")
f.write("#ifndef " + prefix.upper() + "_H\n#define "+prefix.upper()+"_H\n")
f.write("#include <stdint.h>\n#include <stdbool.h>\n")

f.write("/** @brief enumeration of states */\n");
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
f.write("/* Generated statemachine '" + prefix + "' */\n")
f.write("#include <stdint.h>\n#include <stdbool.h>\n")
f.write("#include \""+h_file+"\"\n")

f.write("void "+main_func+"(void)\n{\n")

# prolog for initialisation
f.write("static uint8_t st = "+gen_C_notation(states[0])+";\n")
f.write("static bool inited = false;\n")
f.write("if(inited == false)\n{\n"+prefix+"_Enter_"+gen_C_notation(states[0])+"();\n")
f.write("inited = true;\n}\n")

# execute current state
f.write("/* todo: exectue in state function for selected state */\n")

# handle transitions
if len(trans) > 0:
	for i in trans:
		f.write("if((st == " + gen_C_notation(i[0])+ ") && (" +prefix+"_Ev_"+gen_C_notation(i[2]) + "() == true))\n{\n")
		f.write(prefix+"_Exit_"+gen_C_notation(i[0])+"();\n")
		f.write("st = "+gen_C_notation(i[1])+";\n")
		f.write(prefix+"_Enter_"+gen_C_notation(i[1])+"();\n")
		f.write("}\nelse\n");
# final clause
f.write("{\n/* nothing to do */\n}\n");

f.write("}\n");
f.write("\n");
f.close()

