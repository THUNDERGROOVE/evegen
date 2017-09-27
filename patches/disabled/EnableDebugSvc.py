# WindowMgr.GetWindowColors seemed like a good entry point?
#@liveupdate("globalClassMethod", "svc.window::WindowMgr", "GetWindowColors")
def GetWindowColors(self):
    if getattr(self, "__debugPatched__", None) == None:
        sm.StartService("debug") # maybe something can be hacked together with sm.GetService("debugSvc")._ExecConsole()
        setattr(self, "__debugPatched__", True)
    return (settings.user.windows.Get("wndColor", eve.themeColor),
            settings.user.windows.Get("wndBackgroundcolor", eve.themeBgColor),
            settings.user.windows.Get("wndComponent", eve.themeCompColor),
            settings.user.windows.Get("wndComponentsub", eve.themeCompSubColor)
    )
