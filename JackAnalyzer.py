import shlex
import sys

"""
The below section strips comments from a .jack file
"""

f = open(sys.argv[1],'r') #read .jack file from command line

fname = sys.argv[1] #name of file

if '.' in fname:#determine name of output file
    w = fname.index('.')
    z = fname[:w]
    onameT = z + 'T.xml' #output file from tokenizer
    oname = z + '.xml' #add .xml extension

cr = "no-comments"

wrlist = [] #wrlist = whitespace removed list

for i in f.readlines():
    m = i.strip() #for each line in the file, strip away leading and trailing whitespace characters
    
    if m:#if the line is not blank
        line = str(m)
        wrlist.append(line) #add to whitespace removed list
        
wrclist = [] #wrclist = whitespace and comments removed list

input = '' #input will be a string of elements from the .jack file

if(cr == "no-comments"):#if no-comments command was passed from command line
    for item in wrlist: #for each item in the whitespace removed list
        if '//' in item: #test to see comments are present
            value = item.index('//') #if they are, find where by searching for the index
            newItem = item[:value] #splice off contents beginning with double backslash
            wrclist.append(newItem) #add output to no comments list

        elif '/**' in item: #test to see comments are present
            value = item.index('/**') #if they are, find where by searching for the index
            newItem = item[:value] #splice off contents beginning with double backslash
            wrclist.append(newItem) #add output to no comments list
        elif item.startswith('*'):
            value = item.index('*') #if they are, find where by searching for the index
            newItem = item[:value] #splice off contents beginning with double backslash
            wrclist.append(newItem) #add output to no comments list
        
        else: #no double backslash present
            wrclist.append(item) #no comments to remove, add to wrclist
        
    
        
    for j in wrclist: #for everything in the no comments list 
        if j:
            input = input + j

f.close()

"""
The below section runs the code with comments removed through the tokenizer
"""

fout = open(oname,'w') #this will be the .xml file we end up writing to

y = input.replace('(',' ( ').replace(')',' )').replace('{',' { ').replace('}',' } ').replace('=',' = ').replace(';',' ; ').replace('&',' & ').replace('<',' < ').replace('/',' / ')
z = y.replace('[',' [ ').replace(']',' ] ').replace('.',' . ').replace(',',' , ').replace('+',' + ').replace('-',' - ').replace('*',' * ').replace('>',' > ').replace('|',' | ').replace('~',' ~ ')

values = list(iter(shlex.shlex(z).get_token, '')) #values is turned into a list of elements

#Below is a list of keywords
kwList = ['class','constructor','function','method','field','static','var','int','char','boolean','void',
          'true','false','null','this','let','do','if','else','while','return']

#Below is a list of symbols
symList = ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']

#Below is a range of integers that could make up an integer constant
intcList = range(32768)

#Below is a function that returns the tokenType of a given input
def tokenType(inp):
    
    if(inp in kwList):
        return 'keyword'
    elif(inp in symList):
        return 'symbol'
    elif(inp.isdigit()):
        if(int(inp) in intcList):
            return 'integerConstant'
    elif(inp.startswith('"')):
        return 'stringConstant'
    else:
        return 'identifier'

tokens = list() #tokens will be a list of tokens in the form <xxx> terminal </xxx>

tokens.append('<tokens>') 

for i in values:
    if(i == '<'): #handle unique case where '<' is expressed as '&lt;'
        output = '  <' + tokenType(i) + '> ' + '&lt;' + ' </' + tokenType(i) + '>'
    elif(i == '>'): #handle unique case where '>' is expressed as '&gt;'
        output = '  <' + tokenType(i) + '> ' + '&gt;' + ' </' + tokenType(i) + '>'
    elif(i == '&'): #handle unique case where '&' is expressed as '&amp;'
        output = '  <' + tokenType(i) + '> ' + '&amp;' + ' </' + tokenType(i) + '>'
    elif(tokenType(i) == 'stringConstant'): #remove double quotes in a string constant
        j = i.replace('"','').replace(' ','')
        output = '  <' + tokenType(i) + '> ' + j + ' </' + tokenType(i) + '>'
    else:
        output = '  <' + tokenType(i) + '> ' + i + ' </' + tokenType(i) + '>'
        
    tokens.append(output.strip()) #tokens contains all of the tokens

