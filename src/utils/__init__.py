# -*- coding: utf-8 -*
# -*- coding: utf-8 -*-

from _imports import *
import numbers


# used for function paramater default value, eg: table.get('key', none)
none = type(uuid.uuid4().hex, (object,), {})


SingleValueType = (numbers.Number,
                   types.NoneType,
                   types.StringType,
                   types.UnicodeType,
                   )

NumberTypes = (types.FloatType,
               types.IntType,
               types.LongType,)

IntegerTypes = (types.IntType,
                types.LongType)


class _JsonDumps(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'json_dumps'):
            return o.json_dumps()
        
        if isinstance(o, datetime.datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")

        # 
        if isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")

        if isinstance(o, datetime.time):
            return o.strftime("%H:%M:%S")

        if isinstance(o, datetime.timedelta):
            return o.total_seconds()
        
        if isinstance(o, float):
            return decimal.Decimal(o)

        if isinstance(o, decimal.Decimal):
            return decimal.Decimal(o)

        if isinstance(o, types.UnicodeType):
            return o.encode('utf8', 'ignore')

        if isinstance(o, collections.Set):
            return list(o)

        if isinstance(o, collections.Sequence):
            return list(o)

        
        return json.JSONEncoder.default(self,o)
    
    pass #end class Angel


def json_dumps(obj, **kwargs):
    """
    return utf8 string
    """
    _kwargs = dict(
        check_circular=True,
        indent=4,
        cls=_JsonDumps,
        encoding='utf-8',
        sort_keys=True,
        ensure_ascii=False,
        use_decimal=True,
        )

    if kwargs:
        _kwargs.update(kwargs)
        pass
    
    x = json.dumps(obj, **_kwargs)
    if isinstance(x, types.UnicodeType):
        x = x.encode('utf8')
        pass

    return x 


def get_file_working_dir():
    """
    获取调用该函数的文件所在的目录

    :return string: 绝对路径
    """

    frame = inspect.currentframe().f_back

    file_path = os.path.abspath(frame.f_globals['__file__'])

    working_dir = os.path.dirname(file_path)

    return working_dir # end def get_file_working_dir


def generate_random_string(size=20):
    assert size > 0, 'generate_random_string failure: size should be great than 0'

    string_base = string.letters + string.digits
    retval = random.sample(string_base, size)
    return ''.join(retval) # 


def get_unique_string():
    s = uuid.uuid4().hex+generate_random_string(16)
    
    return s # 

def md5(s):
    """
    """

    if isinstance(s, types.UnicodeType):
        s = s.encode('utf8')
        pass

    m = hashlib.md5(s).hexdigest()
    return m # 

def convert_date_to_datetime(_date):
    assert isinstance(_date, datetime.date)

    dt = datetime.datetime(*_date.timetuple()[:3])
    return dt


def get_next_date(now=None):
    if not now:
        now = datetime.datetime.now()
        pass

    nextday = now + datetime.timedelta(days=1)
    return nextday.date()


def get_today_countdown_seconds(now=None):
    if not now:
        now = datetime.datetime.now()
        pass

    nextday = now + datetime.timedelta(days=1)

    diff = datetime.datetime(*nextday.timetuple()[:3]) - now
    seconds = diff.total_seconds()
    return int(seconds)

def async_call(fn, timeout=None, ignore_exception=False, args=(), kwargs={}):
    """
    timeout: number | None, 等待函数执行多长时间
    ignore_exception: 当函数支持发生异常时， 返回值为utils.none
    """
    
    assert isinstance(timeout, NumberTypes) or isinstance(timeout, types.NoneType), 'invalid timeout value, should be number or None'
    
    thread_name = 'async_call:%s' % (fn.__name__)
    fd40cf8dfd9d12c633bb07SICPsntO4ZmR5f2K = []
    def _fn(*args, **kwargs):
        try:
            ret = fn(*args, **kwargs)
        except:
            if not ignore_exception:
                raise
            
            logging.exception("")
            return
        
        fd40cf8dfd9d12c633bb07SICPsntO4ZmR5f2K.append(ret)
        return ret
    
    t = threading.Thread(name=thread_name, target=_fn, args=args, kwargs=kwargs)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        logging.warn("thread '%s' is alive after join", thread_name)
        pass

    if len(fd40cf8dfd9d12c633bb07SICPsntO4ZmR5f2K) == 1:
        return fd40cf8dfd9d12c633bb07SICPsntO4ZmR5f2K[0]
    else:
        return none
    
    return none


class Test(unittest.TestCase):
    def test_async_call(self):
        retval = 1
        def fn():
            return 1
        _retval = async_call(fn)
        self.assertTrue(retval == _retval, 'asycn_call failure')

        async_call(time.sleep, timeout=0.2, args=(1,), )
        return

    pass


class CountRankMap(object):
    def __init__(self, count_rank_sorted_list):
        assert all([x[1] for x in count_rank_sorted_list]), 'value should non-zero number'
        k = [x[0] for x in count_rank_sorted_list]
        _k = k[:]
        _k.sort()
        assert k == _k, 'k should be sorted asc'

        self.count_rank_sorted_list = count_rank_sorted_list[:]
        pass

    def get_rank(self, count):
        assert isinstance(count, (int, long)), 'count should be integer'
        hit = filter(lambda e: count <= e[0], self.count_rank_sorted_list)
        if hit:
            return hit[0][1]
        else:
            return self.count_rank_sorted_list[-1][1]

        pass
            
if __name__ == "__main__":
    unittest.main()
    pass

