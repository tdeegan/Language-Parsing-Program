# Language-Parsing-Program

JackAnalyzer.py receives a .jack file (academic programming language) as a command-line argument.  It strips the Jack code of all white space and comments, and performs a lexical analysis.  Each token is classified as either a keyword, a symbol, an identifier, an integer constant, or a string constant.

The program then parses the list of tokens and attempts to match the tokens on the Jack language grammar.

The output produced is two .xml files (xxx.xml and xxxT.xml where xxx is the name of the Jack file).  xxxT.xml displays the classified list of tokens.  xxx.xml displays the entire syntactic structure of the Jack source code.  In practice, a TextComparer tool then verifies the validity of the syntactic structure against a sample output file.

The Jack language grammar does require a "look ahead" to the next token when situations of ambiguity arise.

A sample SquareGame.jack file is also present in this repository.
