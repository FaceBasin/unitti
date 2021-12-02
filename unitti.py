"""
Author: Wenda Lu 2019
"""

# TODO handle empty test suite (empty, not included or excluded)

import time
from io import StringIO
from sys import exc_info
from inspect import getsource
from unittest import TestLoader
from unittest.case import SkipTest
from threading import Lock, Event
from collections import defaultdict
from functools import wraps, partial
from concurrent.futures import ThreadPoolExecutor, wait
from unittest.suite import _ErrorHolder


def _d(**kwargs):
    def dd(o):
        for k, v in kwargs.items():
            setattr(o, k, v)
        return o
    return dd


def groups(*args):
    """class or function decorator. assign groups to function
       if a class is decorated by it then groups of all functions in this class will be overwritten
    """
    return _d(groups=args)


def default_groups(*args):
    """class or function decorator. add default groups for function or data
       if a class is decorated by it then default groups of all functions in this class will be overwritten
    """
    return _d(dgs=args)


def alias(name):
    """function decorator. make an alias for the function"""
    return _d(alias=name)


def info(**kwargs):
    """function decorator. add extra information to the function"""
    return _d(info=kwargs)


def class_info(**kwargs):
    """class decorator. add extra information to the function"""
    return _d(ci=kwargs)


def before_functions(*args, hard_dependency=True):
    """
    function decorator. decorated function will run before designated functions
    if hard_dependency is True, designated functions will be skipped if decorated function does not succeed
    """
    return _d(bf=args, hdbf=hard_dependency)


def after_functions(*args, hard_dependency=True):
    """
    function decorator. decorated function will run after designated functions
    if hard_dependency is True, decorated function will be skipped if any designated function does not succeed
    """
    return _d(af=args, hdaf=hard_dependency)


def before_groups(*args, hard_dependency=True):
    """
    function decorator. decorated function will run before all functions in designated groups
    if hard_dependency is True, all functions in designated groups will be skipped if designated function does not succeed
    """
    return _d(bg=args, hdbg=hard_dependency)


def after_groups(*args, hard_dependency=True):
    """
    function decorator. decorated function will run after all functions in designated groups
    if hard_dependency is True, decorated function will be skipped if any function in designated groups does not succeed
    """
    return _d(ag=args, hdag=hard_dependency)


def before_aliases(*args, hard_dependency=True):
    """
    function decorator. decorated function will run before functions represented by designated aliases
    if hard_dependency is True, designated functions will be skipped if decorated function does not succeed
    """
    return _d(ba=args, hdba=hard_dependency)


def after_aliases(*args, hard_dependency=True):
    """
    function decorator. decorated function will run after functions represented by designated aliases
    if hard_dependency is True, decorated function will be skipped if any designated function does not succeed
    """
    return _d(aa=args, hdaa=hard_dependency)


def data_provider(provider, docstring_list=None, group_list=None, info_list=None):
    """
    function decorator. decorated function will derive multiple functions according to the provider function
    for each derived function, docstring, groups and info can be passed via docstring_list, groups_list and info_list
    """
    return _d(pd=provider, dl=docstring_list, gl=group_list, il=info_list)


def serial(*args, **kwargs):
    """
    class decorator. functions in decorated class will be executed one by one in serial
    if definition_order is True, functions will be executed in definition order
    if fast_fail is True, remaining functions will be skipped if a function does not succeed
    """
    if args:
        args[0].serial = True
        args[0].by_def = False
        return args[0]
    else:
        def decorator(o):
            o.serial = True
            o.by_def = kwargs.get('definition_order', False)
            if kwargs.get('fast_fail', False):
                setattr(o, 'setUp', _ff_setup_wrapper(o.setUp))
            return o
        return decorator


def batch(batch_number):
    """
    class decorator. assign class to batch. batch executes one by one in serial.
    dependencies cannot be defined across batches.
    """
    return _d(bn=batch_number)


class UContext:
    pass


# simple test context
u_context = UContext()


def _dp_wrapper(func, ds, *args):
    @wraps(func)
    def wrapper(self):
        return func(self, *args)
    wrapper.__doc__ = ds
    return wrapper


