[33mcommit 521d026a72a84e0d37b56f94e938babb92939cfe[m
Author: [1;31mlin1397[m <[1;31mlin1397[m@purdue.edu>
Date:   Tue Feb 11 15:56:28 2025 -0500

    Update the path for background

 .eggs/README.txt                                   |    6 [31m-[m
 .eggs/altgraph-0.17.4-py3.10.egg/EGG-INFO/LICENSE  |   18 [31m-[m
 .eggs/altgraph-0.17.4-py3.10.egg/EGG-INFO/PKG-INFO |  293 [31m---[m
 .eggs/altgraph-0.17.4-py3.10.egg/EGG-INFO/RECORD   |   13 [31m-[m
 .eggs/altgraph-0.17.4-py3.10.egg/EGG-INFO/WHEEL    |    6 [31m-[m
 .../EGG-INFO/top_level.txt                         |    1 [31m-[m
 .eggs/altgraph-0.17.4-py3.10.egg/EGG-INFO/zip-safe |    1 [31m-[m
 .eggs/altgraph-0.17.4-py3.10.egg/altgraph/Dot.py   |  321 [31m---[m
 .eggs/altgraph-0.17.4-py3.10.egg/altgraph/Graph.py |  682 [31m-----[m
 .../altgraph/GraphAlgo.py                          |  171 [31m--[m
 .../altgraph/GraphStat.py                          |   73 [31m-[m
 .../altgraph/GraphUtil.py                          |  139 [31m-[m
 .../altgraph/ObjectGraph.py                        |  212 [31m--[m
 .../altgraph/__init__.py                           |  148 [31m--[m
 .../altgraph/__pycache__/Graph.cpython-310.pyc     |  Bin [31m19650[m -> [32m0[m bytes
 .../altgraph/__pycache__/GraphUtil.cpython-310.pyc |  Bin [31m3207[m -> [32m0[m bytes
 .../__pycache__/ObjectGraph.cpython-310.pyc        |  Bin [31m6949[m -> [32m0[m bytes
 .../altgraph/__pycache__/__init__.cpython-310.pyc  |  Bin [31m5345[m -> [32m0[m bytes
 .eggs/macholib-1.16.3-py3.10.egg/EGG-INFO/LICENSE  |   21 [31m-[m
 .eggs/macholib-1.16.3-py3.10.egg/EGG-INFO/PKG-INFO |  453 [31m----[m
 .eggs/macholib-1.16.3-py3.10.egg/EGG-INFO/RECORD   |   24 [31m-[m
 .eggs/macholib-1.16.3-py3.10.egg/EGG-INFO/WHEEL    |    6 [31m-[m
 .../EGG-INFO/entry_points.txt                      |    4 [31m-[m
 .../EGG-INFO/requires.txt                          |    1 [31m-[m
 .../EGG-INFO/top_level.txt                         |    1 [31m-[m
 .eggs/macholib-1.16.3-py3.10.egg/EGG-INFO/zip-safe |    1 [31m-[m
 .eggs/macholib-1.16.3-py3.10.egg/macholib/MachO.py |  500 [31m----[m
 .../macholib/MachOGraph.py                         |  141 [31m--[m
 .../macholib/MachOStandalone.py                    |  181 [31m--[m
 .../macholib/SymbolTable.py                        |  104 [31m-[m
 .../macholib/__init__.py                           |    8 [31m-[m
 .../macholib/__main__.py                           |   80 [31m-[m
 .../macholib/__pycache__/MachO.cpython-310.pyc     |  Bin [31m10821[m -> [32m0[m bytes
 .../__pycache__/MachOGraph.cpython-310.pyc         |  Bin [31m4401[m -> [32m0[m bytes
 .../__pycache__/MachOStandalone.cpython-310.pyc    |  Bin [31m5365[m -> [32m0[m bytes
 .../macholib/__pycache__/__init__.cpython-310.pyc  |  Bin [31m345[m -> [32m0[m bytes
 .../macholib/__pycache__/dyld.cpython-310.pyc      |  Bin [31m5239[m -> [32m0[m bytes
 .../macholib/__pycache__/dylib.cpython-310.pyc     |  Bin [31m1171[m -> [32m0[m bytes
 .../macholib/__pycache__/framework.cpython-310.pyc |  Bin [31m1308[m -> [32m0[m bytes
 .../__pycache__/itergraphreport.cpython-310.pyc    |  Bin [31m2109[m -> [32m0[m bytes
 .../macholib/__pycache__/mach_o.cpython-310.pyc    |  Bin [31m40886[m -> [32m0[m bytes
 .../macholib/__pycache__/ptypes.cpython-310.pyc    |  Bin [31m9168[m -> [32m0[m bytes
 .../macholib/__pycache__/util.cpython-310.pyc      |  Bin [31m7399[m -> [32m0[m bytes
 .../macholib/_cmdline.py                           |   49 [31m-[m
 .eggs/macholib-1.16.3-py3.10.egg/macholib/dyld.py  |  228 [31m--[m
 .eggs/macholib-1.16.3-py3.10.egg/macholib/dylib.py |   45 [31m-[m
 .../macholib/framework.py                          |   45 [31m-[m
 .../macholib/itergraphreport.py                    |   73 [31m-[m
 .../macholib-1.16.3-py3.10.egg/macholib/mach_o.py  | 1641 [31m------------[m
 .../macholib/macho_dump.py                         |   57 [31m-[m
 .../macholib/macho_find.py                         |   22 [31m-[m
 .../macholib/macho_standalone.py                   |   30 [31m-[m
 .../macholib-1.16.3-py3.10.egg/macholib/ptypes.py  |  334 [31m---[m
 .eggs/macholib-1.16.3-py3.10.egg/macholib/util.py  |  262 [31m--[m
 .../modulegraph-0.19.6-py3.10.egg/EGG-INFO/LICENSE |   16 [31m-[m
 .../EGG-INFO/PKG-INFO                              |  523 [31m----[m
 .../modulegraph-0.19.6-py3.10.egg/EGG-INFO/RECORD  |   14 [31m-[m
 .eggs/modulegraph-0.19.6-py3.10.egg/EGG-INFO/WHEEL |    6 [31m-[m
 .../EGG-INFO/entry_points.txt                      |    2 [31m-[m
 .../EGG-INFO/requires.txt                          |    2 [31m-[m
 .../EGG-INFO/top_level.txt                         |    1 [31m-[m
 .../EGG-INFO/zip-safe                              |    1 [31m-[m
 .../modulegraph/__init__.py                        |    1 [31m-[m
 .../modulegraph/__main__.py                        |  118 [31m-[m
 .../__pycache__/__init__.cpython-310.pyc           |  Bin [31m208[m -> [32m0[m bytes
 .../modulegraph/__pycache__/_imp.cpython-310.pyc   |  Bin [31m2293[m -> [32m0[m bytes
 .../__pycache__/find_modules.cpython-310.pyc       |  Bin [31m6958[m -> [32m0[m bytes
 .../__pycache__/modulegraph.cpython-310.pyc        |  Bin [31m51114[m -> [32m0[m bytes
 .../modulegraph/__pycache__/util.cpython-310.pyc   |  Bin [31m2886[m -> [32m0[m bytes
 .../modulegraph/__pycache__/zipio.cpython-310.pyc  |  Bin [31m6348[m -> [32m0[m bytes
 .../modulegraph/_imp.py                            |   90 [31m-[m
 .../modulegraph/find_modules.py                    |  326 [31m---[m
 .../modulegraph/modulegraph.py                     | 2295 [31m-----------------[m
 .../modulegraph/util.py                            |  133 [31m-[m
 .../modulegraph/zipio.py                           |  379 [31m---[m
 .../py2app-0.28.8-py3.10.egg/EGG-INFO/LICENSE.txt  |   11 [31m-[m
 .eggs/py2app-0.28.8-py3.10.egg/EGG-INFO/PKG-INFO   | 2027 [31m---------------[m
 .eggs/py2app-0.28.8-py3.10.egg/EGG-INFO/RECORD     |  133 [31m-[m
 .eggs/py2app-0.28.8-py3.10.egg/EGG-INFO/WHEEL      |    6 [31m-[m
 .../EGG-INFO/entry_points.txt                      |   17 [31m-[m
 .../py2app-0.28.8-py3.10.egg/EGG-INFO/requires.txt |    4 [31m-[m
 .../EGG-INFO/top_level.txt                         |    1 [31m-[m
 .eggs/py2app-0.28.8-py3.10.egg/py2app/__init__.py  |   35 [31m-[m
 .../py2app/__pycache__/__init__.cpython-310.pyc    |  Bin [31m1432[m -> [32m0[m bytes
 .../py2app/__pycache__/_pkg_meta.cpython-310.pyc   |  Bin [31m2846[m -> [32m0[m bytes
 .../py2app/__pycache__/build_app.cpython-310.pyc   |  Bin [31m57206[m -> [32m0[m bytes
 .../__pycache__/create_appbundle.cpython-310.pyc   |  Bin [31m2076[m -> [32m0[m bytes
 .../create_pluginbundle.cpython-310.pyc            |  Bin [31m1988[m -> [32m0[m bytes
 .../py2app/__pycache__/filters.cpython-310.pyc     |  Bin [31m2003[m -> [32m0[m bytes
 .../py2app/__pycache__/util.cpython-310.pyc        |  Bin [31m21120[m -> [32m0[m bytes
 .eggs/py2app-0.28.8-py3.10.egg/py2app/_pkg_meta.py |  120 [31m-[m
 .../py2app/apptemplate/__init__.py                 |    2 [31m-[m
 .../__pycache__/__init__.cpython-310.pyc           |  Bin [31m255[m -> [32m0[m bytes
 .../__pycache__/plist_template.cpython-310.pyc     |  Bin [31m1982[m -> [32m0[m bytes
 .../apptemplate/__pycache__/setup.cpython-310.pyc  |  Bin [31m3018[m -> [32m0[m bytes
 .../py2app/apptemplate/lib/__error__.sh            |   19 [31m-[m
 .../py2app/apptemplate/lib/site.py                 |  204 [31m--[m
 .../py2app/apptemplate/plist_template.py           |   61 [31m-[m
 .../py2app/apptemplate/prebuilt/main-arm64         |  Bin [31m74711[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-asl-arm64     |  Bin [31m74971[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-asl-i386      |  Bin [31m44816[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-asl-intel     |  Bin [31m85968[m -> [32m0[m bytes
 .../apptemplate/prebuilt/main-asl-universal2       |  Bin [31m156892[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-asl-x86_64    |  Bin [31m57432[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-fat           |  Bin [31m99716[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-fat3          |  Bin [31m131928[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-i386          |  Bin [31m44648[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-intel         |  Bin [31m85776[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-ppc           |  Bin [31m46468[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-ppc64         |  Bin [31m45936[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-universal     |  Bin [31m181104[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-universal2    |  Bin [31m156636[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-x86_64        |  Bin [31m57240[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/main-x86_64-oldsdk |  Bin [31m36816[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/secondary-arm64    |  Bin [31m74508[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/secondary-fat      |  Bin [31m99476[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/secondary-fat3     |  Bin [31m131696[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/secondary-i386     |  Bin [31m44540[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/secondary-intel    |  Bin [31m85648[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/secondary-ppc      |  Bin [31m46228[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/secondary-ppc64    |  Bin [31m45680[m -> [32m0[m bytes
 .../apptemplate/prebuilt/secondary-universal       |  Bin [31m180848[m -> [32m0[m bytes
 .../apptemplate/prebuilt/secondary-universal2      |  Bin [31m156428[m -> [32m0[m bytes
 .../py2app/apptemplate/prebuilt/secondary-x86_64   |  Bin [31m56968[m -> [32m0[m bytes
 .../apptemplate/prebuilt/secondary-x86_64-oldsdk   |  Bin [31m36496[m -> [32m0[m bytes
 .../py2app/apptemplate/setup.py                    |  172 [31m--[m
 .../py2app/apptemplate/src/main.c                  | 1259 [31m---------[m
 .../py2app/bootstrap/__init__.py                   |    1 [31m-[m
 .../py2app/bootstrap/argv_emulation.py             |  308 [31m---[m
 .../py2app/bootstrap/argv_inject.py                |    8 [31m-[m
 .../py2app/bootstrap/boot_aliasapp.py              |   48 [31m-[m
 .../py2app/bootstrap/boot_aliasplugin.py           |   52 [31m-[m
 .../py2app/bootstrap/boot_app.py                   |   49 [31m-[m
 .../py2app/bootstrap/boot_plugin.py                |   52 [31m-[m
 .../py2app/bootstrap/chdir_resource.py             |    7 [31m-[m
 .../py2app/bootstrap/ctypes_setup.py               |   10 [31m-[m
 .../py2app/bootstrap/disable_linecache.py          |   11 [31m-[m
 .../py2app/bootstrap/emulate_shell_environment.py  |   88 [31m-[m
 .../py2app/bootstrap/import_encodings.py           |   28 [31m-[m
 .../py2app/bootstrap/path_inject.py                |    4 [31m-[m
 .../py2app/bootstrap/reset_sys_path.py             |   11 [31m-[m
 .../py2app/bootstrap/semi_standalone_path.py       |   24 [31m-[m
 .../py2app/bootstrap/setup_included_subpackages.py |   45 [31m-[m
 .../py2app/bootstrap/setup_pkgresource.py          |   27 [31m-[m
 .../py2app/bootstrap/site_packages.py              |   54 [31m-[m
 .../py2app/bootstrap/system_path_extras.py         |   16 [31m-[m
 .../py2app/bootstrap/virtualenv.py                 |   43 [31m-[m
 .../py2app/bootstrap/virtualenv_site_packages.py   |   48 [31m-[m
 .eggs/py2app-0.28.8-py3.10.egg/py2app/build_app.py | 2663 [31m--------------------[m
 .../py2app/bundletemplate/__init__.py              |    2 [31m-[m
 .../__pycache__/__init__.cpython-310.pyc           |  Bin [31m258[m -> [32m0[m bytes
 .../__pycache__/plist_template.cpython-310.pyc     |  Bin [31m2179[m -> [32m0[m bytes
 .../__pycache__/setup.cpython-310.pyc              |  Bin [31m2589[m -> [32m0[m bytes
 .../py2app/bundletemplate/lib/__error__.sh         |   12 [31m-[m
 .../py2app/bundletemplate/lib/site.py              |  207 [31m--[m
 .../py2app/bundletemplate/plist_template.py        |   66 [31m-[m
 .../py2app/bundletemplate/prebuilt/main-arm64      |  Bin [31m54503[m -> [32m0[m bytes
 .../py2app/bundletemplate/prebuilt/main-fat        |  Bin [31m74684[m -> [32m0[m bytes
 .../py2app/bundletemplate/prebuilt/main-fat3       |  Bin [31m94896[m -> [32m0[m bytes
 .../py2app/bundletemplate/prebuilt/main-i386       |  Bin [31m33352[m -> [32m0[m bytes
 .../py2app/bundletemplate/prebuilt/main-intel      |  Bin [31m66348[m -> [32m0[m bytes
 .../py2app/bundletemplate/prebuilt/main-ppc        |  Bin [31m33724[m -> [32m0[m bytes
 .../py2app/bundletemplate/prebuilt/main-ppc64      |  Bin [31m29520[m -> [32m0[m bytes
 .../py2app/bundletemplate/prebuilt/main-universal  |  Bin [31m127664[m -> [32m0[m bytes
 .../py2app/bundletemplate/prebuilt/main-universal2 |  Bin [31m119868[m -> [32m0[m bytes
 .../py2app/bundletemplate/prebuilt/main-x86_64     |  Bin [31m42480[m -> [32m0[m bytes
 .../py2app/bundletemplate/setup.py                 |  135 [31m-[m
 .../py2app/bundletemplate/src/main.m               |  701 [31m------[m
 .../py2app/converters/__init__.py                  |    3 [31m-[m
 .../py2app/converters/coredata.py                  |   27 [31m-[m
 .../py2app/converters/nibfile.py                   |   50 [31m-[m
 .../py2app/create_appbundle.py                     |   90 [31m-[m
 .../py2app/create_pluginbundle.py                  |   82 [31m-[m
 .../py2app-0.28.8-py3.10.egg/py2app/decorators.py  |   16 [31m-[m
 .eggs/py2app-0.28.8-py3.10.egg/py2app/filters.py   |   89 [31m-[m
 .../py2app/recipes/PIL/__init__.py                 |  106 [31m-[m
 .../PIL/__pycache__/__init__.cpython-310.pyc       |  Bin [31m1898[m -> [32m0[m bytes
 .../py2app/recipes/PIL/prescript.py                |   46 [31m-[m
 .../py2app/recipes/__init__.py                     |   40 [31m-[m
 .../recipes/__pycache__/__init__.cpython-310.pyc   |  Bin [31m1395[m -> [32m0[m bytes
 .../__pycache__/automissing.cpython-310.pyc        |  Bin [31m677[m -> [32m0[m bytes
 .../__pycache__/autopackages.cpython-310.pyc       |  Bin [31m568[m -> [32m0[m bytes
 .../recipes/__pycache__/black.cpython-310.pyc      |  Bin [31m1735[m -> [32m0[m bytes
 .../recipes/__pycache__/ctypes.cpython-310.pyc     |  Bin [31m460[m -> [32m0[m bytes
 .../__pycache__/detect_dunder_file.cpython-310.pyc |  Bin [31m1600[m -> [32m0[m bytes
 .../recipes/__pycache__/ftplib.cpython-310.pyc     |  Bin [31m543[m -> [32m0[m bytes
 .../recipes/__pycache__/gcloud.cpython-310.pyc     |  Bin [31m377[m -> [32m0[m bytes
 .../recipes/__pycache__/lxml.cpython-310.pyc       |  Bin [31m776[m -> [32m0[m bytes
 .../recipes/__pycache__/matplotlib.cpython-310.pyc |  Bin [31m950[m -> [32m0[m bytes
 .../__pycache__/multiprocessing.cpython-310.pyc    |  Bin [31m1117[m -> [32m0[m bytes
 .../recipes/__pycache__/opencv.cpython-310.pyc     |  Bin [31m369[m -> [32m0[m bytes
 .../recipes/__pycache__/pandas.cpython-310.pyc     |  Bin [31m402[m -> [32m0[m bytes
 .../__pycache__/platformdirs.cpython-310.pyc       |  Bin [31m408[m -> [32m0[m bytes
 .../recipes/__pycache__/pydantic.cpython-310.pyc   |  Bin [31m678[m -> [32m0[m bytes
 .../recipes/__pycache__/pydoc.cpython-310.pyc      |  Bin [31m501[m -> [32m0[m bytes
 .../recipes/__pycache__/pyenchant.cpython-310.pyc  |  Bin [31m877[m -> [32m0[m bytes
 .../recipes/__pycache__/pygame.cpython-310.pyc     |  Bin [31m630[m -> [32m0[m bytes
 .../recipes/__pycache__/pylsp.cpython-310.pyc      |  Bin [31m638[m -> [32m0[m bytes
 .../recipes/__pycache__/pyopengl.cpython-310.pyc   |  Bin [31m601[m -> [32m0[m bytes
 .../recipes/__pycache__/pyside.cpython-310.pyc     |  Bin [31m1233[m -> [32m0[m bytes
 .../recipes/__pycache__/pyside2.cpython-310.pyc    |  Bin [31m1482[m -> [32m0[m bytes
 .../recipes/__pycache__/pyside6.cpython-310.pyc    |  Bin [31m1498[m -> [32m0[m bytes
 .../py2app/recipes/__pycache__/qt5.cpython-310.pyc |  Bin [31m1175[m -> [32m0[m bytes
 .../py2app/recipes/__pycache__/qt6.cpython-310.pyc |  Bin [31m1016[m -> [32m0[m bytes
 .../recipes/__pycache__/rtree.cpython-310.pyc      |  Bin [31m673[m -> [32m0[m bytes
 .../recipes/__pycache__/setuptools.cpython-310.pyc |  Bin [31m2780[m -> [32m0[m bytes
 .../recipes/__pycache__/shiboken2.cpython-310.pyc  |  Bin [31m518[m -> [32m0[m bytes
 .../recipes/__pycache__/shiboken6.cpython-310.pyc  |  Bin [31m534[m -> [32m0[m bytes
 .../py2app/recipes/__pycache__/sip.cpython-310.pyc |  Bin [31m3292[m -> [32m0[m bytes
 .../py2app/recipes/__pycache__/six.cpython-310.pyc |  Bin [31m3702[m -> [32m0[m bytes
 .../recipes/__pycache__/sphinx.cpython-310.pyc     |  Bin [31m527[m -> [32m0[m bytes
 .../recipes/__pycache__/sqlalchemy.cpython-310.pyc |  Bin [31m1033[m -> [32m0[m bytes
 .../recipes/__pycache__/sslmod.cpython-310.pyc     |  Bin [31m1306[m -> [32m0[m bytes
 .../__pycache__/sysconfig_module.cpython-310.pyc   |  Bin [31m503[m -> [32m0[m bytes
 .../recipes/__pycache__/tkinter.cpython-310.pyc    |  Bin [31m1792[m -> [32m0[m bytes
 .../recipes/__pycache__/virtualenv.cpython-310.pyc |  Bin [31m2572[m -> [32m0[m bytes
 .../py2app/recipes/__pycache__/wx.cpython-310.pyc  |  Bin [31m564[m -> [32m0[m bytes
 .../py2app/recipes/__pycache__/xml.cpython-310.pyc |  Bin [31m523[m -> [32m0[m bytes
 .../py2app/recipes/__pycache__/zmq.cpython-310.pyc |  Bin [31m624[m -> [32m0[m bytes
 .../py2app/recipes/automissing.py                  |   28 [31m-[m
 .../py2app/recipes/autopackages.py                 |   39 [31m-[m
 .../py2app/recipes/black.py                        |   79 [31m-[m
 .../py2app/recipes/cjkcodecs.py                    |    7 [31m-[m
 .../py2app/recipes/ctypes.py                       |    7 [31m-[m
 .../py2app/recipes/detect_dunder_file.py           |   71 [31m-[m
 .../py2app/recipes/ftplib.py                       |   17 [31m-[m
 .../py2app/recipes/gcloud.py                       |   10 [31m-[m
 .../py2app/recipes/lxml.py                         |   38 [31m-[m
 .../py2app/recipes/matplotlib.py                   |   39 [31m-[m
 .../py2app/recipes/matplotlib_prescript.py         |    3 [31m-[m
 .../py2app/recipes/multiprocessing.py              |   39 [31m-[m
 .../py2app/recipes/opencv.py                       |    6 [31m-[m
 .../py2app/recipes/pandas.py                       |    8 [31m-[m
 .../py2app/recipes/platformdirs.py                 |    8 [31m-[m
 .../py2app/recipes/pydantic.py                     |   40 [31m-[m
 .../py2app/recipes/pydoc.py                        |   19 [31m-[m
 .../py2app/recipes/pyenchant.py                    |   29 [31m-[m
 .../py2app/recipes/pygame.py                       |   13 [31m-[m
 .../py2app/recipes/pylsp.py                        |   17 [31m-[m
 .../py2app/recipes/pyopengl.py                     |   17 [31m-[m
 .../py2app/recipes/pyside.py                       |   53 [31m-[m
 .../py2app/recipes/pyside2.py                      |   60 [31m-[m
 .../py2app/recipes/pyside6.py                      |   60 [31m-[m
 .../py2app/recipes/qt.conf                         |    3 [31m-[m
 .../py2app-0.28.8-py3.10.egg/py2app/recipes/qt5.py |   66 [31m-[m
 .../py2app-0.28.8-py3.10.egg/py2app/recipes/qt6.py |   60 [31m-[m
 .../py2app/recipes/rtree.py                        |   16 [31m-[m
 .../py2app/recipes/setuptools.py                   |   90 [31m-[m
 .../py2app/recipes/shiboken2.py                    |   11 [31m-[m
 .../py2app/recipes/shiboken6.py                    |   11 [31m-[m
 .../py2app-0.28.8-py3.10.egg/py2app/recipes/sip.py |  150 [31m--[m
 .../py2app-0.28.8-py3.10.egg/py2app/recipes/six.py |  148 [31m--[m
 .../py2app/recipes/sphinx.py                       |   15 [31m-[m
 .../py2app/recipes/sqlalchemy.py                   |   46 [31m-[m
 .../py2app/recipes/sslmod.py                       |   52 [31m-[m
 .../py2app/recipes/sysconfig_module.py             |   16 [31m-[m
 .../py2app/recipes/tkinter.py                      |   78 [31m-[m
 .../py2app/recipes/virtualenv.py                   |  120 [31m-[m
 .../py2app-0.28.8-py3.10.egg/py2app/recipes/wx.py  |   18 [31m-[m
 .../py2app-0.28.8-py3.10.egg/py2app/recipes/xml.py |   16 [31m-[m
 .../py2app-0.28.8-py3.10.egg/py2app/recipes/zmq.py |   12 [31m-[m
 .../py2app/script_py2applet.py                     |  217 [31m--[m
 .eggs/py2app-0.28.8-py3.10.egg/py2app/util.py      |  907 [31m-------[m
 MVP/View/__pycache__/view.cpython-310.pyc          |  Bin [31m2156[m -> [32m2129[m bytes
 MVP/View/view.py                                   |   12 [32m+[m[31m-[m
 265 files changed, 8 insertions(+), 22405 deletions(-)

[33mcommit 209e37da4a6856a1c7112bf0c209268b7f3944fa[m
Author: [1;31mlin1397[m <[1;31mlin1397[m@purdue.edu>
Date:   Tue Feb 11 15:47:43 2025 -0500

    Prevent writing in home screen

 .eggs/README.txt                                   |    6 [32m+[m
 .eggs/altgraph-0.17.4-py3.10.egg/EGG-INFO/LICENSE  |   18 [32m+[m
 .eggs/altgraph-0.17.4-py3.10.egg/EGG-INFO/PKG-INFO |  293 [32m+++[m
 .eggs/altgraph-0.17.4-py3.10.egg/EGG-INFO/RECORD   |   13 [32m+[m
 .eggs/altgraph-0.17.4-py3.10.egg/EGG-INFO/WHEEL    |    6 [32m+[m
 .../EGG-INFO/top_level.txt                         |    1 [32m+[m
 .eggs/altgraph-0.17.4-py3.10.egg/EGG-INFO/zip-safe |    1 [32m+[m
 .eggs/altgraph-0.17.4-py3.10.egg/altgraph/Dot.py   |  321 [32m+++[m
 .eggs/altgraph-0.17.4-py3.10.egg/altgraph/Graph.py |  682 [32m+++++[m
 .../altgraph/GraphAlgo.py                          |  171 [32m++[m
 .../altgraph/GraphStat.py                          |   73 [32m+[m
 .../altgraph/GraphUtil.py                          |  139 [32m+[m
 .../altgraph/ObjectGraph.py                        |  212 [32m++[m
 .../altgraph/__init__.py                           |  148 [32m++[m
 .../altgraph/__pycache__/Graph.cpython-310.pyc     |  Bin [31m0[m -> [32m19650[m bytes
 .../altgraph/__pycache__/GraphUtil.cpython-310.pyc |  Bin [31m0[m -> [32m3207[m bytes
 .../__pycache__/ObjectGraph.cpython-310.pyc        |  Bin [31m0[m -> [32m6949[m bytes
 .../altgraph/__pycache__/__init__.cpython-310.pyc  |  Bin [31m0[m -> [32m5345[m bytes
 .eggs/macholib-1.16.3-py3.10.egg/EGG-INFO/LICENSE  |   21 [32m+[m
 .eggs/macholib-1.16.3-py3.10.egg/EGG-INFO/PKG-INFO |  453 [32m++++[m
 .eggs/macholib-1.16.3-py3.10.egg/EGG-INFO/RECORD   |   24 [32m+[m
 .eggs/macholib-1.16.3-py3.10.egg/EGG-INFO/WHEEL    |    6 [32m+[m
 .../EGG-INFO/entry_points.txt                      |    4 [32m+[m
 .../EGG-INFO/requires.txt                          |    1 [32m+[m
 .../EGG-INFO/top_level.txt                         |    1 [32m+[m
 .eggs/macholib-1.16.3-py3.10.egg/EGG-INFO/zip-safe |    1 [32m+[m
 .eggs/macholib-1.16.3-py3.10.egg/macholib/MachO.py |  500 [32m++++[m
 .../macholib/MachOGraph.py                         |  141 [32m++[m
 .../macholib/MachOStandalone.py                    |  181 [32m++[m
 .../macholib/SymbolTable.py                        |  104 [32m+[m
 .../macholib/__init__.py                           |    8 [32m+[m
 .../macholib/__main__.py                           |   80 [32m+[m
 .../macholib/__pycache__/MachO.cpython-310.pyc     |  Bin [31m0[m -> [32m10821[m bytes
 .../__pycache__/MachOGraph.cpython-310.pyc         |  Bin [31m0[m -> [32m4401[m bytes
 .../__pycache__/MachOStandalone.cpython-310.pyc    |  Bin [31m0[m -> [32m5365[m bytes
 .../macholib/__pycache__/__init__.cpython-310.pyc  |  Bin [31m0[m -> [32m345[m bytes
 .../macholib/__pycache__/dyld.cpython-310.pyc      |  Bin [31m0[m -> [32m5239[m bytes
 .../macholib/__pycache__/dylib.cpython-310.pyc     |  Bin [31m0[m -> [32m1171[m bytes
 .../macholib/__pycache__/framework.cpython-310.pyc |  Bin [31m0[m -> [32m1308[m bytes
 .../__pycache__/itergraphreport.cpython-310.pyc    |  Bin [31m0[m -> [32m2109[m bytes
 .../macholib/__pycache__/mach_o.cpython-310.pyc    |  Bin [31m0[m -> [32m40886[m bytes
 .../macholib/__pycache__/ptypes.cpython-310.pyc    |  Bin [31m0[m -> [32m9168[m bytes
 .../macholib/__pycache__/util.cpython-310.pyc      |  Bin [31m0[m -> [32m7399[m bytes
 .../macholib/_cmdline.py                           |   49 [32m+[m
 .eggs/macholib-1.16.3-py3.10.egg/macholib/dyld.py  |  228 [32m++[m
 .eggs/macholib-1.16.3-py3.10.egg/macholib/dylib.py |   45 [32m+[m
 .../macholib/framework.py                          |   45 [32m+[m
 .../macholib/itergraphreport.py                    |   73 [32m+[m
 .../macholib-1.16.3-py3.10.egg/macholib/mach_o.py  | 1641 [32m++++++++++++[m
 .../macholib/macho_dump.py                         |   57 [32m+[m
 .../macholib/macho_find.py                         |   22 [32m+[m
 .../macholib/macho_standalone.py                   |   30 [32m+[m
 .../macholib-1.16.3-py3.10.egg/macholib/ptypes.py  |  334 [32m+++[m
 .eggs/macholib-1.16.3-py3.10.egg/macholib/util.py  |  262 [32m++[m
 .../modulegraph-0.19.6-py3.10.egg/EGG-INFO/LICENSE |   16 [32m+[m
 .../EGG-INFO/PKG-INFO                              |  523 [32m++++[m
 .../modulegraph-0.19.6-py3.10.egg/EGG-INFO/RECORD  |   14 [32m+[m
 .eggs/modulegraph-0.19.6-py3.10.egg/EGG-INFO/WHEEL |    6 [32m+[m
 .../EGG-INFO/entry_points.txt                      |    2 [32m+[m
 .../EGG-INFO/requires.txt                          |    2 [32m+[m
 .../EGG-INFO/top_level.txt                         |    1 [32m+[m
 .../EGG-INFO/zip-safe                              |    1 [32m+[m
 .../modulegraph/__init__.py                        |    1 [32m+[m
 .../modulegraph/__main__.py                        |  118 [32m+[m
 .../__pycache__/__init__.cpython-310.pyc           |  Bin [31m0[m -> [32m208[m bytes
 .../modulegraph/__pycache__/_imp.cpython-310.pyc   |  Bin [31m0[m -> [32m2293[m bytes
 .../__pycache__/find_modules.cpython-310.pyc       |  Bin [31m0[m -> [32m6958[m bytes
 .../__pycache__/modulegraph.cpython-310.pyc        |  Bin [31m0[m -> [32m51114[m bytes
 .../modulegraph/__pycache__/util.cpython-310.pyc   |  Bin [31m0[m -> [32m2886[m bytes
 .../modulegraph/__pycache__/zipio.cpython-310.pyc  |  Bin [31m0[m -> [32m6348[m bytes
 .../modulegraph/_imp.py                            |   90 [32m+[m
 .../modulegraph/find_modules.py                    |  326 [32m+++[m
 .../modulegraph/modulegraph.py                     | 2295 [32m+++++++++++++++++[m
 .../modulegraph/util.py                            |  133 [32m+[m
 .../modulegraph/zipio.py                           |  379 [32m+++[m
 .../py2app-0.28.8-py3.10.egg/EGG-INFO/LICENSE.txt  |   11 [32m+[m
 .eggs/py2app-0.28.8-py3.10.egg/EGG-INFO/PKG-INFO   | 2027 [32m+++++++++++++++[m
 .eggs/py2app-0.28.8-py3.10.egg/EGG-INFO/RECORD     |  133 [32m+[m
 .eggs/py2app-0.28.8-py3.10.egg/EGG-INFO/WHEEL      |    6 [32m+[m
 .../EGG-INFO/entry_points.txt                      |   17 [32m+[m
 .../py2app-0.28.8-py3.10.egg/EGG-INFO/requires.txt |    4 [32m+[m
 .../EGG-INFO/top_level.txt                         |    1 [32m+[m
 .eggs/py2app-0.28.8-py3.10.egg/py2app/__init__.py  |   35 [32m+[m
 .../py2app/__pycache__/__init__.cpython-310.pyc    |  Bin [31m0[m -> [32m1432[m bytes
 .../py2app/__pycache__/_pkg_meta.cpython-310.pyc   |  Bin [31m0[m -> [32m2846[m bytes
 .../py2app/__pycache__/build_app.cpython-310.pyc   |  Bin [31m0[m -> [32m57206[m bytes
 .../__pycache__/create_appbundle.cpython-310.pyc   |  Bin [31m0[m -> [32m2076[m bytes
 .../create_pluginbundle.cpython-310.pyc            |  Bin [31m0[m -> [32m1988[m bytes
 .../py2app/__pycache__/filters.cpython-310.pyc     |  Bin [31m0[m -> [32m2003[m bytes
 .../py2app/__pycache__/util.cpython-310.pyc        |  Bin [31m0[m -> [32m21120[m bytes
 .eggs/py2app-0.28.8-py3.10.egg/py2app/_pkg_meta.py |  120 [32m+[m
 .../py2app/apptemplate/__init__.py                 |    2 [32m+[m
 .../__pycache__/__init__.cpython-310.pyc           |  Bin [31m0[m -> [32m255[m bytes
 .../__pycache__/plist_template.cpython-310.pyc     |  Bin [31m0[m -> [32m1982[m bytes
 .../apptemplate/__pycache__/setup.cpython-310.pyc  |  Bin [31m0[m -> [32m3018[m bytes
 .../py2app/apptemplate/lib/__error__.sh            |   19 [32m+[m
 .../py2app/apptemplate/lib/site.py                 |  204 [32m++[m
 .../py2app/apptemplate/plist_template.py           |   61 [32m+[m
 .../py2app/apptemplate/prebuilt/main-arm64         |  Bin [31m0[m -> [32m74711[m bytes
 .../py2app/apptemplate/prebuilt/main-asl-arm64     |  Bin [31m0[m -> [32m74971[m bytes
 .../py2app/apptemplate/prebuilt/main-asl-i386      |  Bin [31m0[m -> [32m44816[m bytes
 .../py2app/apptemplate/prebuilt/main-asl-intel     |  Bin [31m0[m -> [32m85968[m bytes
 .../apptemplate/prebuilt/main-asl-universal2       |  Bin [31m0[m -> [32m156892[m bytes
 .../py2app/apptemplate/prebuilt/main-asl-x86_64    |  Bin [31m0[m -> [32m57432[m bytes
 .../py2app/apptemplate/prebuilt/main-fat           |  Bin [31m0[m -> [32m99716[m bytes
 .../py2app/apptemplate/prebuilt/main-fat3          |  Bin [31m0[m -> [32m131928[m bytes
 .../py2app/apptemplate/prebuilt/main-i386          |  Bin [31m0[m -> [32m44648[m bytes
 .../py2app/apptemplate/prebuilt/main-intel         |  Bin [31m0[m -> [32m85776[m bytes
 .../py2app/apptemplate/prebuilt/main-ppc           |  Bin [31m0[m -> [32m46468[m bytes
 .../py2app/apptemplate/prebuilt/main-ppc64         |  Bin [31m0[m -> [32m45936[m bytes
 .../py2app/apptemplate/prebuilt/main-universal     |  Bin [31m0[m -> [32m181104[m bytes
 .../py2app/apptemplate/prebuilt/main-universal2    |  Bin [31m0[m -> [32m156636[m bytes
 .../py2app/apptemplate/prebuilt/main-x86_64        |  Bin [31m0[m -> [32m57240[m bytes
 .../py2app/apptemplate/prebuilt/main-x86_64-oldsdk |  Bin [31m0[m -> [32m36816[m bytes
 .../py2app/apptemplate/prebuilt/secondary-arm64    |  Bin [31m0[m -> [32m74508[m bytes
 .../py2app/apptemplate/prebuilt/secondary-fat      |  Bin [31m0[m -> [32m99476[m bytes
 .../py2app/apptemplate/prebuilt/secondary-fat3     |  Bin [31m0[m -> [32m131696[m bytes
 .../py2app/apptemplate/prebuilt/secondary-i386     |  Bin [31m0[m -> [32m44540[m bytes
 .../py2app/apptemplate/prebuilt/secondary-intel    |  Bin [31m0[m -> [32m85648[m bytes
 .../py2app/apptemplate/prebuilt/secondary-ppc      |  Bin [31m0[m -> [32m46228[m bytes
 .../py2app/apptemplate/prebuilt/secondary-ppc64    |  Bin [31m0[m -> [32m45680[m bytes
 .../apptemplate/prebuilt/secondary-universal       |  Bin [31m0[m -> [32m180848[m bytes
 .../apptemplate/prebuilt/secondary-universal2      |  Bin [31m0[m -> [32m156428[m bytes
 .../py2app/apptemplate/prebuilt/secondary-x86_64   |  Bin [31m0[m -> [32m56968[m bytes
 .../apptemplate/prebuilt/secondary-x86_64-oldsdk   |  Bin [31m0[m -> [32m36496[m bytes
 .../py2app/apptemplate/setup.py                    |  172 [32m++[m
 .../py2app/apptemplate/src/main.c                  | 1259 [32m+++++++++[m
 .../py2app/bootstrap/__init__.py                   |    1 [32m+[m
 .../py2app/bootstrap/argv_emulation.py             |  308 [32m+++[m
 .../py2app/bootstrap/argv_inject.py                |    8 [32m+[m
 .../py2app/bootstrap/boot_aliasapp.py              |   48 [32m+[m
 .../py2app/bootstrap/boot_aliasplugin.py           |   52 [32m+[m
 .../py2app/bootstrap/boot_app.py                   |   49 [32m+[m
 .../py2app/bootstrap/boot_plugin.py                |   52 [32m+[m
 .../py2app/bootstrap/chdir_resource.py             |    7 [32m+[m
 .../py2app/bootstrap/ctypes_setup.py               |   10 [32m+[m
 .../py2app/bootstrap/disable_linecache.py          |   11 [32m+[m
 .../py2app/bootstrap/emulate_shell_environment.py  |   88 [32m+[m
 .../py2app/bootstrap/import_encodings.py           |   28 [32m+[m
 .../py2app/bootstrap/path_inject.py                |    4 [32m+[m
 .../py2app/bootstrap/reset_sys_path.py             |   11 [32m+[m
 .../py2app/bootstrap/semi_standalone_path.py       |   24 [32m+[m
 .../py2app/bootstrap/setup_included_subpackages.py |   45 [32m+[m
 .../py2app/bootstrap/setup_pkgresource.py          |   27 [32m+[m
 .../py2app/bootstrap/site_packages.py              |   54 [32m+[m
 .../py2app/bootstrap/system_path_extras.py         |   16 [32m+[m
 .../py2app/bootstrap/virtualenv.py                 |   43 [32m+[m
 .../py2app/bootstrap/virtualenv_site_packages.py   |   48 [32m+[m
 .eggs/py2app-0.28.8-py3.10.egg/py2app/build_app.py | 2663 [32m++++++++++++++++++++[m
 .../py2app/bundletemplate/__init__.py              |    2 [32m+[m
 .../__pycache__/__init__.cpython-310.pyc           |  Bin [31m0[m -> [32m258[m bytes
 .../__pycache__/plist_template.cpython-310.pyc     |  Bin [31m0[m -> [32m2179[m bytes
 .../__pycache__/setup.cpython-310.pyc              |  Bin [31m0[m -> [32m2589[m bytes
 .../py2app/bundletemplate/lib/__error__.sh         |   12 [