from xbmcplugin import addDirectoryItem, endOfDirectory, setContent
from xbmcgui import ListItem

class KODIMenu():

    def __init__(self, plugin):
        self.plugin=plugin
        self.h = plugin.handle

    def start_folder(self):
        setContent(self.h, "files")

    def new_info_item(self, info):
        li = ListItem(label=info)
        li.setProperty('IsPlayable', 'False')
        addDirectoryItem(self.h, "", listitem=li, isFolder=False)

    def new_video_item(self, displayName, title, playURL, thumbURL, duration):

        if displayName is not None:
            str=displayName + ": " + title
        else:
            str=title

        li = ListItem(label=str, path=playURL)

        li.setProperty('IsPlayable', 'True')
        li.addStreamInfo('video', {'duration': duration})
        li.setArt({'icon': thumbURL, 'poster': thumbURL, 'thumb': thumbURL, 'banner': thumbURL})


        #li.setInfo('video', { 'plot': 'Left hand desc' })

        addDirectoryItem(self.h, playURL, listitem=li, isFolder=False)

    def new_folder_item(self, item_name, item_val, func):

        li = ListItem(label=item_name)
        li.setProperty('IsPlayable', 'False')
        addDirectoryItem(self.h, self.plugin.url_for(func, item_val=item_val),
                         listitem=li, isFolder=True)

    def end_folder(self):
        endOfDirectory(self.h)
