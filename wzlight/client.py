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

    # // original client : changed method : now GetProfile instead of GetPlayerProfile
    # title and mode args now have default Warzone values
    async def GetProfile(self, platform, username, **kwargs):

        """
        Get a Call of Duty player's profile for Warzone

        Parameters
        ----------
        platform : str, either "battle", "uno" (activision), "psn", "steam", "xbl"
            Platform to get the player from.
        username : str
            Player's username for the designated platform.
        title : str, optional
            Call of Duty title to get the player's profile from
            (default for Warzone is "mw" aka modernwarfare)
        mode: str, optional
            Call of Duty mode to get the player's profile from.
            (default for Warzone is "wz")

        Returns
        -------
        dict
            JSON data of the player's complete profile for the requested
            title and mode.
        """
        title: str = kwargs.get("title", "mw")
        mode: str = kwargs.get("mode", "wz")

        return (await self.http.GetProfile(platform, username, title, mode))["data"]

    # // original client : name changed from GetFullMatch to GetMatchStats
    # title, mode, language args now have default Warzone values
    async def GetMatchStats(self, platform, matchId, **kwargs):
        """
        Get Call of Duty Warzone match stats using given a specific matchId

        Parameters
        ----------
        platform : str, either "battle", "uno" (activision), "psn", "steam", "xbl"
            Platform to get the player from.
        matchId : int
            Match ID.
        title : str, optional
            Call of Duty title to get the player's profile from
            (default for Warzone is "mw" aka modernwarfare)
        mode: str, optional
            Call of Duty mode to get the player's profile from.
            (default for Warzone is "wz")
        language : callofduty.Language, optional
            Language to use for localization data (default is English.)

        Returns
        -------
        dict
            Match detailed stats
        """
        title: str = kwargs.get("title", "mw")
        mode: str = kwargs.get("mode", "wz")
        language: str = kwargs.get("language", "en")

        return (
            await self.http.GetMatchStats(title, platform, mode, matchId, language)
        )["data"]["allPlayers"]

    # // Original client : GetPlayerMatches split in two :
    #    GetMatches (ids history) and GetMatchesDetailed (stats history)
    #    Removed "uno" endpoint that have been disabled by Activision
    #    Title, mode args now have default Warzone values
    async def GetMatches(self, platform, username, **kwargs):
        """
        Returns Warzone matches history, notably matches Ids --without stats

        Parameters
        ----------
        platform : str, either "battle", "uno" (activision), "psn", "steam", "xbl"
            Platform to get the player from.
        username : str
            Player's username for the designated platform.
        title : str, optional
            Call of Duty title to get the player's profile from
            (default for Warzone is "mw" aka modernwarfare)
        mode: str, optional
            Call of Duty mode to get the player's profile from.
            (default for Warzone is "wz")
        limit: optional
        startTimestamp: optional
        endTimestamp: optional

        Returns
        -------
        dict
            Warzone matches history --ids, not stats
        """
        title: str = kwargs.get("title", "mw")
        mode: str = kwargs.get("mode", "wz")

        limit: int = kwargs.get("limit", 20)  # API default is 10, max is 20
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

    async def GetMatchesDetailed(self, platform, username, **kwargs):
        """
        Returns matches history, with username's stats for every match

        Parameters
        ----------
        platform : str, either "battle", "uno" (activision), "psn", "steam", "xbl"
            Platform to get the player from.
        username : str
            Player's username for the designated platform.
        title : str, optional
            Call of Duty title to get the player's profile from
            (default for Warzone is "mw" aka modernwarfare)
        mode: str, optional
            Call of Duty mode to get the player's profile from.
            (default for Warzone is "wz")
        limit: optional
        startTimestamp: optional
        endTimestamp: optional

        Returns
        -------
        dict
            Warzone matches history with detailed stats
        """

        title: str = kwargs.get("title", "mw")
        mode: str = kwargs.get("mode", "wz")

        limit: int = kwargs.get("limit", 20)  # API default is 10, max is 20
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

    ##  Convenience functions to loop over GetMatchStats and GetMatchesDetailed

    async def LoopMatchesDetailed(self, platform, username, **kwargs):
        title: str = kwargs.get("title", "mw")
        mode: str = kwargs.get("mode", "wz")

        limit: int = kwargs.get("limit", 20)  # API default is 10, max is 20
        startTimestamp: int = kwargs.get("startTimestamp", 0)
        endTimestamp: int = kwargs.get("endTimestamp", 0)

        # add loop here
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

    async def LoopMatchStats(self, platform, matchId, **kwargs):
        title: str = kwargs.get("title", "mw")
        mode: str = kwargs.get("mode", "wz")
        language: str = kwargs.get("language", "en")

        # add loop here
        return (
            await self.http.GetMatchStats(title, platform, mode, matchId, language)
        )["data"]["allPlayers"]
