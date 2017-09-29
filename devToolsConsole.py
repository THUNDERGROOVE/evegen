import uicls
import uiconst

class ConsoleWindow(uicls.Window):
    __guid__ = "form.Console"
    default_windowID = "Console"
    default_width = 450
    default_height = 300
    default_topParentHeight = 0
    default_minSize = (default_width, default_height)



    def write(self, txt):
        import listentry
        self.sr.scroll.AddNode(-1, listentry.Get("Text", {"text": txt, "line": 1}))

    def ApplyAttributes(self, attributes):
        import uicls
        import uiutil
        import uiconst
        import sys
        sys.stdout = self
        uicls.Window.ApplyAttributes(self, attributes)
        scroll = uicls.Scroll(parent=uiutil.GetChild(self, 'main'), padding=2)
        self.sr.scroll = scroll
        self.edit = uicls.SinglelineEdit(name="", readonly=False, parent=self.sr.maincontainer, align=uiconst.RELATIVE, pos=(2, 2, 150, 25), padding=(0,0,0,0))
        self.edit.OnReturn = self.EnterPressed

    def EnterPressed(self, *args):
       val = self.edit.GetValue() 
       exec(val + "\n")

