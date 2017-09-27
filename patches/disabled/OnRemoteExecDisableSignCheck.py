#@liveupdate("globalClassMethod", "svc.debug::debugSvc", "OnRemoteExec")
def OnRemoteExec(self, signedCode):
    eve.Message("CustomNotify", {"notify": "OnRemoteExec called"})
    # No need to check if we're a client!
    code = marshal.loads(signedCode)
    self._Exec(code, {})
