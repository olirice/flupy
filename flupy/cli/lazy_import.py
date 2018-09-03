import importlib


class LazyObject:
    def __init__(self, load, ctx, name):
        self._lasdo = {
            'loaded': False,
            'load': load,
            'ctx': ctx,
            'name': name
        }

    def _lazy_obj(self):
        d = self._lasdo
        if d['loaded']:
            obj = d['obj']
        else:
            obj = d['load']()
            d['ctx'][d['name']] = d['obj'] = obj
            d['loaded'] = True
        return obj

    def __getattribute__(self, name):
        if name == '_lasdo' or name == '_lazy_obj':
            return super().__getattribute__(name)
        obj = self._lazy_obj()
        return getattr(obj, name)


def lazy_import(module_name):
    return LazyObject(load=lambda: importlib.import_module(module_name),
                      ctx=globals(),
                      name=module_name)

json = lazy_import('json')
os = lazy_import('os')
csv = lazy_import('csv')
re = lazy_import('re')
math = lazy_import('math')
random = lazy_import('random')
statistics = lazy_import('statistics')
