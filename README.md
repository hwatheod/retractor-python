Retractor-Python
================

This repository consists of utilities written in Python related to retrograde analysis
chess problems. A full web application for retrograde analysis can be found at the repository
[retractor](https://github.com/hwatheod/retractor).

cages
-----

The utility `cages` is a prototype implementation of an algorithm for verifying cages
described in [this article](/doc/cages.pdf) in this repository. The file `test_cages.txt` has a sample input file that can be run with
`python3 cages.py < test_cages.txt`

The output looks like this:

```
8/8/8/8/8/8/PPkPP3/KR1b4 True 
7K/pppp1ppp/4p3/8/8/8/8/8 True 
4B1rk/3ppKpp/8/8/8/8/8/8 True 
4Bnrk/3ppK1p/4p1p1/8/8/8/8/8 True 
2K2b2/1p1pppp1/1pp5/8/8/8/8/8 True 
8/8/8/8/8/8/PPPPPPPP/2B1RK2 False e1-d1 f1-g1 d1-e1 e1-f1 g1-e1
8/8/8/8/8/8/PPPPPPPP/KR3B2 False b1-c1 a1-b1 c1-d1 b1-c1 c1-e1
8/8/8/8/8/5P2/4PrPP/7K False f2-f1 f1-b1 h1-g1 f3-f2 g1-f1 f1-e1
8/8/8/8/8/8/6PP/6Nr True 
```
Each output line repeats the Forsythe notation for the position. This is followed by `True` if the
position was verified as a cage, or `False` if it was not verified (which suggests, but does not prove, 
that the position is not a cage). If verification failed, a sequence of retractions is given that leads to
a home position or the maximum depth. This should give some idea of why the program thinks the position
is not a cage.

Details on the input: It consists of lines in the following form:

`position key1=value1 key2=value2 ...`

The positions are evaluated in order, so once a cage is successfully verified, it is
used in the analysis of later cages in the input.

`position` should be in Forsythe notation with English symbols K, Q, R, B, N, P.

The following keys are valid as additional parameters. However, for most problems, they are not needed.

`zone` The list of squares to add to the zone in addition to the default, which is the set of occupied squares
and the squares that are a king's move from an occupied square. The value should be a comma separated
list of squares in algebraic notation with no spaces. For example: `zone=a1,b3,c4`. For most problems, the
default zone is sufficient.

`depth` The maximum search depth before terminating with failure. The value should be a
positive integer. For example: `depth=10`. For most problems, the default depth of 20 is more than
sufficient.

`frozen` The list of pieces to be marked as frozen in the position. Frozen pieces cannot be moved.
The square must contain the piece that occupies that square in the initial array.  The value should be a comma separated
list of squares in algebraic notation with no spaces. For example: `zone=e1,f1`. Most problems
will not have frozen squares.

