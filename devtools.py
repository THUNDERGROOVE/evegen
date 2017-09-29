def Bootstrap(a, b):
    import marshal
    import imp
    import sys
    import svc
    import service
    import types
    import form
    import nasty



    insiderClass = 'hexex::insider.py' #This will get replaced with the actual hex encoded code
    code = marshal.loads(insiderClass.decode('hex'))
    insider = imp.new_module('insider')
    exec code in insider.__dict__, None
    setattr(svc, 'insider', insider.insider)
    sm.StopService('insider')
    sm.StartService('insider')

    devWindowClass = 'hexex::devToolsWindow.py'
    devConsoleClass = 'hexex::devToolsConsole.py'

    code2 = marshal.loads(devWindowClass.decode('hex'))
    DevWindow = imp.new_module("DevWindow")
    exec code2 in DevWindow.__dict__, None
    #setattr(form, "DevWindow", DevWindow.DevWindow)
    nasty.nasty.RegisterNamedObject(DevWindow.DevWindow, "form", "DevWindow", "devtools.py", globals())

    code3 = marshal.loads(devConsoleClass.decode('hex'))
    ConsoleWindow = imp.new_module("ConsoleWindow")
    exec code3 in ConsoleWindow.__dict__, None
    nasty.nasty.RegisterNamedObject(ConsoleWindow.ConsoleWindow, "form", "ConsoleWindow", "devtools.py", globals())

    script = 'def evemuLoad():\n\tsm.StartService("insider")'
    code = compile(script, '<script>', 'exec')
    data = marshal.dumps(code)
    exec marshal.loads(data) in None, None
    a.Loader = evemuLoad

