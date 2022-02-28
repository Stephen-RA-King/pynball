# Core Library modules
import os
import subprocess
import winreg


class VarControl:
    def __init__(self):
        self.env_variables = os.environ
        self.environment = os.name
        self.user_key = winreg.HKEY_CURRENT_USER
        self.user_subkey = "Environment"
        self.system_key = winreg.HKEY_LOCAL_MACHINE
        self.system_subkey = (
            r"System\CurrentControlSet\Control\Session Manager\Environment"
        )

    @staticmethod
    def _execute(*args, supress_exception=False):
        print(args)
        try:
            proc = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            out, err = proc.communicate()
            decoded_out = out.decode("utf-8")
            decoded_err = err.decode("utf-8")
            if err and not supress_exception:
                raise Exception(decoded_err)
            else:
                return decoded_out
        except OSError as e:
            print(e)

    def setenv(self, scope, name, value):
        if scope != "user" and scope != "system":
            print("Scope value must be 'user' or 'system'")
            return
        if scope == "user":
            key = winreg.OpenKey(
                self.user_key, self.user_subkey, 0, winreg.KEY_ALL_ACCESS
            )
        elif scope == "system":
            key = winreg.OpenKey(
                self.system_key, self.system_subkey, 0, winreg.KEY_ALL_ACCESS
            )
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)  # noqa
        winreg.CloseKey(key)

    def getenv(self, scope, name):
        """No need to open the key as they are one of the predefined
        HKEY_* constants.
        """
        if scope != "user" and scope != "system":
            print("Scope value must be 'user' or 'system'")
            return
        elif scope == "user":
            key = winreg.CreateKey(self.user_key, self.user_subkey)
        elif scope == "system":
            key = winreg.CreateKey(self.system_key, self.system_subkey)
        value, _ = winreg.QueryValueEx(key, name)  # noqa
        return value

    def deletenv(self, scope, name):
        """No need to open the key as they are one of the predefined
        HKEY_* constants.
        """
        if scope != "user" and scope != "system":
            print("Scope value must be 'user' or 'system'")
            return
        elif scope == "user":
            key = winreg.CreateKey(self.user_key, self.user_subkey)
        elif scope == "system":
            key = winreg.CreateKey(self.system_key, self.system_subkey)
        try:
            winreg.DeleteValue(key, name)  # noqa
        except OSError as e:
            print(f"Deletion of key: '{name}' failed -\n {e}")


x = VarControl()
x.setenv("system", "STEVE", "123")
x.setenv("user", "STEVE", "456")
print(x.getenv("system", "STEVE"))
print(x.getenv("user", "STEVE"))
x.deletenv("system", "STEVE")
x.deletenv("user", "STEVE")