fTokens = open(onameT,'w') #tokenizer .xml output

for each in tokens:
    fTokens.write(each + '\n') #write to tokenizer .xml file

fTokens.write('</tokens>') #include trailing </tokens>

fTokens.close() #close the file

operators = ['<symbol> + </symbol>','<symbol> - </symbol>','<symbol> * </symbol>','<symbol> / </symbol>',
             '<symbol> &amp; </symbol>','<symbol> | </symbol>','<symbol> &lt; </symbol>','<symbol> &gt; </symbol>',
             '<symbol> = </symbol>','<symbol> ~ </symbol>']

'''
#The below section contains all of the compilexxx() statements
'''

def isStatement(token): #determine if the token is a statement
    
    if(token == '<keyword> let </keyword>'):
        return True
    elif(token == '<keyword> if </keyword>'):
        return True
    elif(token == '<keyword> while </keyword>'):
        return True
    elif(token == '<keyword> do </keyword>'):
        return True
    elif(token == '<keyword> return </keyword>'):
        return True
    else:
        return False

def CompileClass(tks): #receives list of tokens as an argument
    
    fout.write('<class>\n')
    
    index = 0 #initialize index to 0
    
    if(tks[index] == '<tokens>'): #advance past token header
        index = index + 1
    
    fout.write(tks[index]+'\n') #prints 'class'
    index = index + 1
    fout.write(tks[index]+'\n') #prints 'className'
    index = index + 1
    fout.write(tks[index]+'\n') #prints '{'
    index = index + 1
    
    #handles classVarDec
    while((tks[index] == '<keyword> static </keyword>') | (tks[index] == '<keyword> field </keyword>')):
        
        index = CompileClassVarDec(tks,index)
        
    #handles subroutineDec    
    while((tks[index] == '<keyword> constructor </keyword>') | (tks[index] == '<keyword> function </keyword>') | (tks[index] == '<keyword> method </keyword>')):
        
        index = CompileSubroutine(tks,index)
    
    fout.write(tks[index]+'\n') #prints '}'
    index = index + 1
    
    fout.write('</class>\n') #closing '</class>'
        
    
def CompileClassVarDec(tks,index): #compiles class variable declarations
    
    fout.write('<classVarDec>\n')
    
    fout.write(tks[index]+'\n') #prints 'static' or 'field'
    index = index + 1
    fout.write(tks[index]+'\n') #prints type
    index = index + 1
    fout.write(tks[index]+'\n') #prints varName
    index = index + 1
    
    while(tks[index] == '<symbol> , </symbol>'): #prints ', varName' as many times as necessary
        
        fout.write(tks[index]+'\n')
        index = index + 1
        fout.write(tks[index]+'\n')
        index = index + 1
    
    fout.write(tks[index]+'\n') #prints closing ';'
    index = index + 1
    
    fout.write('</classVarDec>\n')
    
    return index

def CompileSubroutine(tks,index): #handles subroutine compilation
    
    fout.write('<subroutineDec>\n')
    
    fout.write(tks[index]+'\n') #prints constructor or function or method
    index = index + 1
    fout.write(tks[index]+'\n') #prints void / type
    index = index + 1
    fout.write(tks[index]+'\n') #prints subroutine name
    index = index + 1
    fout.write(tks[index]+'\n') #prints '('
    index = index + 1
    
    if(tks[index] == '<symbol> ) </symbol>'): #handles situation where parameter list is empty
        fout.write('<parameterList>\n')
        fout.write('</parameterList>\n')
        fout.write(tks[index]+'\n') #prints )
        index = index + 1
    else: #parameter list is not empty, handle compilation of ParameterList
        index = compileParameterList(tks,index)
        
        fout.write(tks[index]+'\n') #this should be ')'
        index = index + 1
        
    fout.write('<subroutineBody>\n')
        
    fout.write(tks[index]+'\n') #print '{'
    index = index + 1
    
    while(tks[index] == '<keyword> var </keyword>'):
        index = compileVarDec(tks,index)
    
    while(isStatement(tks[index])):
        index = compileStatement(tks,index)
    
    fout.write(tks[index]+'\n') #print '}' at end of subroutine body
    index = index + 1
    
    fout.write('</subroutineBody>\n')
    
    fout.write('</subroutineDec>\n')
    
    return index

