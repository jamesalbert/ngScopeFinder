from os import listdir
from re import search, I
from .font import font

class ngApp(object):
    syntax = {
        'jsfunction': 'function\s(?P<function>\w+)\(.*\)\s*\{',
        'ngfunction': 'scope\.(?P<function>\w+)\s*=\s*function\(.*\)\s*\{',
        'ngvariable': 'scope\.(?P<variable>\w+)\s*={1}\s*',
        'jsdom': '\son-\w+="(?P<reference>\w+)\(.*\)"',
        'ngdom': '\sng-(?P<directive>\w+)="(?P<reference>\w+)\(*.*\)*\s*\&{0,2}\s*(\w*)"'
    }
    def __init__(self, path):
        if path.endswith('/'):
            path = path[:-1]
        self.path = path
        self.ctrl = None
        self.line = None
        self.lineNumber = None
        self.fileName = None
        self.functions = {}
        self.exemptNames = []

    def run(self):
        self.searchCtrl()
        self.searchTemplates()
        self.printLog()

    def testJSSyntax(self, lang, t):
        s = search(ngApp.syntax[lang+t], self.line, flags=I)
        if not s or s.group(t) in self.functions:
            return None
        name = s.group(t)
        self.functions[name] = {
            'ctrl': font.fileName(self.ctrl),
            'lineNumber': font.lineNumber('line %s' % self.lineNumber),
            'type': t,
            'occurances': []
        }

    def testDOMSyntax(self, lang):
        s = search(ngApp.syntax[lang], self.line, flags=I)
        if not s:
            return None
        self.lineNumber = font.lineNumber('line %s' % self.lineNumber)
        reference = s.group('reference')
        directive = None
        if 'ng' in lang:
            directive = s.group('directive')
        if reference not in self.functions:
            if directive in ['repeat']:
                self.exemptNames.append(reference)
                return True
            if reference in self.exemptNames:
                return True
            log_params = (font.underline('reference'), font.badName(reference),
                          font.fileName(self.fileName), self.lineNumber)
            print '%s %s found in %s at %s not found in any controller' % log_params
        else:
            self.functions[reference]['occurances'].append({
                'fileName': font.fileName(self.fileName),
                'lineNumber': font.lineNumber(self.lineNumber)
            })

    def findCtrlFunction(self):
        if self.testJSSyntax('js', 'function'): return
        if self.testJSSyntax('ng', 'function'): return
        if self.testJSSyntax('ng', 'variable'): return

    def findDOMFunctionCall(self):
        if self.testDOMSyntax('jsdom'): return
        if self.testDOMSyntax('ngdom'): return

    def searchCtrl(self):
        with open('%s/js/controllers.js' % self.path, 'r') as controllers:
            for i, line in enumerate(controllers.readlines()):
                if 'function' not in line and '=' not in line:
                    continue
                if '.controller' in line:
                    m = search('.controller\((\'|")(?P<ctrl>\w+)(\'|")', line)
                    self.ctrl = m.group('ctrl')
                    continue
                self.line = line
                self.lineNumber = i+1
                self.findCtrlFunction()
            controllers.close()

    def searchTemplates(self):
        for htmlFile in listdir('%s/templates' % self.path):
            with open('%s/templates/%s' % (self.path, htmlFile), 'r') as template:
                for i, line in enumerate(template.readlines()):
                    if 'ng-' in line or 'on-' in line:
                        self.fileName = htmlFile
                        self.line = line
                        self.lineNumber = i+1
                        self.findDOMFunctionCall()
                template.close()

    def printLog(self):
        for funcName, function in self.functions.iteritems():
            for occurance in function['occurances']:
                logParams = (font.underline(function['type']),
                             font.funcName(funcName),
                             occurance['fileName'],
                             occurance['lineNumber'],
                             function['ctrl'],
                             function['lineNumber'])
                print '%s %s found in %s at %s is located in controller %s at %s' % logParams
