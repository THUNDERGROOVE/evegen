#@liveupdate("globalClassMethod", "uicls.CharacterCreationLayer::CharacterCreationLayer", "AskForPortraitConfirmation")
#@patchinfo("AskForPortraitConfirmation", "Patch to fix photo uploads on char creation")
def AskForPortraitConfirmation(self, *args):
    photo = self.GetActivePortrait()
    snapPath = self.GetPortraitSnapshotPath(self.activePortraitIndex)
    photoFile = open(snapPath, "rb")
    photoData = photoFile.read()
    photoFile.close()
    eve.Message('CustomNotify', {'notify': 'Uploading your character portrait to EVEMu'})
    result = sm.RemoteSvc("photoUploadSvc").Upload(photoData)
    if ((result is None) or (result == False)):
        eve.Message('CustomNotify', {'notify': 'Portrait upload failed!'})
    else:
        eve.Message('CustomNotify', {'notify': 'Portrait upload successful!'})
        return True
