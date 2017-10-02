#@liveupdate("globalClassMethod", "form.LSCChannel::Channel", "InputKeyUp")
#@patchinfo("InputKeyUp", "Allow / in chat without svc_slash")
def InputKeyUp(self, *args):
    import blue
    shift = uicore.uilib.Key(uiconst.VK_SHIFT)
    if shift:
        return 
    if self.waitingForReturn and blue.os.GetWallclockTime() - self.waitingForReturn < MIN:
        txt = self.input.GetValue(html=0)
        txt = txt.rstrip()
        cursorPos = -1
        self.input.SetValue(txt, cursorPos=cursorPos)
        eve.Message('uiwarning03')
        return 
    NUM_SECONDS = 4
    if session.userType == 23 and (type(self.channelID) != types.IntType or self.channelID < 2100000000 and self.channelID > 0):
        lastMessageTime = long(getattr(self, 'lastMessageTime', blue.os.GetWallclockTime() - 1 * MIN))
        if blue.os.GetWallclockTime() - lastMessageTime < NUM_SECONDS * SEC:
            eve.Message('LSCTrialRestriction_SendMessage', {'sec': (NUM_SECONDS * SEC - (blue.os.GetWallclockTime() - lastMessageTime)) / SEC})
            return 
        setattr(self, 'lastMessageTime', blue.os.GetWallclockTime())
    txt = self.input.GetValue(html=0)
    self.input.SetValue('')
    txt = txt.strip()
    while txt.endswith('<br>'):
        txt = txt[:-4]

    txt = txt.strip()
    while txt.startswith('<br>'):
        txt = txt[4:]

    txt = txt.strip()
    if not txt or len(txt) <= 0:
        return 
    if sm.GetService('LSC').IsLanguageRestricted(self.channelID):
        try:
            if unicode(txt) != unicode(txt).encode('ascii', 'replace'):
                uicore.registry.BlockConfirm()
                eve.Message('LscLanguageRestrictionViolation')
                return 
        except:
            log.LogTraceback('Gurgle?')
            sys.exc_clear()
            eve.Message('uiwarning03')
            return 
    if boot.region == 'optic':
        try:
            bw = str(localization.GetByLabel('UI/Chat/ChannelWindow/OpticServerBannedWords')).decode('utf-7')
            banned = [ word for word in bw.split() if word ]
            for bword in banned:
                if txt.startswith('/') and not (txt.startswith('/emote') or txt.startswith('/me')):
                    txt = txt
                else:
                    txt = txt.replace(bword, '*')

        except Exception:
            log.LogTraceback('Borgle?')
            sys.exc_clear()
    if not sm.GetService('LSC').IsSpeaker(self.channelID):
        access = sm.GetService('LSC').GetMyAccessInfo(self.channelID)
        if access[1]:
            if access[1].reason:
                reason = access[1].reason
            else:
                reason = localization.GetByLabel('UI/Chat/NotSpecified')
            if access[1].admin:
                admin = access[1].admin
            else:
                admin = localization.GetByLabel('UI/Chat/NotSpecified')
            if access[1].untilWhen:
                borki = localization.GetByLabel('UI/Chat/CannotSpeakOnChannelUntil', reason=reason, untilWhen=access[1].untilWhen, admin=admin)
            else:
                borki = localization.GetByLabel('UI/Chat/CannotSpeakOnChannel', reason=reason, admin=admin)
        else:
            borki = localization.GetByLabel('UI/Chat/CannotSpeakOnChannel', reason=localization.GetByLabel('UI/Chat/NotSpecified'), admin=localization.GetByLabel('UI/Chat/NotSpecified'))
        self._Channel__LocalEcho(borki)
    if txt != '' and txt.replace('\r', '').replace('\n', '').replace('<br>', '').replace(' ', '').replace('/emote', '').replace('/me', '') != '':
        if txt.startswith('/me'):
            txt = '/emote' + txt[3:]
        spoke = 0
        if self.inputs[-1] != txt:
            self.inputs.append(txt)
            self.inputIndex = None
        nobreak = uiutil.StripTags(txt.replace('<br>', ''))
        if nobreak.startswith('/') and not (nobreak.startswith('/emote') or nobreak == '/'):
            for commandLine in uiutil.StripTags(txt.replace('<br>', '\n')).split('\n'):
                try:
                    slashRes = uicore.cmd.Execute(commandLine)
                    if slashRes is not None:
                        sm.GetService('logger').AddText('slash result: %s' % slashRes, 'slash')
                    elif nobreak.startswith('/tutorial') and eve.session and eve.session.role & service.ROLE_GML:
                        sm.GetService('tutorial').SlashCmd(commandLine)
                    elif eve.session and eve.session.role & ROLE_SLASH:
                        if commandLine.lower().startswith('/mark'):
                            sm.StartService('logger').LogError('SLASHMARKER: ', (eve.session.userid, eve.session.charid), ': ', commandLine)
                        slashRes = sm.RemoteSvc('slash').SlashCmd(commandLine)
                        if slashRes is not None:
                            sm.GetService('logger').AddText('slash result: %s' % slashRes, 'slash')
                    self._Channel__LocalEcho('/slash: ' + commandLine)
                except:
                    self._Channel__LocalEcho('/slash failed: ' + commandLine)
                    raise 

        else:
            stext = uiutil.StripTags(txt, ignoredTags=['b',
                'i',
                'u',
                'url',
                'br'])
            try:
                if type(self.channelID) != types.IntType and self.channelID[0][0] in ('constellationid', 'regionid') and util.IsWormholeSystem(eve.session.solarsystemid2):
                    self._Channel__Output(localization.GetByLabel('UI/Chat/NoChannelAccessWormhole'), 1, 1)
                    return 
                self.waitingForReturn = blue.os.GetWallclockTime()
                self._Channel__LocalEcho(stext)
                if not IsSpam(stext):
                    sm.GetService('LSC').SendMessage(self.channelID, stext)
                else:
                    self.waitingForReturn = 0
            except:
                self.waitingForReturn = 0
                raise 
