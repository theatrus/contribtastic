from distutils.core import setup
import py2exe

manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
manifestVersion="1.0">
<assemblyIdentity

    version="0.64.1.0"
    processorArchitecture="x86"
    name="Controls"
    type="win32"

/>
<description>myProgram</description>
<dependency>

    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>

</dependency>
</assembly>
"""

setup(
    options={"py2exe":{"optimize":2}},

    windows=
[
{ 
            "script": "evec_upload.py", 
            "icon_resources": [(1, "evec_all.ico")] ,
            "other_resources": [(24,1,manifest)]
        }
]
)
