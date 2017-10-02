#@liveupdate("globalClassMethod", "svc.tutorial::TutorialSvc", "GetTutorials")
#@patchinfo("GetTutorials", "Disable tutorials whenever accessed.  They cause issues")
def GetTutorials(self):
    import __builtin__
    eve.Message("CustomNotify", {"notify": "Disabling tutorials"})
    __builtin__.settings.Get("char").Set("ui", "showTutorials", 0)
    eve.Message("CustomNotify", {"notify": "Tutorials disabled!"})
    return {}