def compileParameterList(tks,index):
    
    fout.write('<parameterList>\n')
    
    fout.write(tks[index]+'\n') #prints type
    index = index + 1
    fout.write(tks[index]+'\n') #prints varName
    index = index + 1
    
    while(tks[index] == '<symbol> , </symbol>'):
        fout.write(tks[index]+'\n') #prints ,
        index = index + 1
        fout.write(tks[index]+'\n') #prints type
        index = index + 1
        fout.write(tks[index]+'\n') #prints varName
        index = index + 1
    
    
    fout.write('</parameterList>\n')
    
    return index

def compileVarDec(tks,index):
    
    fout.write('<varDec>\n')
    
    fout.write(tks[index]+'\n') #print var
    index = index + 1
    fout.write(tks[index]+'\n') #print type
    index = index + 1
    fout.write(tks[index]+'\n') #print varName
    index = index + 1
    
    while(tks[index] == '<symbol> , </symbol>'):
        fout.write(tks[index]+'\n')
        index = index + 1
        fout.write(tks[index]+'\n')
        index = index + 1
        
    fout.write(tks[index]+'\n')
    index = index + 1
    
    
    fout.write('</varDec>\n')
    
    return index

def compileStatement(tks,index): 
    
    fout.write('<statements>\n')
    
    while(isStatement(tks[index])): #redirects compilation to appropriate statement compilation type
    
        if(tks[index] == '<keyword> do </keyword>'):
            index = compileDo(tks,index)
        elif(tks[index] == '<keyword> let </keyword>'):
            index = compileLet(tks,index)
        elif(tks[index] == '<keyword> while </keyword>'):
           index = compileWhile(tks,index)
        elif(tks[index] == '<keyword> return </keyword>'):
            index = compileReturn(tks,index)
        else:
            index = compileIf(tks,index) 
            
    fout.write('</statements>\n')
    
    return index  

def compileIf(tks,index):
    
    fout.write('<ifStatement>\n')
    
    fout.write(tks[index]+'\n') #prints if
    index = index + 1
    fout.write(tks[index]+'\n') #prints (
    index = index + 1
    index = CompileExpression(tks,index)
    fout.write(tks[index]+'\n') #prints )
    index = index + 1
    fout.write(tks[index]+'\n') #prints {
    index = index + 1
    index = compileStatement(tks,index)
    fout.write(tks[index]+'\n') #prints }
    index = index + 1
    
    if(tks[index] == '<keyword> else </keyword>'):
        fout.write(tks[index]+'\n') #prints else
        index = index + 1
        fout.write(tks[index]+'\n') #prints {
        index = index + 1
        index = compileStatement(tks,index)
        fout.write(tks[index]+'\n')
        index = index + 1
    
    fout.write('</ifStatement>\n')
    
    return index

def compileWhile(tks,index):
    
    fout.write('<whileStatement>\n')
    
    fout.write(tks[index]+'\n') #prints while
    index = index + 1
    fout.write(tks[index]+'\n') #prints (
    index = index + 1
    index = CompileExpression(tks,index)
    fout.write(tks[index]+'\n') #prints )
    index = index + 1
    fout.write(tks[index]+'\n') #prints {
    index = index + 1
    index = compileStatement(tks,index)
    fout.write(tks[index]+'\n') #prints }
    index = index + 1
    
    fout.write('</whileStatement>\n')
    
    return index


    
def compileDo(tks,index):
    
    fout.write('<doStatement>\n')
    
    fout.write(tks[index]+'\n') #prints 'do'
    index = index + 1
    
    while((tks[index] == '<symbol> ( </symbol>') is False):
        fout.write(tks[index]+'\n')
        index = index + 1
        
    fout.write(tks[index]+'\n') #prints opening (
    index = index + 1
    
    index = CompileExpressionList(tks,index)
    
    fout.write(tks[index]+'\n') #prints closing )
    index = index + 1
    
    fout.write(tks[index]+'\n') #prints ';'
    index = index + 1
    
    fout.write('</doStatement>\n')
    
    return index

