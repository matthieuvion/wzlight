class Client:
    """Client which manages communication with the Call of Duty API."""

    def __init__(self, http):
        self.http = http

    async def SearchPlayers(self, platform, username, **kwargs):
        """
        Search Call of Duty players by platform and username.

        Parameters
        ----------
        platform : callofduty.Platform
            Platform to get the players from.
        username : str
            Player's username for the designated platform.
        limit : int, optional
            Number of search results to return (default is None.)

        Returns
        -------
        list
            Array of Player objects matching the query.
        """

        data: dict = (await self.http.SearchPlayer(platform, username))["data"]

        limit: int = kwargs.get("limit", 0)
        if limit > 0:
            data = data[:limit]

        return data

    # // original client changed method : now GetProfile instead of GetPlayerProfile
    async def GetProfile(self, platform, username, title, mode):
        """
        Get a Call of Duty player's profile for Warzone

        Parameters
        ----------
        platform : callofduty.Platform
            Platform to get the player from.
        username : str
            Player's username for the designated platform.
        title : callofduty.Title
            Call of Duty title to get the player's profile from.
        mode: callofduty.Mode
            Call of Duty mode to get the player's profile from.

        Returns
        -------
        dict
            JSON data of the player's complete profile for the requested
            title and mode.
        """

        return (await self.http.GetProfile(platform, username, title, mode))["data"]

    # // original client : name changed from GetFullMatch to GetMatchStats
    async def GetMatchStats(self, platform, title, mode, matchId, language="en"):
        """
        Get Call of Duty Warzone match stats using given a specific matchId

        Parameters
        ----------
        platform : callofduty.Platform
            Platform to get the player from.
        title : callofduty.Title
            Call of Duty title which the match occured on.
        mode: callofduty.Mode
            Call of Duty mode to get the matches from.
        matchId : int
            Match ID.
        language : callofduty.Language, optional
            Language to use for localization data (default is English.)

        Returns
        -------
        object
            Match object representing the specified details.
        """

        return (
            await self.http.GetMatchStats(title, platform, mode, matchId, language)
        )["data"]["allPlayers"]

    # // Original client : GetPlayerMatches split in two : GetMatches (ids history) and GetMatchesDetailed (stats history)
    async def GetMatches(self, platform, username, title, mode, **kwargs):
        """Returns Warzone matches history, notably matches Ids --without stats"""

        limit: int = kwargs.get("limit", 20)
        startTimestamp: int = kwargs.get("startTimestamp", 0)
        endTimestamp: int = kwargs.get("endTimestamp", 0)

        data: dict = (
            await self.http.GetMatches(
                platform,
                username,
                title,
                mode,
                limit,
                startTimestamp,
                endTimestamp,
            )
        )["data"]

        return data

    async def GetMatchesDetailed(self, platform, username, title, mode, **kwargs):
        """Returns matches history, with username's stats for every match

        Modifications compared to callofduty.py > client.GetPlayerMatches :
        - removed if platform == 'Activision', no longer supported by API
        - filtered out summary data from API's matches res: ['data'] becomes ['data']['matches']
        - default number of matches returned is now 20 (max allowed by the API) instead of 10
        - added @backoff decorator to handle (some of) API rate/availability limits
        """
        limit: int = kwargs.get("limit", 20)
        startTimestamp: int = kwargs.get("startTimestamp", 0)
        endTimestamp: int = kwargs.get("endTimestamp", 0)

        return (
            await self.http.GetMatchesDetailed(
                platform,
                username,
                title,
                mode,
                limit,
                startTimestamp,
                endTimestamp,
            )
        )["data"]["matches"]


## Add convenience function here to loop over GetMatchStats and GetMatchesDetailed
