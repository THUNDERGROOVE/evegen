#@liveupdate("globalClassMethod", "form.CharSelection::CharSelection", "OpenNews")
def OpenNews(self, browser, *args):
    import uicls
    uicls.Fill(parent=browser, color=(0.2, 0.2, 0.2, 0.4))
    browser.GoTo("http://evenews.alasiya.net")
