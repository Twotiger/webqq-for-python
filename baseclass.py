# -*- coding: utf-8 -*-
class BaseDict():

    def mydecorator(self, function):
        def _mydecorator(*args, **kw):
            s =function(*args, **kw)
            if s:
                return u"[\""+ s+u"\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]"
            else:
                return None
        return _mydecorator

    def test(self):
        print 'hooll'