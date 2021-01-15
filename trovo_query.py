from requests import post
import json


"""
Data class - unsure if @dataclass is allowed in Kodi
"""


class LiveStream():

    def __init__(self, title, description, coverURL, playURL, displayName):
        self.title = title
        self.displayName=displayName
        self.description = description
        self.coverURL = coverURL
        self.playURL = playURL


"""
Data class - unsure if @dataclass is allowed in Kodi
"""


class ReplayStream():

    def __init__(self, title, playURL, coverURL, duration):
        self.title = title
        self.playURL = playURL
        self.coverURL = coverURL
        self.duration = duration

"""
Data class - unsure if @dataclass is allowed in Kodi
"""


class User():

    def __init__(self, userName, displayName, channelName, faceURL, isLive):
        self.userName = userName
        self.displayName = displayName
        self.channelName = channelName
        self.faceURL=faceURL
        self.isLive = isLive


"""
Query class for TROVO - funnel all 
"""


class Query():

    def __init__(self):
        self.endpoint = 'https://gql.trovo.live'
        self.token = None
        self.headername = None
        self.uid = ""
        self.validated_user = False

    
    def set_user(self, userName):
        self.userName=userName
        self.uid=self.get_user_uid(userName)
        self.validated_user=True
        return True

    def __execute(self, query, variables=None):
        return self.__send(query, variables)

    def __send(self, query, variables):
        data = {'query': query, 'variables': variables}
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        if self.token is not None:
            headers[self.headername] = '{}'.format(self.token)

        #        response = request("POST", url, data=payload)
        req = post(self.endpoint, data=json.dumps(
            data).encode('utf-8'), headers=headers)
        j = req.json()
        return j

 
    """
    returns the uid given the Trovo userName
    """

    def get_user_uid(self, userName):

        query='''query { getLiveInfo ( params: { userName: "'''+self.userName+'''" } ) { streamerInfo { uid } } } '''
        result = self.__execute(query)

        ret=result["data"]["getLiveInfo"]["streamerInfo"]["uid"]
        
        return ret


    def get_channel_id(self, userName):

        query='''query {
                getLiveInfo (
                        params: {
                            userName: "'''+userName+'''"
                        }
                    ) 
                    { 
                    channelInfo
                    {
                        id
                    },
                }
            }'''

        result = self.__execute(query)

        ret=result["data"]["getLiveInfo"]["channelInfo"]["id"]
        
        return ret

    """
    Returns a list of all the extant live streams on trovo - by making multiple calls if necessary
    """

    def get_live_info(self, userName):

        query='''
            query {
                getLiveInfo (
                        params: {
                            userName: "'''+userName+'''"
                        }
                    ) 
                    { 
                    programInfo {
                        title,
                        description
                        streamInfo {
                            bitrate,
                            playUrl
                        }
                    }
                }
            }
        '''
        result = self.__execute(query)

        pg=result["data"]["getLiveInfo"]["programInfo"]
        title=description=coverURL="NO DATA"

        print(result)
        if pg is not None:
            if "title" in pg:
                title=pg["title"]

            if "description" in pg:
                description=pg["description"]

            if "coverURL" in pg:
                coverURL=pg["coverURL"]

        streams = pg["streamInfo"]
        playURL=""
        for stream in streams:
            if stream["bitrate"]==0:
                # 0 bitrate means default?
                playURL=stream["playUrl"]

        l=LiveStream(displayName="",title=title,description=description, coverURL=coverURL, playURL=playURL)
        return l



    def get_all_live_streams(self):
        pass

    """
    Get the graphql information for user (A) and then parse it into a list of that (A) is following and are
    currently live
    """

    def get_following(self):
       
        query='''
            query {
                getMoreFollowedUsers (
                        params: {
                            uid: '''+str(self.uid)+'''
                            start: 0
                            count: 30
                        }
                    ) 
                    { 
                            list {
                                users {
                                    uid,
                                    name,
                                    faceUrl,
                                    channelName,
                                    channelCategory
                                    userName,
                                    liveState
                                }
                            }
                        }
                    }
            '''

        #EM_CHANNEL_STATE_LIVE 
      
        result = self.__execute(query)

        t_users=result["data"]["getMoreFollowedUsers"]["list"]["users"]

        users = []

        for user in t_users:

            isLive=user["liveState"]=='EM_CHANNEL_STATE_LIVE'
            displayName = user["name"]
            userName = user["userName"]
            channelName=user["channelName"]
            faceUrl=user["faceUrl"]
            u=User(userName=userName, displayName=displayName, channelName=channelName, faceURL=faceUrl, isLive=isLive)
            users.append(u)
    
        return (users)


    def get_following_live_streams(self):
        
        streams = []

        users=self.get_following()
        for user in users:
            if user.isLive:
                s=self.get_live_info(user.userName)
                s.displayName=user.displayName
                streams.append(s)

        return streams


    """
    """

    def get_replays(self, userName):

        uid = self.get_channel_id(userName)
        print("333333:" , uid )
        query=  '''
            query {
            getChannelLtvVideoInfos (
                    params: {
                        pageSize: 30,
                        currPage: 1,
                        channelID: '''+str(uid)+'''
                    }
                ) 
                { 
                    vodInfos {
                        title,
                        duration,
                        coverUrl,
                        playInfos {
                            bitrate,
                            playUrl,
                            desc
                        }
                }
        
            }
        }
        '''

        result = self.__execute(query)
        replays = []

        for u in result["data"]["getChannelLtvVideoInfos"]["vodInfos"]:
            title=u["title"]
            duration=u["duration"]
            coverURL=u["coverUrl"]
            bitrate=-1
            playURL=""

            for vod in u["playInfos"]:

                if vod["bitrate"]>bitrate:
                    playURL = vod["playUrl"]
                    bitrate=vod["bitrate"]

            r= ReplayStream(title=title,playURL=playURL,coverURL=coverURL, duration=duration)
            replays.append(r)

        return replays
