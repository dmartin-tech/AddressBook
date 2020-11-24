import json
import os
import wx
import uuid
import random


class ContactBook():
    def __init__(self, bookName):
        super().__init__()
        self.book = bookName
        if not os.path.exists(self.getBookFile()):
            with open(self.getBookFile(), "+x") as conBook:
                json.dump({"entries": {}}, conBook)

    def addEntry(self, details):
        entrylist = self.getEntries()
        entrylist["entries"][str(uuid.uuid4().hex)] = details
        with open(self.getBookFile(), "+w") as conBook:
            json.dump(entrylist, conBook, sort_keys=True, indent=2)

    def removeEntry(self, entryUUID):
        entrylist = self.getEntries()
        del entrylist["entries"][f"{entryUUID}"]
        with open(self.getBookFile(), "+w") as conBook:
            json.dump(entrylist, conBook, sort_keys=True, indent=2)

    def modifyEntry(self, entryUUID, details):
        entrylist = self.getEntries()
        entrylist["entries"][f"{entryUUID}"] = details
        with open(self.getBookFile(), "+w") as conBook:
            json.dump(entrylist, conBook, sort_keys=True, indent=2)

    def getEntry(self, entryUUID):
        return self.getEntries()["entries"][f"{entryUUID}"]

    def getEntries(self):
        with open(self.getBookFile(), "r") as conBook:
            return json.load(conBook)

    def getBookFile(self):
        return self.book+".json"


