import uicls
import uiconst

# sm.GetService("cmd").commandMap.AddCommand(util.CommandMap(form.DevWindow.Show, (uiconst.VK_CONTROL, uiconst.VK_D)))
class DevWindow(uicls.Window):
    __guid__ = "form.DevWindow"
    default_windowID = "DevWindow"
    default_width = 450
    default_height = 300
    default_topParentHeight = 0
    default_minSize = (default_width, default_height)
    console_state = 0

    def ApplyAttributes(self, attributes):
        import uicls
        import uiconst
        uicls.Window.ApplyAttributes(self, attributes)
        uicls.Button(parent=self.sr.maincontainer, align=uiconst.TOLEFT, label="UIDebugger", func=self.OpenUIDebugger)
        uicls.Button(parent=self.sr.maincontainer, align=uiconst.TOLEFT, label="Dungeon Editor", func=self.OpenDungeonEditor)
        uicls.Button(parent=self.sr.maincontainer, align=uiconst.TOLEFT, label="Paint Direction Vectors", func=self.StartPaintingDirectionVectors)

        #uicls.Button(self.sr.maincontainer, align=uiconst.TOLEFT, label="Camera Settings", func=self.OpenCameraSettings)
        uicls.Button(parent=self.sr.maincontainer, align=uiconst.TOLEFT, label="Start RC", func=self.ToggleRemoteConsole)

    def OpenUIDebugger(self, a):
        import form
        form.UIDebugger.Open()

    def OpenDungeonEditor(self, a):
        import form
        form.DungeonEditor.Open()

    def OpenCameraSettings(self, a):
        import cameras
        cameras.DebugChangeCameraSettingsWindow.Open()
    def StartPaintingDirectionVectors(self, a):
        from log import LogError
        import uix
	import uiutil
	import mathUtil
	import xtriui
	import uthread
	import form
	import blue
	import util
	import spaceObject
	import trinity
	import service
	import destiny
	import listentry
	import base
	import math
	import sys
	import geo2
	import maputils
	import copy
	from math import pi, cos, sin, sqrt, floor
	from foo import Vector3
	from mapcommon import SYSTEMMAP_SCALE
	from traceback import format_exception
	import functools
	import uiconst
	import uicls
	import listentry
	import state
	import localization
	import localizationUtil
	
	def safetycheck(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except:
                    try:
                        print "exception in " + func.__name__
                        (exc, e, tb,) = sys.exc_info()
                        result2 = (''.join(format_exception(exc, e, tb)) + '\n').replace('\n', '<br>')
                        #sm.GetService('gameui').MessageBox(result2, "ProbeHelper Exception")
                        sm.GetService('FxSequencer').LogError(result2)
                    except:
                        print "exception in safetycheck"
            return wrapper

	@safetycheck
	def WarpToStuff(ItemID):
            sm.services["michelle"].GetRemotePark().CmdWarpToStuff("item", ItemID, 50000)	
		
	@safetycheck
	def GetBallPark():
            bp = sm.GetService('michelle').GetBallpark()
            while(not bp):
                blue.pyos.synchro.Sleep(5000)
                bp = sm.GetService('michelle').GetBallpark()
            return bp	

	@safetycheck
	def LogMessage(Message_Text):
		sm.GetService('gameui').Say(Message_Text)
	
	@safetycheck
	def ShowAllPaths():
            bp = GetBallPark()
            myball = bp.GetBall(eve.session.shipid)	
            if not myball:
                LogMessage("ball doesnt exist")
                return
            if bp:
                balls = copy.copy(bp.balls)
                LogMessage("Copied Ballpark")
            else:
                LogMessage("Invalid Ballpark")
                
                
            tacticalSvc = sm.GetService("tactical")
            tacticalSvc.circles.ClearLines()
            color = (0.25,0.25,0.25,1)
                
            i = 0
            for qq in range(500):
                blue.pyos.synchro.Sleep(500)
                tacticalSvc.circles.ClearLines()
                for ballid in balls.iterkeys():
                    ball = bp.GetBall(ballid)
                    slimItem = bp.GetInvItem(ballid) 
                    if (ball.maxVelocity != 0):
                        currentDirection = ball.GetQuaternionAt(blue.os.GetTime())
                        d = trinity.TriVector(0,0,1)
                        d.TransformQuaternion(currentDirection)
                        #LogMessage(str(d.x) + " " + str(d.y) + "  " + str(d.z))
                        d.x = d.x*10000
                        d.y = d.y*10000
                        d.z = d.z*10000
                        LogMessage(str(d.x) + " " + str(d.y) + "  " + str(d.z))
                        RelPosBallX = (ball.x-myball.x)
                        RelPosBallY = (ball.y-myball.y)
                        RelPosBallZ = (ball.z-myball.z)
					
                        tacticalSvc.circles.AddLine((RelPosBallX,RelPosBallY,RelPosBallZ),color,(RelPosBallX+d.x,RelPosBallY+d.y,RelPosBallZ+d.z),color)
                        tacticalSvc.circles.SubmitChanges()
		i=i+1
        try:
            uthread.new(ShowAllPaths)
	except:
		LogMessage("error")

    def ToggleRemoteConsole(self, a):
        import uicls
        import uiconst

        self.sr.maincontainer.children.remove(self.sr.maincontainer.children[9]) # TODO: Nick: Fix this hardcoded garbage if possible
        if self.console_state == 0:
            uicls.Button(parent=self.sr.maincontainer, align=uiconst.TOLEFT, label="RC Running..", func=self.ToggleRemoteConsole)
            self.console_state = 1
            sm.GetService("insider").start_remote_console()
            
            



