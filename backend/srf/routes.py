"""
@Author: WangYuXiang
@E-mile: Hill@3io.cc
@CreateTime: 2021/1/19 16:08
@DependencyLibrary: 无
@MainFunction：无
@FileDoc:
    routes.py
    便捷路由文件
"""
from collections import namedtuple

# 默认分组
from pprint import pprint

Route = namedtuple('Route', ['url', 'mapping', 'name', 'detail', 'initkwargs', 'is_base'])


class BaseRoute:

    def __init__(self, trailing_slash=False):
        """
        基础类
        :param trailing_slash:
        """
        self.trailing_slash = '/' if trailing_slash else ''
        self.registry = []

    def register(self, viewset: object, prefix: str, basename: str = None, is_base: bool = False):
        if basename is None:
            basename = prefix.replace('/', '_')
        self.registry.append((prefix, viewset, basename, is_base))

        # invalidate the urls cache
        if hasattr(self, '_urls'):
            del self._urls

    def get_urls(self):
        pass

    @property
    def urls(self):
        if not hasattr(self, '_urls'):
            self._urls = self.get_urls()
        return self._urls


class ViewSetRouter(BaseRoute):
    routes = [
        # List route.
        Route(
            url=r'{prefix}{trailing_slash}',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'},
            is_base=False,
        ),
        Route(
            url=r'{prefix}/<{lookup}:str>{trailing_slash}',
            mapping={
                'get': 'retrieve',
                'put': 'put',
                'patch': 'patch',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'},
            is_base=False,
        ),
    ]

    def get_lookup(self, viewset):
        """
        得到主键字段名
        :param viewset: 集合视图
        :return:
        """
        return getattr(viewset, 'lookup_field', 'pk')

    def get_urls(self):
        """
        Use the registered viewsets to generate a list of URL patterns.
        """
        ret = []

        for prefix, viewset, basename, is_base in self.registry:
            lookup = self.get_lookup(viewset)

            for route in self.routes:

                # Only actions which actually exist on the viewset will be bound
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue

                # Build the url pattern
                uri = route.url.format(
                    prefix=prefix,
                    lookup=lookup,
                    trailing_slash=self.trailing_slash
                )

                # If there is no prefix, the first part of the url is probably
                #   controlled by project's urls.py and the router is in an app,
                #   so a slash in the beginning will (A) cause Django to give
                #   warnings and (B) generate URLS that will require using '//'.
                if not prefix and uri[:2] == '^/':
                    uri = '^' + uri[2:]

                initkwargs = route.initkwargs.copy()
                initkwargs.update({
                    'basename': basename,
                    'detail': route.detail,
                })

                view = viewset.as_view(mapping, **initkwargs)
                name = route.name.format(basename=basename)
                ret.append({
                    'handler': view,
                    'uri': uri,
                    'name': name,
                    'is_base': is_base,

                })
        return ret

    def get_method_map(self, viewset, method_map):
        """得到可用的模型"""
        bound_methods = {}
        for method, action in method_map.items():
            if hasattr(viewset, action):
                bound_methods[method] = action
        return bound_methods
