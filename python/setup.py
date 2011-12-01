import sys

print "Your platform is",sys.platform

manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity version="1.0.0.0" processorArchitecture="X86" name="*.*.*" type="win32" />
<description>*</description>
<dependency>
<dependentAssembly>
<assemblyIdentity type="win32" name="Microsoft.Windows.Common-Controls"
 version="6.0.0.0" processorArchitecture="X86" publicKeyToken="6595b64144ccf1df" language="*" />
</dependentAssembly>
</dependency>
 <dependency>
 <dependentAssembly>
  <assemblyIdentity type="win32" name="Microsoft.VC90.CRT" version="9.0.30729.4148" processorArchitecture="x86" publicKeyToken="1fc8b3b9a1e18e3b" /> 
  </dependentAssembly>
  </dependency>
</assembly>
"""


sys.path.append('src')
if sys.platform == 'win32' or sys.platform == 'linux2':
    from distutils.core import setup
    import py2exe

    try:
        # if this doesn't work, try import modulefinder
        import py2exe.mf as modulefinder
        import win32com
        for p in win32com.__path__[1:]:
            modulefinder.AddPackagePath("win32com", p)
        for extra in ["win32com.shell"]: #,"win32com.mapi"
            __import__(extra)
            m = sys.modules[extra]
            for p in m.__path__[1:]:
                modulefinder.AddPackagePath(extra, p)
    except ImportError:
        # no build path setup, no worries.
        pass


    setup(
        options={"py2exe":
                     {"optimize": 2,
                      "compressed" : False,
                      "packages" : ['evec_upload'],
                      "dll_excludes" : ['msvcp90.dll', 'powrprof.dll', 'api-ms-win-core-localregistry-l1-1-0.dll', 
                                        'api-ms-win-core-processthreads-l1-1-0.dll', 'api-ms-win-security-base-l1-1-0.dll']
                      }
                 },
        windows= [ {
                "script": "src/uploader.py",
                "icon_resources": [(1, "images/evec_all.ico")] ,
                "other_resources": [(24,1,manifest)]
                }
            ],
        data_files=["images/evec_all.ico"]
        )

elif sys.platform == 'darwin':
    from setuptools import setup
    buildstyle = 'app'

    setup(
        app=[ 'src/uploader.py' ],
        options=dict( py2app=dict(
                optimize=2,
                iconfile='images/evec_mac.icns'
                ) ),
        name="evec_upload",
        setup_requires=["py2app"],
        )
