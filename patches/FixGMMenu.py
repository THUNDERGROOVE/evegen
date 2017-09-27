#@liveupdate("globalClassMethod", "svc.menu::MenuSvc", "GetGMMenu")
def GetGMMenu(self, itemID = None, slimItem = None, charID = None, invItem = None, mapItem = None):

    def startConsole():
        import form
        import triui
        import code
        import uthread
        m = form.MessageBox.Open()
        m.Execute("a", "Notice", triui.OK, triui.INFO, "don't look at me")
        m.SetText("You must start exefile.exe with /console for this to do anything")
        uthread.new(code.interact, ())

    if not session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
        if charID and session.role & service.ROLE_LEGIONEER:
            return [('Gag ISK Spammer', self.GagIskSpammer, (charID,))]
        return []
    gm = [(str(itemID or charID), blue.pyos.SetClipboardData, (str(itemID or charID),))]
    gm.append(("Open Dev Window", form.DevWindow.Open, ()))
    gm.append(("Open Console (don't do it)", startConsole, ()))
    if mapItem and not slimItem:
       #gm.append(('TR me here!', sm.RemoteSvc('slash').SlashCmd, ('/tr me ' + str(mapItem.itemID),)))
        eve.Message("CustomNotify", {"notify": "Teleporting to: " + str(mapItem.itemID)})
        gm.append(("TR me here!", sm.GetService("LSC").LocalEchoAll, (".tr " + str(mapItem.itemID),), eve.session.charid))
        gm.append(None)
    elif charID:
        gm.append(('TR me to %s' % cfg.eveowners.Get(charID).name, sm.RemoteSvc('slash').SlashCmd, ('/tr me ' + str(charID),)))
        gm.append(None)
    elif slimItem:
        gm.append(('TR me here!', sm.RemoteSvc('slash').SlashCmd, ('/tr me ' + str(itemID),)))
        gm.append(None)
    if invItem:
        typeID = invItem.typeID
        gm += [('Copy ID/Qty', self.CopyItemIDAndMaybeQuantityToClipboard, (invItem,))]
        typeText = 'copy typeID (%s)' % invItem.typeID
        gm += [(typeText, blue.pyos.SetClipboardData, (str(invItem.typeID),))]
        if invItem.flagID == const.flagHangar and invItem.locationID == session.stationid and invItem.itemID not in (session.shipid, session.charid):
            gm.append(('Take out trash', self.TakeOutTrash, [[invItem]]))
        #gm.append(('Edit', self.GetAdamEditType, [invItem.typeID]))
        #gm.append(None)
        if typeID < 140000000:
            typeID = invItem.typeID
            gm.append(('typeID: ' + str(typeID) + ' (%s)' % cfg.invtypes.Get(typeID).name, blue.pyos.SetClipboardData, (str(typeID),)))
            invType = cfg.invtypes.Get(typeID)
            group = invType.groupID
            gm.append(('groupID: ' + str(group) + ' (%s)' % invType.Group().name, blue.pyos.SetClipboardData, (str(group),)))
            category = invType.categoryID
            categoryName = cfg.invcategories.Get(category).name
            gm.append(('categID: ' + str(category) + ' (%s)' % categoryName, blue.pyos.SetClipboardData, (str(category),)))
            graphic = invType.Graphic()
            if graphic:
                gm.append(('graphicID: ' + str(graphic.id), blue.pyos.SetClipboardData, (str(graphic.id),)))
                gm.append(('graphicFile: ' + str(graphic.graphicFile), blue.pyos.SetClipboardData, (str(graphic.graphicFile),)))
    if charID and not util.IsNPC(charID):
        action = 'gm/character.py?action=Character&characterID=' + str(charID)
        #gm.append(('Show in ESP', self.GetFromESP, (action,)))
        gm.append(None)
        gm.append(('Gag ISK Spammer', self.GagIskSpammer, (charID,)))
        gm.append(('Ban ISK Spammer', self.BanIskSpammer, (charID,)))
        #action = 'gm/users.py?action=BanUserByCharacterID&characterID=' + str(charID)
        #gm.append(('Ban User (ESP)', self.GetFromESP, (action,)))
        gm += [('Gag User', [('30 minutes', self.GagPopup, (charID, 30)),
            ('1 hour', self.GagPopup, (charID, 60)),
            ('6 hours', self.GagPopup, (charID, 360)),
            ('24 hours', self.GagPopup, (charID, 1440)),
            None,
            ('Ungag', lambda *x: self.SlashCmd('/ungag %s' % charID))])]
    gm.append(None)
    item = slimItem or invItem
    if item:
        if item.categoryID == const.categoryShip and (item.singleton or not session.stationid):
            #import dna
            #if item.ownerID in [session.corpid, session.charid] or session.role & service.ROLE_WORLDMOD:
            #    try:
            #        menu = dna.Ship().ImportFromShip(shipID=item.itemID, ownerID=item.ownerID, deferred=True).GetMenuInline(spiffy=False, fit=item.itemID != session.shipid)
            #        gm.append(('Copycat', menu))
            #    except RuntimeError:
            #        pass
            gm += [('/Online modules', lambda shipID = item.itemID: self.SlashCmd('/online %d' % shipID))]
        gm += self.GetGMTypeMenu(item.typeID, itemID=item.itemID)
        if getattr(slimItem, 'categoryID', None) == const.categoryEntity or getattr(slimItem, 'groupID', None) == const.groupWreck:
            gm.append(('NPC Info', ('isDynamic', self.NPCInfoMenu, (item,))))
        gm.append(None)
    if session.role & service.ROLE_CONTENT:
        if slimItem:
            if getattr(slimItem, 'dunObjectID', None) != None:
                if not sm.StartService('scenario').IsSelected(itemID):
                    gm.append(('Add to Selection', sm.StartService('scenario').AddSelected, (itemID,)))
                else:
                    gm.append(('Remove from Selection', sm.StartService('scenario').RemoveSelected, (itemID,)))
    if slimItem:
        itemID = slimItem.itemID
        graphicID = cfg.invtypes.Get(slimItem.typeID).graphicID
        graphicFile = util.GraphicFile(graphicID)
        if graphicFile is '':
            graphicFile = None
        subMenu = self.GetGMStructureStateMenu(itemID, slimItem, charID, invItem, mapItem)
        if len(subMenu) > 0:
            gm += [('Change State', subMenu)]
        gm += self.GetGMBallsAndBoxesMenu(itemID, slimItem, charID, invItem, mapItem)
        gm.append(None)
        gm.append(('charID: ' + self.GetOwnerLabel(slimItem.charID), blue.pyos.SetClipboardData, (str(slimItem.charID),)))
        gm.append(('ownerID: ' + self.GetOwnerLabel(slimItem.ownerID), blue.pyos.SetClipboardData, (str(slimItem.ownerID),)))
        gm.append(('corpID: ' + self.GetOwnerLabel(slimItem.corpID), blue.pyos.SetClipboardData, (str(slimItem.corpID),)))
        gm.append(('allianceID: ' + self.GetOwnerLabel(slimItem.allianceID), blue.pyos.SetClipboardData, (str(slimItem.allianceID),)))
        gm.append(None)
        gm.append(('typeID: ' + str(slimItem.typeID) + ' (%s)' % cfg.invtypes.Get(slimItem.typeID).name, blue.pyos.SetClipboardData, (str(slimItem.typeID),)))
        gm.append(('groupID: ' + str(slimItem.groupID) + ' (%s)' % cfg.invgroups.Get(slimItem.groupID).name, blue.pyos.SetClipboardData, (str(slimItem.groupID),)))
        gm.append(('categID: ' + str(slimItem.categoryID) + ' (%s)' % cfg.invcategories.Get(slimItem.categoryID).name, blue.pyos.SetClipboardData, (str(slimItem.categoryID),)))
        gm.append(('graphicID: ' + str(graphicID), blue.pyos.SetClipboardData, (str(graphicID),)))
        gm.append(('graphicFile: ' + str(graphicFile), blue.pyos.SetClipboardData, (str(graphicFile),)))
        gm.append(None)
        gm.append(('Copy Coordinates', self.CopyCoordinates, (itemID,)))
        gm.append(None)
        try:
            state = slimItem.orbitalState
            if state in (entities.STATE_UNANCHORING,
                entities.STATE_ONLINING,
                entities.STATE_ANCHORING,
                entities.STATE_OPERATING,
                entities.STATE_OFFLINING,
                entities.STATE_SHIELD_REINFORCE):
                stateText = pos.DISPLAY_NAMES[pos.Entity2DB(state)]
                gm.append(('End orbital state change (%s)' % stateText, self.CompleteOrbitalStateChange, (itemID,)))
            elif state == entities.STATE_ANCHORED:
                upgradeType = sm.GetService('godma').GetTypeAttribute2(slimItem.typeID, const.attributeConstructionType)
                if upgradeType is not None:
                    gm.append(('Upgrade to %s' % cfg.invtypes.Get(upgradeType).typeName, self.GMUpgradeOrbital, (itemID,)))
            gm.append(('GM: Take Control', self.TakeOrbitalOwnership, (itemID, slimItem.planetID)))
        except ValueError:
            pass
    gm.append(None)
    dict = {'CHARID': charID,
        'ITEMID': itemID,
        'ID': charID or itemID}
    for i in range(20):
        item = prefs.GetValue('gmmenuslash%d' % i, None)
        if item:
            for (k, v,) in dict.iteritems():
                if ' %s ' % k in item and v:
                    item = item.replace(k, str(v))
                    break
            else:
                continue
            gm.append((item, sm.RemoteSvc('slash').SlashCmd, (item,)))
    return gm
