# Finite State Machine Generator for C

(c) 2017 by Matthias Arndt <marndt@asmsoftware.de>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE

## Abstract
This is a generator tool for finite state machines(see also https://en.wikipedia.org/wiki/Finite-state_machine).
It generates C code from a transition table entered in OpenDocument format.

The intention is to ease and speedup implementation of finite state machines
in software for small scale embedded systems with STM8, AVR, MSP430 or similar
microcontrollers.

The software uses ODSReader Copyright 2011 by Marco Conti.

## System requirements

- Python
- Odfpy (Package python-odf for Ubuntu Linux)
- suitable input data in OpenDocument table format

## Command line options

$ gen-fsm-simple <odsfile> <sheetname>

## Input format

## Name of the generated finite state machine

The given sheetname is converted to a C identifier, e.q. all characters 
except A-Z, a-z, 0-9 and _ are removed.

This denotes the $NAME of the generated state machine. It is used for
- identifying the function to handle state transitions, `$NAME_Fsm`
- internal data types, e.q. available states, `$NAME_states`
- destination filenames

Example for name "C&a#r" will generate `Car_Fsm` and `Car_states` identifiers.

## Generated files

Two files are generated, `$NAME_fsm.c` containing the transition logic and
`$NAME_.h` containing the API.

## User provided implmentations

The user must provide the actual implementation for state behaviour.

For each state, an entry, exit and "in state" function is to be provided.
- The entry function is called upon entry into the state.
- The "inside state" function is always exectued beore conditions for any state transitions are checked.
- The exit function is called upon leaving a certain state on transitions.

It is recommend to implement these in their own C file, `$NAME_fsm.c`

## Events

Events trigger state transitions. Each event is provided as a boolean function.
A true result leads to a state change.

## Variants

Multiple generators are provided.

- The simple variant provides a single instance state machine with classic switch-case implementation. 
State variables are static inside the transition function.
- The OOP variant works with pointers to a structure. For each event and state handling function, a pointer to a `$NAME_t` struct is passed.
The structure itself is not implemented by the generator, it is an abstract type.
The user must provide an implementation while implementing the state handling functions. This variant uses a table of function pointers for the transition function.