class ContactBookApp(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 600))
        self.contactBook = ContactBook("main")
        self.selectedContact = None
        self.SetMinSize((800, 600))
        self.CreateStatusBar()
        self.mainPanel = wx.Panel(self)

        filemenu = wx.Menu()
        aboutItem = filemenu.Append(
            wx.ID_ABOUT, "&About", "About this software")
        filemenu.AppendSeparator()
        exitItem = filemenu.Append(wx.ID_EXIT, "E&xit", "Quit")

        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")

        self.Bind(wx.EVT_MENU, self.onAbout, aboutItem)
        self.Bind(wx.EVT_MENU, self.onExit, exitItem)
        self.createWidgets()
        self.populateEntries()
        self.SetMenuBar(menubar)
        self.Show()

    def createWidgets(self):
        self.entriesBox = wx.ListBox(
            self.mainPanel, choices=[], style=wx.LB_EXTENDED)
        self.entriesBox.SetLabelText("Entries")

        self.nameText = wx.StaticText(self.mainPanel, label="")
        self.emailText = wx.StaticText(self.mainPanel, label="")
        self.phoneText = wx.StaticText(self.mainPanel, label="")
        self.addressText = wx.StaticText(self.mainPanel, label="")

        leftSizer = wx.BoxSizer(wx.VERTICAL)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

        rightSizer = wx.BoxSizer(wx.HORIZONTAL)
        infoSizer = wx.GridBagSizer(vgap=5, hgap=5)
        nameSizer = wx.BoxSizer(wx.HORIZONTAL)
        emailSizer = wx.BoxSizer(wx.HORIZONTAL)
        phoneSizer = wx.BoxSizer(wx.HORIZONTAL)
        addressSizer = wx.BoxSizer(wx.HORIZONTAL)

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        addButton = wx.Button(self.mainPanel, label="Add Entry")
        modifyButton = wx.Button(self.mainPanel, label="Modify Entry")
        removeButton = wx.Button(self.mainPanel, label="Remove Entry")

        buttonSizer.AddMany([(addButton, 1, wx.ALL | wx.EXPAND),
                             (modifyButton, 1, wx.ALL | wx.EXPAND),
                             (removeButton, 1, wx.ALL | wx.EXPAND)])

        leftSizer.Add(self.entriesBox, 10, wx.ALL | wx.EXPAND)
        leftSizer.Add(buttonSizer, 1, wx.ALL | wx.EXPAND)
        infoSizer.Add(sizer=nameSizer, pos=wx.GBPosition(
            0, 0), flag=wx.ALIGN_RIGHT)
        infoSizer.Add(sizer=emailSizer, pos=wx.GBPosition(
            1, 0), flag=wx.ALIGN_RIGHT)
        infoSizer.Add(sizer=phoneSizer, pos=wx.GBPosition(
            2, 0), flag=wx.ALIGN_RIGHT)
        infoSizer.Add(sizer=addressSizer, pos=wx.GBPosition(
            3, 0), flag=wx.ALIGN_RIGHT)

        rightSizer.Add(infoSizer, 1, wx.ALL | wx.EXPAND, 4)

        nameSizer.Add(wx.StaticText(self.mainPanel, label="Name: "))
        nameSizer.Add(self.nameText)

        emailSizer.Add(wx.StaticText(self.mainPanel, label="Email: "))
        emailSizer.Add(self.emailText)

        phoneSizer.Add(wx.StaticText(self.mainPanel, label="Phone: "))
        phoneSizer.Add(self.phoneText)

        addressSizer.Add(wx.StaticText(self.mainPanel, label="Address: "))
        addressSizer.Add(self.addressText)

        mainSizer.Fit(self)
        mainSizer.Add(leftSizer, 1, wx.ALIGN_LEFT | wx.EXPAND, 4)
        mainSizer.Add(rightSizer, 2, wx.EXPAND, 4)
        self.mainPanel.SetSizer(mainSizer)
        self.Bind(wx.EVT_BUTTON, self.onAddEntry, addButton)
        self.Bind(wx.EVT_BUTTON, self.onModifyEntry, modifyButton)
        self.Bind(wx.EVT_BUTTON, self.onRemoveEntry, removeButton)
        self.Bind(wx.EVT_LISTBOX, self.onSelectEntry, self.entriesBox)

    def populateEntries(self):
        self.entriesBox.Clear()
        self.clearInfo()
        for v in self.contactBook.getEntries()["entries"]:
            self.entriesBox.Append(self.contactBook.getEntries()[
                                   "entries"][v]["name"], clientData=v)

    def clearInfo(self):
        self.nameText.SetLabelText("")
        self.emailText.SetLabelText("")
        self.phoneText.SetLabelText("")
        self.addressText.SetLabelText("")

    def updateInfo(self, entryUUID):
        entry = self.contactBook.getEntry(entryUUID)
        self.nameText.SetLabelText(entry["name"])
        self.emailText.SetLabelText(entry["email"])
        self.phoneText.SetLabelText(entry["phone"])
        self.addressText.SetLabelText(entry["address"])
        pass

    def onSelectEntry(self, event):
        try:
            self.selectedContact = self.entriesBox.GetClientData(
                event.GetSelection())
            self.updateInfo(self.selectedContact)
        except:
            self.clearInfo()
        pass

    def onAddEntry(self, event):
        entryDialog = AddEntryDialog(self)
        entryDialog.ShowModal()
        if entryDialog.isConfirmed():
            self.contactBook.addEntry(entryDialog.getDetails())
            self.populateEntries()
        pass

    def onModifyEntry(self, event):
        try:
            selectedContact = self.entriesBox.GetSelections()
            if len(selectedContact) > 1:
                raise Exception("Select at most one contact to modify.")
            elif len(selectedContact) == 0:
                raise Exception("Select a single contact to modify.")
            entryDialog = ModifyEntryDialog(self)
            entryUUID = self.entriesBox.GetClientData(selectedContact[0])
            print(entryUUID)
            entry = self.contactBook.getEntry(entryUUID)
            entryDialog.setDetails(entry)
            entryDialog.ShowModal()
            if entryDialog.isConfirmed():
                self.contactBook.modifyEntry(
                    entryUUID, entryDialog.getDetails())
                self.populateEntries()
        except Exception as e:
            wx.MessageBox(e.args[0],
                          style=wx.ICON_ERROR)
            pass
        pass

    def onRemoveEntry(self, event):
        dialog = wx.MessageDialog(self, "Are you sure you wish to remove these contacts?",
                                  style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
        if dialog.ShowModal() == wx.ID_YES:
            statusbar = self.GetStatusBar()
            try:
                selectedContacts = self.entriesBox.GetSelections()
                statusbar.PushStatusText("Deleting Contacts...")
                for contact in selectedContacts:
                    self.contactBook.removeEntry(
                        self.entriesBox.GetClientData(contact))
                self.populateEntries()
            except:
                wx.MessageBox("Select a contact to remove.",
                              style=wx.ICON_ERROR)
                pass
            statusbar.PopStatusText()
        pass

    def onAbout(self, event):
        wx.MessageBox(
            "A contact book made using wxPython in Python 3.", "About", parent=self)
        pass

    def onExit(self, event):
        self.Close()


class EntryDialog(wx.Dialog):

    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, title=title, size=(200, 250))
        self.CenterOnParent()

        self.confirm = False
        self.mainPanel = wx.Panel(self)
        self.flexSizer = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        self.mainPanel.SetSizer(self.flexSizer)

        self.nameLabel = wx.StaticText(self.mainPanel, label="Name: ")
        self.nameInput = wx.TextCtrl(self.mainPanel)

        self.emailLabel = wx.StaticText(self.mainPanel, label="Email: ")
        self.emailInput = wx.TextCtrl(self.mainPanel)

        self.phoneLabel = wx.StaticText(self.mainPanel, label="Phone: ")
        self.phoneInput = wx.TextCtrl(self.mainPanel)

        self.addressLabel = wx.StaticText(self.mainPanel, label="Address: ")
        self.addressInput = wx.TextCtrl(self.mainPanel)

        self.confirmButton = wx.Button(self.mainPanel, label="Confirm")
        self.Bind(wx.EVT_BUTTON, self.onConfirm, self.confirmButton)

        flags = wx.ALIGN_RIGHT | wx.ALL | wx.ALIGN_CENTER_VERTICAL
        self.flexSizer.Add(self.nameLabel, flag=flags, border=4)
        self.flexSizer.Add(self.nameInput, flag=flags, border=4)

        self.flexSizer.Add(self.emailLabel, flag=flags, border=4)
        self.flexSizer.Add(self.emailInput, flag=flags, border=4)

        self.flexSizer.Add(self.phoneLabel, flag=flags, border=4)
        self.flexSizer.Add(self.phoneInput, flag=flags, border=4)

        self.flexSizer.Add(self.addressLabel, flag=flags, border=4)
        self.flexSizer.Add(self.addressInput, flag=flags, border=4)

        self.flexSizer.AddSpacer(1)
        self.flexSizer.Add(self.confirmButton, flag=flags, border=4)

    def getDetails(self):
        return {"name": self.nameInput.GetValue(),
                "email": self.emailInput.GetValue(),
                "phone": self.phoneInput.GetValue(),
                "address": self.addressInput.GetValue()}

    def setDetails(self, details):
        self.nameInput.SetValue(details["name"])
        self.emailInput.SetValue(details["email"])
        self.phoneInput.SetValue(details["phone"])
        self.addressInput.SetValue(details["address"])

    def onConfirm(self, evt):
        self.confirm = True
        self.Close()

    def isConfirmed(self):
        return self.confirm


class AddEntryDialog(EntryDialog):

    def __init__(self, parent):
        super().__init__(parent, "Add Entry")
        self.confirmButton.SetLabel("Add Contact")


class ModifyEntryDialog(EntryDialog):

    def __init__(self, parent):
        super().__init__(parent, "Modify Entry")
        self.confirmButton.SetLabel("Modify Contact")


if __name__ == "__main__":
    app = wx.App(False)
    frame = ContactBookApp(None, "Contact Book")
    app.MainLoop()
    pass