def _dp_exc_wrapper(func, exc):
    @wraps(func)
    def wrapper(x):
        raise exc
    return wrapper


def _ff_setup_wrapper(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        _check_ff(self, self._outcome.result.failures)
        _check_ff(self, self._outcome.result.errors)
        _check_ff(self, self._outcome.result.skipped)
        func(self, *args, **kwargs)
    return wrapper


def _check_ff(cls, result_list):
    if result_list and type(result_list[-1][0]) == type(cls):
        cls.skipTest('Skip remaining tests as fast fail is enabled')


class DAG:
    def __init__(self):
        self._o_edges = defaultdict(list)

    def add(self, a, b):
        # a->b
        self._o_edges[a].append(b)
        if b and b not in self._o_edges:
            self._o_edges[b] = [None]

    def erase(self, x):
        del self._o_edges[x]

    def sort(self):
        ret = []
        visited = defaultdict(lambda: -1)
        tests = [x for x in self._o_edges if x is not None]
        tests.reverse()

        def _sort_helper(a):
            visited[a] = 0
            for b in self._o_edges[a]:
                if not b:
                    continue
                if visited[b] == 0:
                    raise ValueError('Cyclic dependency <{}> detected'.format(b))
                if visited[b] == -1:
                    _sort_helper(b)
            ret.insert(0, a)
            visited[a] = 1

        for test in tests:
            if visited[test] == -1:
                _sort_helper(test)
        return ret

    def __len__(self):
        return len(self._o_edges)


class DAGExec(DAG):
    def __init__(self, timeout=2400):
        super().__init__()
        self._timeout = timeout
        self._started = set()

    def fetch(self):
        dp = set()
        for k, v in self._o_edges.items():
            dp |= set(v)
        return [k for k, v in self._o_edges.items() if k not in dp and k not in self._started]

    def start(self, x):
        self._started.add(x)

    def is_started(self, x):
        return x in self._started

    def count_started(self):
        return len(self._started)

    def execute(self, pool_size=4, *exec_args, **exec_kwargs):
        total = len(self)
        if not total:
            return
        ac = Event()
        lock = Lock()
        pool = ThreadPoolExecutor(pool_size)
        futures = []

        def _callback(node_finished, _f):
            with lock:
                self.erase(node_finished)
            if self.count_started() == total:
                ac.set()
                return
            for a in self.fetch():
                if not self.is_started(a):
                    self.start(a)
                    ft = pool.submit(a, *exec_args, **exec_kwargs)
                    ft.add_done_callback(partial(_callback, a))
                    futures.append(ft)

        for b in self.fetch():
            if not self.is_started(b):
                self.start(b)
                f = pool.submit(b, *exec_args, **exec_kwargs)
                futures.append(f)
                f.add_done_callback(partial(_callback, b))
        u = time.time()
        ac.wait(self._timeout)
        v = time.time()
        wait(futures, timeout=self._timeout-int(v-u))
        _show_errors(futures)


def _show_errors(ft):
    # TODO
    for f in ft:
        e = f.exception()
        if e:
            print('ERROR - {}'.format(e))


class _RC:
    def __init__(self):
        self.i = 0
        self.result = None
        self.dds1 = defaultdict(set)
        self.ddlk1 = defaultdict(Lock)
        self.dde1 = defaultdict(Event)
        self.ddi1 = defaultdict(int)
        self.ddb1 = defaultdict(bool)
        self.ddl1 = defaultdict(list)
        self.dddb1 = defaultdict(lambda: defaultdict(bool))


def _compare_test_by_ln(c, t1, t2):
    x = getattr(c, t1).__code__.co_firstlineno
    y = getattr(c, t2).__code__.co_firstlineno
    return (x > y) - (x < y)


def _sw(x):
    # TODO show detail
    raise SkipTest('Prerequisite {} did not pass'.format(x))


def _fw():
    raise RuntimeError('setUpClass failed')


def _cd(r, d):
    for u in (r.failures, r.errors, r.skipped):
        for v in u:
            if v[0] == d:
                return v[0]


def _test_wrapper(self, *args, **kwargs):
    i = self.i
    rc = self.rc
    with rc.ddlk1[i]:
        if i not in rc.dds1[i]:
            rc.dds1[i].add(i)
            c = self.__class__
            if not getattr(c, '__unittest_skip__', False) and hasattr(c, 'setUpClass'):
                try:
                    c.setUpClass()
                except Exception as ex:
                    rc.ddb1[i] = True
                    err = 'setUpClass {}'.format('{0}.{1}'.format(c.__module__, c.__qualname__))
                    _eh(rc.result, ex, err)
            rc.dde1[i].set()
    rc.dde1[i].wait()
    for dp in rc.ddl1[self.n]:
        if _cd(args[0], dp) and rc.dddb1[self][dp]:
            # self.setUp = _sw
            self.setUp = partial(_sw, dp)
            break
    if rc.ddb1[i]:
        self.setUp = _fw
    r = self.run(*args, **kwargs)
    rc.ddi1[i] -= 1
    with rc.ddlk1[i]:
        if rc.ddi1[i] == 0:
            rc.dds1[i].remove(i)
            c = self.__class__
            if hasattr(c, 'tearDownClass'):
                try:
                    c.tearDownClass()
                except Exception as ex:
                    err = 'tearDownClass {}'.format('{0}.{1}'.format(c.__module__, c.__qualname__))
                    _eh(rc.result, ex, err)
    return r


def _eh(res, ex, err):
    err = _ErrorHolder(err)
    if isinstance(ex, SkipTest):
        res.addSkip(err, str(ex))
    else:
        res.addError(err, exc_info())


def _rm_deco(cls):
    cstr = 'class UtiTempLoading:\n'
    st = StringIO(getsource(cls))
    f = False
    for l in st:
        if l.startswith('class'):
            continue
        x = l.strip()
        if x.startswith('@'):
            f = True
        elif x.startswith('def') or x.startswith('class'):
            f = False
        if not f:
            cstr += l
    return cstr


def _pd(tc, tn):
    ret = []
    for n in tn:
        m = getattr(tc, n)
        if getattr(m, '_derived', False):
            continue
        pd = getattr(m, 'pd', None)
        if pd:
            pdf = pd.__func__ if type(pd) == staticmethod else pd
            try:
                dt = pdf()
            except Exception as e:
                setattr(tc, n, _dp_exc_wrapper(m, e))
                ret.append(n)
                continue
            s = len(dt)
            dl = getattr(m, 'dl', None) or [None]*s
            gl = getattr(m, 'gl', None) or [None]*s
            il = getattr(m, 'il', None) or [None]*s
            for i in dl, gl, il:
                if len(i) != s:
                    raise ValueError('parameter size does not match test data size: {}'.format(i))
            for i, (x, y, z, w) in enumerate(zip(dt, dl, gl, il)):
                pn = '{0}_{1}'.format(n, i+1)
                docstring = y if y else m.__doc__
                setattr(tc, pn, _dp_wrapper(m, docstring, *x))
                nf = getattr(tc, pn)
                nf._derived = True
                nf._derived_by = m.__name__
                if z:
                    g = list(z)
                    g.extend(getattr(nf, 'groups', []))
                    if len(g) == 0:
                        g.extend(getattr(nf, 'dgs', []))
                    nf.groups = g
                if w:
                    nf.info = getattr(m, 'info', {}).copy()
                    nf.info.update(w)
                ret.append(pn)
        else:
            ret.append(n)
    return ret


def _gf(cls, names, incl, excl):
    incl, excl = set(incl), set(excl)
    if incl & excl:
        raise ValueError('Include and exclude groups conflict: ' + ''.join(incl & excl))
    if incl or excl:
        ret = []
        cdg = getattr(cls, 'dgs', None)
        cg = getattr(cls, 'groups', None)
        for t in names:
            func = getattr(cls, t)
            test_groups = cg or getattr(func, 'groups', ()) or cdg or getattr(func, 'dgs', ())
            g = set(test_groups)
            if (not incl or g & incl) and not (g & excl):
                ret.append(t)
        return ret
    return names


def _bp(dd, tt, de, hd, key, rc):
    for k, v in dd[key].items():
        for dep in v:
            t = tt[dep]
            de.add(k, t)
            rc.ddl1[t.n].append(k)
            if hd[key].get(k, False):
                rc.dddb1[t][k] = True


def _ap(dd, tt, de, hd, key, rc):
    for k, v in dd[key].items():
        for dep in v:
            t = tt[dep]
            de.add(t, k)
            rc.ddl1[k.n].append(t)
            if hd[key].get(k, False):
                rc.dddb1[k][t] = True


def load_classes(*classes, include=(), exclude=(), pool_size=32):
    ld = UtiTestLoader()
    ddl = defaultdict(list)
    res = []
    for c in classes:
        b = getattr(c, 'bn', 4)
        ddl[b].append(c)
        c.bn = b
    for k, v in sorted(ddl.items()):
        de = DAGExec()
        rc = _RC()
        ld.load_classes(*v, de=de, rc=rc, include=include, exclude=exclude)
        res.append((de, rc))
    s = UtiTestSuite(*res, pool_size=pool_size)
    s.pool_size = pool_size
    return s


class UtiTestLoader(TestLoader):
    def load_classes(self, *classes, de, rc, include=(), exclude=()):
        a2t = {}
        g2t = defaultdict(list)
        dd = defaultdict(dict)
        hd = defaultdict(dict)
        n = 0
        for c in classes:
            cg = getattr(c, 'groups', None)
            cdg = getattr(c, 'dgs', None)
            c.group_map = defaultdict(list)
            sorting_method = self.sortTestMethodsUsing
            se = getattr(c, 'serial', False)
            by_def = getattr(c, 'by_def', False)
            if by_def:
                exec(_rm_deco(c))
                self.sortTestMethodsUsing = partial(_compare_test_by_ln, eval('UtiTempLoading'))
            test_names = self.getTestCaseNames(c)
            self.sortTestMethodsUsing = sorting_method
            test_names = _pd(c, test_names)
            test_names = _gf(c, test_names, include, exclude)
            c.__call__ = _test_wrapper
            prev = None
            n2t, md = {}, {}
            ci = getattr(c, 'ci', {})
            for name in test_names:
                test = c(name)
                for k, v in ci.items():
                    setattr(test, '_'+k, v)
                if se and prev:
                    de.add(prev, test)
                prev = test
                test.rc = rc
                test.i = rc.i
                test.n = n
                n += 1
                n2t[name] = test
                f = getattr(c, name)
                gps = cg or getattr(f, 'groups', ()) or cdg or getattr(f, 'dgs', ())
                c.group_map[name] = gps or ['Ungrouped']
                for g in gps:
                    g2t[g].append(test)
                if hasattr(f, 'alias'):
                    # TODO nonrepeat
                    a2t[getattr(f, 'alias')] = test
                for attr in 'bf', 'ba', 'bg', 'af', 'aa', 'ag':
                    dd[attr][test] = getattr(f, attr, ())
                    hd[attr][test] = getattr(f, 'hd'+attr, False)
                de.add(test, None)
                rc.ddi1[rc.i] += 1
            _bp(dd, n2t, de, hd, 'bf', rc)
            dd['bf'] = {}
            _ap(dd, n2t, de, hd, 'af', rc)
            dd['af'] = {}
            rc.i += 1
        _bp(dd, a2t, de, hd, 'ba', rc)
        _ap(dd, a2t, de, hd, 'aa', rc)
        for k, v in dd['bg'].items():
            for g in v:
                for t in g2t[g]:
                    de.add(k, t)
                    rc.ddl1[t.n].append(k)
                    if hd['bg'].get(k, False):
                        rc.dddb1[t][k] = True
        for k, v in dd['ag'].items():
            for g in v:
                for t in g2t[g]:
                    de.add(t, k)
                    if hd['ag'].get(k, False):
                        rc.dddb1[k][t] = True
                rc.ddl1[k.n] += g2t[g]
        de.sort()
        # return de


class UtiTestSuite:
    def __init__(self, *dr, pool_size=32):
        self.dr = dr
        self.pool_size = pool_size

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def run(self, result):
        for x in self.dr:
            x[1].result = result
            x[0].execute(self.pool_size, result)
        return result
