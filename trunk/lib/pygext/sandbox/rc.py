"""RC - Restricted Compiler

Compile-time sandbox utility, that compiles ython source to Python into
bytecode, and tries to scan the code for "dangerous" instructions. Should be
pretty trustworthy, provided you are careful with what you publish.

As a guideline, NEVER publish anything that gives access to abitrary dictionaries
such as the builtin function 'getattr' or something like 'globals' and 'locals'.
"""

import dis, sys

__all__ = [
    "RCompiler",
    "RCompilerError",
    ]

def _get_opcodes(codeobj):
    """_get_opcodes(codeobj) -> [opcodes]

    Extract the actual opcodes as a list from a code object

    >>> c = compile("[1 + 2, (1,2)]", "", "eval")
    >>> _get_opcodes(c)
    [100, 100, 23, 100, 100, 102, 103, 83]
    """
    i = 0
    opcodes = []
    s = codeobj.co_code
    while i < len(s):
        code = ord(s[i])
        opcodes.append(code)
        if code >= dis.HAVE_ARGUMENT:
            i += 3
        else:
            i += 1
    return opcodes        

def _map_names(names):
    return map(dis.opmap.__getitem__, names)

bad_names = []
_code  = compile("pass", "", "exec")
def _func(): pass
_frame = sys._getframe()

for name in dir(_code)+dir(_func)+dir(_frame):
    if not name.startswith("_"):
        bad_names.append(name)

bad_opcodes = _map_names([
    "IMPORT_NAME",
    "IMPORT_STAR",
    "IMPORT_FROM",
    "EXEC_STMT",
    ])

class RCompilerError(Exception): pass

class RCode(object):
    def __init__(self, codeobj, namespace):
        self._codeobj = codeobj
        self._namespace = namespace

    def execute(self):
        ns = self._namespace
        exec self._codeobj in ns
        return ns

class RCompiler(object):
    def __init__(self):
        """Create a new RCompiler"""
        self._namespace = {}

    def publish_func(self, *funcs):
        """Publish a function to the source"""
        for func in funcs:
            self._namespace[func.func_name] = func

    def publish_obj(self, name, obj):
        """Publish an object to the source"""
        self._namespace[func.func_name] = obj

    def publish_module(self, *modules):
        """Publish a module to the source"""
        for mod in modules:
            if type(mod) is str:
                mod = __import__(mod)
            self._namespace[mod.__name__] = mod

    def publish_from(self, module):
        """Publish all symbols from a given module"""
        if type(module) is str:
            module = __import__(module)
        if hasattr(module, '__all__'):
            names = module.__all__
        else:
            names = module.__dict__.keys()
            
        for name in names:
            self.publish_obj(name, getattr(module, name))

    def compile(self, src):
        """Compile Python source to bytecode"""
        c = compile(src, "<string>", "exec")
        self._check_code(c)
        ns = self._namespace.copy()
        ns['__builtins__'] = {}
        return RCode(c, ns)

    def _check_code(self, c):
        for op in _get_opcodes(c):
            if op in bad_opcodes:
                raise RCompilerError, "Forbidden bytecode: %s" % dis.opname(op)
        for name in c.co_names:
            if name in bad_names or name.startswith("_"):
                raise RCompilerError, "Forbidden name: %s" % name            
        for const in c.co_consts:
            if type(const) is type(c):
                self._check_code(const)