def compileReturn(tks,index):
    
    fout.write('<returnStatement>\n')
    
    fout.write(tks[index]+'\n') #prints return
    index = index + 1
    
    if(tks[index] == '<symbol> ; </symbol>'):
        fout.write(tks[index] + '\n') #prints ;
        index = index + 1
    else: #there's a value to return (expressionless for now)
        index = CompileExpression(tks,index)
        fout.write(tks[index]+'\n') #prints ;
        index = index + 1
        
    fout.write('</returnStatement>\n')
    
    return index

def compileLet(tks,index):
    
    fout.write('<letStatement>\n')
    
    fout.write(tks[index]+'\n') #prints let
    index = index + 1
    
    fout.write(tks[index]+'\n') #prints varName
    index = index + 1
    
    if(tks[index] == '<symbol> [ </symbol>'):
        fout.write(tks[index]+'\n') #prints [
        index = index + 1
        index = CompileExpression(tks,index)
        fout.write(tks[index]+'\n') #prints ]
        index = index + 1
        fout.write(tks[index]+'\n') #prints =
        index = index + 1
        index = CompileExpression(tks,index)
        fout.write(tks[index]+'\n') #prints ;
        index = index + 1
    else:
        fout.write(tks[index]+'\n') #prints =
        index = index + 1
        index = CompileExpression(tks,index)
        fout.write(tks[index]+'\n') #prints ;
        index = index + 1
        
    fout.write('</letStatement>\n')
    
    return index

def CompileExpressionList(tks,index):

    fout.write('<expressionList>\n')
    
    while((tks[index] == '<symbol> ) </symbol>') is False): #while the expression list is not empty
        if(tks[index] == '<symbol> , </symbol>'): #more than one expression in list
            fout.write(tks[index]+'\n')
            index = index + 1
        index = CompileExpression(tks,index)
    
    fout.write('</expressionList>\n')
    
    return index
    
def CompileExpression(tks,index):
    fout.write('<expression>\n') 
        
    index = CompileTerm(tks,index) 
    
    while(tks[index] in operators):
        fout.write(tks[index]+'\n') #print operator
        index = index + 1
        index = CompileTerm(tks,index)
        
    fout.write('</expression>\n')
        
    return index

def CompileTerm(tks,index):
    
    fout.write('<term>\n') #print <term>
    
    if((tks[index] == '<symbol> - </symbol>') | (tks[index] == '<symbol> ~ </symbol>')): #handle unary operator
        fout.write(tks[index]+'\n')
        index = index + 1
        index = CompileTerm(tks,index)
        
        fout.write('</term>\n')
        
        return index
    
    if(tks[index] == '<symbol> ( </symbol>'): #handle unique case 1: '('
        fout.write(tks[index]+'\n') 
        index = index + 1
        index = CompileExpression(tks,index)
        fout.write(tks[index]+'\n') 
        index = index + 1
        
        fout.write('</term>\n')
        
        return index
    
    else:
    
        fout.write(tks[index]+'\n')
        index = index + 1 
    
        while(tks[index] == '<symbol> . </symbol>'): #subroutine call
            fout.write(tks[index]+'\n') #this prints .
            index = index + 1
            fout.write(tks[index]+'\n') #this prints new
            index = index + 1
            fout.write(tks[index]+'\n') #this prints (
            index = index + 1
            index = CompileExpressionList(tks,index)
            fout.write(tks[index]+'\n') #this prints )
            index = index + 1
        
        if(tks[index] == '<symbol> [ </symbol>'): #dealing with an array
            fout.write(tks[index]+'\n') #this prints [
            index = index + 1
            index = CompileExpression(tks,index)
            fout.write(tks[index]+'\n') #this prints ]
            index = index + 1
        
        fout.write('</term>\n')
    
        return index
    

CompileClass(tokens) #drive activity

fout.close() #close .xml file


    







    
   










