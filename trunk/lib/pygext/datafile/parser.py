
import re
KEYVALUE = r"(\w+)\s*=\s*(.*)$"

__all__ = [
    "LineParser",
    "ClassParser",
    "EndParse",
    "DataFile",
    "DataFileError",
    ]


class EndParse: pass

class LineParser(object):
    rules = []

    def __init__(self, lines, namespace=None):
        self.lines = lines
        self.results = []
        self.lineno = 0
        self.parse()
        if namespace is None:
            namespace = {}
        self.namespace = namespace
        self.result = self.process()

    def parse(self):
        while self.lines:
            line = self.next()
            if line is None:
                return
            for rule, handler in self.rules:
                m = re.match(rule, line)
                if m:
                    if handler is None:
                        self.add(*m.groups())
                    elif handler is EndParse:
                        return
                    else:
                        if isinstance(handler, basestring):
                            handler = getattr(self, handler)
                        result = handler(self, *m.groups())
                        if isinstance(result, Parser):
                            result = result.result
                        if result is EndParse:
                            return
                        if result is not None:
                            self.results.append(result)
                    break
            else:
                self.push(line)
                return
    
    def next(self):
        while self.lines:
            self.lineno += 1
            line = self.lines.pop(0).split('#')[0].strip()
            if line:
                return line

    def push(self, line):
        self.lines.insert(0, line)

    def process(self):
        return results

    def add(self, *args):
        self.results.append(args)

class DataClass(type):
    def __new__(cls, name, base, attrlist, namespace):
        clsname = "".join(map(str.capitalize, name.split()))
        obj = type.__new__(cls, clsname, (base,), {})
        return obj

    def __init__(self, name, base, attrlist, namespace):
        self.name = name
        for k,v in attrlist:
            if isinstance(v, basestring):
                v = eval(v, namespace)
            if k.startswith("["):
                listname = k[1:]
                if hasattr(self, listname):
                    getattr(self,listname).append(v)
                else:
                    setattr(self, listname, [v])
            elif k.startswith("{"):
                dictname = k[1:]
                key,value = v
                if hasattr(self, dictname):
                    getattr(self, dictname)[key] = value
                else:
                    setattr(self, dictname, {key:value})
            else:
                setattr(self, k, v)
        

class ClassParser(Parser):
    baseclass = None

    def __init__(self, parser, name, *args):
        self.name = name
        self.parser = parser
        lines = parser.lines
        self.init(*args)
        Parser.__init__(self, lines)

    def init(self, *args):
        pass

    def process(self):
        return DataClass(self.name, self.baseclass, self.results, self.parser.namespace)


class DataFileError(Exception): pass

class DataFile(Parser):   
    def __init__(self, filename, namespace=None):
        self.filename = filename
        lines = open(self.filename).readlines()
        Parser.__init__(self, lines, namespace)

    def process(self):
        if self.lines:
            raise DataFileError, "Invalid syntax on line %i in datafile %s: %r" % (self.lineno, self.filename, self.lines[0])
        self.defs = {}
        for r in self.results:
            self.defs[r.name] = r

    def __getitem__(self, key):
        return self.defs[key]
                    
