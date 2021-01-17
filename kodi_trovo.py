import routing
from xbmcgui import Dialog, INPUT_ALPHANUM
import xbmcaddon
import trovo_query
import KODIMenu as kodi_menu


plugin = routing.Plugin()


def valid_user():
    global query
    if not query.validated_user:
        # Warn the user that it's not a valid user
        dialog = Dialog()
        dialog.ok("Warning", "The add-on has not found your user name on TROVO.LIVE")
        return False

    return True


@plugin.route('/')
def index():
    build_main_menu()


@plugin.route('/followed_live')
def followed_live():

    if not valid_user():
        return

    build_followed_live()


@plugin.route('/followed_replay')
def followed_replay():

    if not valid_user():
        return

    build_followed_replay()


@plugin.route('/followed_replay_user/<item_val>')
def followed_replay_user(item_val):

    if not valid_user():
        return

    build_followed_replay_user(item_val)


@plugin.route('/livestreams_search')
def livestreams_search():

    if not valid_user():
        return

    """ There is no test for valid_user needed here. getting all the livestreams (to search through) doesn't require a user id
    Even if there is a problem in future, this bit of the add-on should still run """
    build_livestreams_search()


@plugin.route('/all_livestreams')
def livestreams_all():

    if not valid_user():
        return

    """ There is no test for valid_user needed here. getting all the livestreams doesn't require a user id
    Even if there is a problem in future, this bit of the add-on should still run """

    build_all_livestreams()


@plugin.route('/open_settings')
def open_settings():
    build_open_settings()


def build_main_menu():
   
    global menu
    menu.start_folder()

    menu.new_folder_item(item_name="Set your TROVO user", item_val=None, func=open_settings)
    menu.new_folder_item(
        item_name="Currently live streamers you follow", item_val=None, func=followed_live)
    menu.new_folder_item(
        item_name="Replays of streamers you follow", item_val=None, func=followed_replay)
    #menu.new_folder_item(
    #    item_name="View all currently live streams", item_val=None, func=livestreams_all)
    #menu.new_folder_item(item_name="Search currently live streams",
    #                     item_val=None, func=livestreams_search)
    menu.end_folder()


def build_followed_live():

    global query, menu
    menu.start_folder()

    live_streams = query.get_following_live_streams()

    if 0 == len(live_streams):
        menu.new_info_item("** NONE OF THE STREAMERS YOU FOLLOW ARE LIVE **")
    else:
        for stream in live_streams:
            menu.new_video_item(displayName=stream.displayName, title=stream.title,
                                playURL=stream.playURL, thumbURL=stream.coverURL, duration=0)

    menu.end_folder()


def build_followed_replay():

    global query, menu
    menu.start_folder()

    following = query.get_following()

    if 0 == len(following):
        menu.new_info_item("** YOU ARE NOT FOLLOWING ANYONE **")
    else:
        for user in following:
            menu.new_folder_item(item_name=user.displayName,
                                 item_val=user.userName, func=followed_replay_user)

    menu.end_folder()


def build_followed_replay_user(item_val):

    global query, menu
    menu.start_folder()

    replays = query.get_replays(item_val)

    if 0 == len(replays):
        menu.new_info_item("** NO REPLAYS FOUND **")
    else:
        for stream in replays:
            menu.new_video_item(displayName=item_val, title=stream.title,
                                playURL=stream.playURL, thumbURL=stream.coverURL, duration=stream.duration)

    menu.end_folder()


def build_all_livestreams():

    global query, menu
    menu.start_folder()

    streams = query.get_all_live_streams()

    if 0 == len(streams):
        menu.new_info_item("** NO LIVE STREAMS FOUND **")
    else:
        for stream in streams:

            menu.new_video_item(displayName=stream.displayName, title=stream.title,
                                playURL=stream.playURL, thumbURL=stream.thumbURL, duration=None)

    menu.end_folder()


def build_livestreams_search():

    search_for = Dialog().input("Enter search", "", INPUT_ALPHANUM, 0, 0).upper()

    global query, menu
    menu.start_folder()

    streams = query.get_all_live_streams()

    if 0 == len(streams):
        menu.new_info_item("** NO LIVE STREAMS FOUND **")
    else:

        for stream in streams:

            if search_for in stream.title.upper():

                menu.new_video_item(displayName=stream.displayName, title=stream.title,
                                    playURL=stream.playURL, thumbURL=stream.thumbURL, duration=None)

    menu.end_folder()


def build_open_settings():
    xbmcaddon.Addon().openSettings()
    get_trovo_userid()


def get_trovo_userid():
    global query, menu
    # What is the Display Name set as in the add-on settings
    userName = xbmcaddon.Addon().getSetting("user")

    query.set_user(userName)

    # set the query object if it has a valid blockchain user-id
    if not query.validated_user:

        # Warn the user that it's not a valid user and resort to Trovo so the add-on at least runs
        dialog = Dialog()
        dialog.ok("Unable to find your TROVO.LIVE user",
                  "User name could not be found. Using the default: Trovo")

        query.set_user("Trovo")        
        xbmcaddon.Addon().setSetting(id="user", value="Trovo")  # Write that to the settings

    return userName


query = trovo_query.Query()
menu = kodi_menu.KODIMenu(plugin)
get_trovo_userid()
