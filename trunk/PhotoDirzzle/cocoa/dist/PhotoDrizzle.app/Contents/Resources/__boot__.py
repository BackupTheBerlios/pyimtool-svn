def _site_packages():
    import site, sys, os
    paths = []
    prefixes = [sys.prefix]
    if sys.exec_prefix != sys.prefix:
        prefixes.append(sys.exec_prefix)
    for prefix in prefixes:
        paths.append(os.path.join(prefix, 'lib', 'python' + sys.version[:3],
            'site-packages'))
    if os.path.join('.framework', '') in os.path.join(sys.prefix, ''):
        home = os.environ.get('HOME')
        if home:
            paths.append(os.path.join(home, 'Library', 'Python',
                sys.version[:3], 'site-packages'))
    for path in paths:
        site.addsitedir(path)
_site_packages()


def _chdir_resource():
    import os
    os.chdir(os.environ['RESOURCEPATH'])
_chdir_resource()


def _path_inject(paths):
    import sys
    sys.path[:0] = paths


_path_inject(['/Users/fpierfed/Documents/workspace/PhotoDirzzle/cocoa'])


def _run(*scripts):
    import os, sys, site
    import Carbon.File
    sys.frozen = 'macosx_app'
    site.addsitedir(os.environ['RESOURCEPATH'])
    for (script, path) in scripts:
        alias = Carbon.File.Alias(rawdata=script)
        target, wasChanged = alias.ResolveAlias(None)
        if not os.path.exists(path):
            path = target.as_pathname()
        sys.path.append(os.path.dirname(path))
        execfile(path, globals(), globals())


try:
    _run(('\x00\x00\x00\x00\x00\xd8\x00\x02\x00\x00\x06tiamat\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbd\x80\x95+H+\x00\x00\x00\x1e\x0eZ\x07main.py\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1e\x0e]\xbed\x80K\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\t \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00\x08\x00\x00\xbd\x80\xf7\x9b\x00\x00\x00\x11\x00\x08\x00\x00\xbed\xe2\xbb\x00\x00\x00\x0e\x00\x10\x00\x07\x00m\x00a\x00i\x00n\x00.\x00p\x00y\x00\x0f\x00\x0e\x00\x06\x00t\x00i\x00a\x00m\x00a\x00t\xff\xff\x00\x00', '/Users/fpierfed/Documents/workspace/PhotoDirzzle/cocoa/main.py'))
except KeyboardInterrupt:
    pass
