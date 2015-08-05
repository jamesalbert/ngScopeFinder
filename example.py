from sys import argv
from os import listdir
from re import search, I

functions = {}
exemptNames = []

class font:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @staticmethod
    def funcName(s):
        return '%s%s%s' % (font.BOLD,s,font.END)

    @staticmethod
    def fileName(s):
        return '%s%s%s%s%s' % (font.UNDERLINE,font.BOLD,font.GREEN,s,font.END)

    @staticmethod
    def lineNumber(s):
        return '%s%s%s%s' % (font.BOLD,font.CYAN,s,font.END)

    @staticmethod
    def badName(s):
        return '%s%s%s%s' % (font.BOLD,font.RED,s,font.END)

    @staticmethod
    def underline(s):
        return '%s%s%s%s' % (font.UNDERLINE,font.YELLOW,s,font.END)

def findCtrlFunction(ctrl, line, lineNumber):
    jsSyntax = search('function\s(\w+)\(.*\)\s*\{', line)
    ngSyntax = search('scope\.(\w+)\s*=\s*function\(.*\)\s*\{', line, flags=I)
    variable = search('scope\.(\w+)\s*={1}\s*', line, flags=I)
    name, t = None, None
    if jsSyntax:
        name = jsSyntax.group(1)
        t = 'function'
    elif ngSyntax:
        name = ngSyntax.group(1)
        t = 'function'
    elif variable:
        name = variable.group(1)
        t = 'variable'
    if jsSyntax or ngSyntax or variable:
        if name in functions:
            return
        functions[name] = {
            'ctrl': font.fileName(ctrl),
            'lineNumber': font.lineNumber('line %s' % lineNumber),
            'type': t,
            'occurances': []
        }

def findDOMFunctionCall(fileName, line, lineNumber):
    jsSyntax = search('\son-\w+="(\w+)\(.*\)"', line)
    ngSyntax = search('\sng-(\w+)="(\w+)\(*.*\)*\s*\&{0,2}\s*(\w*)"', line)
    funcName, directive = None, None
    lineNumber = font.lineNumber('line %s' % lineNumber)
    if jsSyntax:
        funcName = jsSyntax.group(1)
    elif ngSyntax:
        directive = ngSyntax.group(1)
        funcName = ngSyntax.group(2)
    if jsSyntax or ngSyntax:
        if funcName not in functions:
            if directive in ['repeat']:
                exemptNames.append(funcName)
                return
            if funcName in exemptNames:
                return
            log_params = (font.underline('reference'), font.badName(funcName),
                          font.fileName(fileName), lineNumber)
            print '%s %s found in %s at %s not found in any controller' % log_params
        else:
            functions[funcName]['occurances'].append({
                'fileName': font.fileName(fileName),
                'lineNumber': font.lineNumber(lineNumber)
            })

def printLog():
    for funcName, function in functions.iteritems():
        for occurance in function['occurances']:
            logParams = (font.underline(function['type']), font.funcName(funcName), occurance['fileName'],
                         occurance['lineNumber'], function['ctrl'], function['lineNumber'])
            print '%s %s found in %s at %s is located in controller %s at %s' % logParams

def searchTemplates(path):
    for htmlFile in listdir('%s/templates' % path):
        with open('%s/templates/%s' % (path, htmlFile), 'r') as template:
            for i, line in enumerate(template.readlines()):
                if 'ng-' in line or 'on-' in line:
                    lineNumber = i+1
                    findDOMFunctionCall(htmlFile, line, lineNumber)
            template.close()

def searchJS(path, ctrl):
    with open('%s/js/controllers.js' % path, 'r') as controllers:
        for i, line in enumerate(controllers.readlines()):
            if 'function' not in line and '=' not in line:
                continue
            if '.controller' in line:
                m = search('.controller\((\'|")(\w+)(\'|")', line)
                ctrl = m.group(2)
                continue
            lineNumber = i+1
            findCtrlFunction(ctrl, line, lineNumber)
        controllers.close()

def main(path):
    currentCtrl = None;
    if path.endswith('/'):
        path = path[:-1]
    searchJS(path, currentCtrl)
    searchTemplates(path)
    printLog()
main(argv[1])
