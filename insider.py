import service
import marshal
import types
import log
import socket
import stackless
import code
import sys

# Thanks to t0st for the console code \0/
# TODO: Nick Pull remote console into it's own service.

class insider(service.Service):
    __guid__ = 'svc.insider'
    __displayname__ = 'Evemu Insider Service'
    __notifyevents__ = ['OnSessionChanged']

    # socket wrapper
    class probe_sw():
        def __init__(self, s):
            self.s = s
        def read(self, len):
            return self.s.recv(len)
        def write(self, str):
            return self.s.send(str)
        def readline(self):
            return self.read(256) # lazy implementation for quick testing
    
    def __init__(self):
        service.Service.__init__(self)
        
    def OnSessionChanged(self, isRemote, sess, change):
        self.LogInfo('On Session Change In Insider')
                
    def Show(self, argOne, argTwo):
        self.LogInfo('Insider Show Was Called')
        import form
        form.DevWindow.Open()
        sm.GetService("registry").GetWindow("devwindow").Minimize()

    def start_remote_console(self):
        import socket
        import stackless
        self.LogInfo("Starting remote console on port 2112")
        # listening socket
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('127.0.0.1', 2112))
        self.s.listen(3)
        
        # k, go!
        #stackless.tasklet(probe_accept)(probe_sock)
        #stackless.run()
        
        #self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        stackless.tasklet(self.probe_accept)()

    def probe_accept(self):
        import socket
        import stackless
        import code
        import sys
        while True:
            c, a = self.s.accept()
            c = self.probe_sw(c)
            
            sys.stdin = c
            sys.stdout = c
            sys.stderr = c
            
            # should break if connection is dropped
            try:
                code.interact()
            except:
                pass
        
            # I wanted to kill the socket on clean exit()
            # but it doesn't seem to work?
            try:
                c.s.shutdown(SHUT_RDWR)
                c.s.close()
            except:
                pass
            
            # restore original stds
            sys.stdin = sys.__stdin__
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        
            stackless.schedule()

    def probe_connect(self):
        import socket
        import stackless
        import code
        import sys

        self.s.connect(("127.0.0.1", 2112))
        c = self.probe_sw(self.s)

        sys.stdin = c
        sys.stdout = c
        sys.stderr = c
        # should break if connection is dropped
        try:
            code.interact()
        except:
            pass
        # restore original stds
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        stackless.schedule()

