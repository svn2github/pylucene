
import sys

global JAVAHOME
JAVAHOME = None

if sys.platform == "win32":
    # figure out where the JDK lives

    try:
        import _winreg as wreg

        class WindowsRegistry:
            # see the Python Cookbook, #146305, Dirk Holtwick

            def __init__(self, keyname):
                " handle registry access "
                self.reg = wreg.ConnectRegistry(None, wreg.HKEY_LOCAL_MACHINE)
                self.key = wreg.OpenKey(self.reg, keyname)

            def get(self, name):
                " get value out of registry "
                v, t = wreg.QueryValueEx(self.key, name)
                return v, t

            def close(self):
                " close the key finally "
                self.key.Close()
                self.reg.Close()

            def __del__(self):
                self.close()

        def get_registry_value(vname, subname):
            r = WindowsRegistry(vname)
            v, t = r.get(subname)
            return v

        javaversion = get_registry_value(r"SOFTWARE\JavaSoft\Java Development Kit", "CurrentVersion")
        JAVAHOME = get_registry_value(r"SOFTWARE\JavaSoft\Java Development Kit\%s" % javaversion, "JavaHome")

    except:
        JAVAHOME = 'c:/Program Files/Java/jdk1.6.0_18'
