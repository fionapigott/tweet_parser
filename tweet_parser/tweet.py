import datetime

from tweet_parser.lazy_property import lazy_property
from tweet_parser.tweet_parser_errors import NotATweetError
from tweet_parser import tweet_checking
from tweet_parser.getter_methods import tweet_date, tweet_user
from tweet_parser.getter_methods import tweet_text, tweet_geo, tweet_links
from tweet_parser.getter_methods import tweet_entities, tweet_embeds


class Tweet(dict):
    """
    tweet class
    """
    def __init__(self, tweet_dict, do_format_validation=False):
        """
        Initialize a Tweet object from a dict representing a Tweet payload

        Args:
            tweet_dict (dict): A dictionary representing a Tweet payload
            do_format_checking (bool): If "True", compare the keys in this
                dict to a supeset of expected keys and to a minimum set of
                expected keys (as defined in tweet_parser.tweet_keys).
                Will cause the parser to fail if unexpected keys are present
                or if expected keys are missing.
                Intended to allow run-time format testing, allowing the user
                to surface unexpected format changes.

        Returns:
            Tweet: Class "Tweet", inherits from dict, provides properties to
                   get various data values from the Tweet.

        Example:
        >>> # python dict representing a Tweet
        >>> tweet_dict = {"id": 867474613139156993,
                          "id_str": "867474613139156993",
                          "created_at": "Wed May 24 20:17:19 +0000 2017",
                          "text": "Some Tweet text",
                          "user": {
                              "screen_name": "RobotPrincessFi",
                              "id_str": "815279070241955840"
                              }
                         }
        >>> # create a Tweet object
        >>> tweet = Tweet(tweet_dict)
        >>> # use the Tweet obj to access data elements
        >>> tweet.id
        "867474613139156993"
        >>> tweet.created_at_seconds
        1495657039
        """

        # get the format of the Tweet data
        # also, this throws an error if it's not a tweet
        self.original_format = tweet_checking.check_tweet(tweet_dict,
                                                          do_format_validation)

        # make sure that this obj has all of the keys that our dict had
        self.update(tweet_dict)

    @lazy_property
    def id(self):
        """
        Tweet snowflake id as a string

        Returns:
            str: Twitter snowflake id, numeric only (no other text)

        Example:
        >>> original_format_dict = {
                "created_at": "Wed May 24 20:17:19 +0000 2017",
                "id": 867474613139156993,
                "id_str": "867474613139156993",
                "user": {"user_keys":"user_data"},
                "text": "some tweet text"
                }
        >>> Tweet(original_format_dict).id
        "867474613139156993"

        >>> activity_streams_dict = {
                "postedTime": "2017-05-24T20:17:19.000Z",
                "id": "tag:search.twitter.com,2005:867474613139156993",
                "actor": {"user_keys":"user_data"},
                "body": "some tweet text"
                }
        >>> Tweet(activity_streams_dict).id
        "867474613139156993"

        """
        if self.original_format:
            return self["id_str"]
        else:
            return self["id"].split(":")[-1]

    @lazy_property
    def created_at_seconds(self):
        """
        Time that a Tweet was posted in seconds since the Unix epoch

        Returns:
            int: seconds since the unix epoch
                 (determined by converting Tweet.id
                 into a timestamp using tweet_date.snowflake2utc)
        """
        return tweet_date.snowflake2utc(self.id)

    @lazy_property
    def created_at_datetime(self):
        """
        Time that a Tweet was posted as a Python datetime object

        Returns:
            datetime.datetime: the value of tweet.created_at_seconds
                               converted into a datetime object
        """
        return datetime.datetime.utcfromtimestamp(self.created_at_seconds)

    @lazy_property
    def created_at_string(self):
        """
        Time that a Tweet was posted as a string with the format:
        'YYYY-MM-ddTHH:MM:SS.000Z'

        Returns:
            str: the value of tweet.created_at_seconds
                 converted into a string ('YYYY-MM-ddTHH:MM:SS.000Z')
        """
        return self.created_at_datetime.strftime("%Y-%M-%dT%H:%M:%S.000Z")

    @lazy_property
    def user_id(self):
        """
        The Twitter ID of the user who posted the Tweet

        Returns:
            str: value returned by calling tweet_user.get_user_id on 'self'
        """
        return tweet_user.get_user_id(self)

    @lazy_property
    def screen_name(self):
        """
        The screen name (@ handle) of the user who posted the Tweet

        Returns:
            str: value returned by calling tweet_user.get_screen_name on 'self'
        """
        return tweet_user.get_screen_name(self)

    @lazy_property
    def name(self):
        """
        The display name of the user who posted the Tweet

        Returns:
            str: value returned by calling tweet_user.get_name on 'self'
        """
        return tweet_user.get_name(self)

    @lazy_property
    def klout_score(self):
        """
        The Klout score (int) (if it exists) of the user who posted the Tweet

        Returns:
            int: value returned by calling tweet_user.get_klout_score on 'self'
                 (if no Klout is present, this returns a None)
        """
        return tweet_user.get_klout_score(self)

    @lazy_property
    def klout_profile(self):
        """
        The Klout profile URL of the user (str) (if it exists)

        Returns:
            str: value returned by calling tweet_user.get_klout_profile on 'self'
                 (if no Klout is present, this returns a None)
        """
        return tweet_user.get_klout_profile(self)

    @lazy_property
    def klout_id(self):
        """
        The Klout ID of the user (str) (if it exists)

        Returns:
            str: value returned by calling tweet_user.get_klout_id on 'self'
                 (if no Klout is present, this returns a None)
        """
        return tweet_user.get_klout_id(self)

    @lazy_property
    def klout_influence_topics(self):
        """
        Get the user's Klout influence topics (a list of dicts), if it exists.
        Topic dicts will have these keys: url, id, name, score

        Returns:
            list: value returned by calling
                  tweet_user.get_klout_topics(self, topic_type = 'influence')
                  (if no Klout is present, this returns a None)
        """
        return tweet_user.get_klout_topics(self, topic_type='influence')

    @lazy_property
    def klout_interest_topics(self):
        """
        Get the user's Klout interest topics (a list of dicts), if it exists.
        Topic dicts will have these keys: url, id, name, score

        Returns:
            list: value returned by calling
                  tweet_user.get_klout_topics(self, topic_type = 'interest')
                  (if no Klout is present, this returns a None)
        """
        return tweet_user.get_klout_topics(self, topic_type='interest')

    @lazy_property
    def text(self):
        """
        The contents of "text" (original format) 
        or "body" (activity streams format)

        Returns:
            str: value returned by calling tweet_text.get_text on 'self'
        """
        return tweet_text.get_text(self)

    @lazy_property
    def tweet_type(self):
        """
        The type of Tweet this is (3 options: tweet, quote, and retweet

        Returns:
            str: ("tweet","quote" or "retweet" only)
                 value returned by calling tweet_text.get_tweet_type on 'self'
        """
        return tweet_text.get_tweet_type(self)

    @lazy_property
    def user_entered_text(self):
        """
        The text that the posting user entered 
         - tweet: untruncated (includes @-mention replies and long links)
                  text of an original Tweet
         - quote tweet: untruncated poster-added content in a quote-tweet
         - retweet: empty string

        Returns:
            str: if tweet.tweet_type == "retweet", returns an empty string
                 else, returns the value of tweet_text.get_full_text(self)
        """
        if self.tweet_type == "retweet":
            return ""
        return tweet_text.get_full_text(self)

    @lazy_property
    def poll_options(self):
        """
        The text in the options of a poll as a list
         - If there is no poll in the Tweet, return an empty list
         - If activity-streams format, raise 'NotAvailableError'

        Returns:
            list (list of strings): value returned by calling
                                    tweet_text.get_poll_options on 'self'
        """
        return tweet_text.get_poll_options(self)

    @lazy_property
    def quote_or_rt_text(self):
        """
        The quoted or retweeted text in a Tweet
        (this is not the text entered by the posting user)
         - tweet: empty string (there is no quoted or retweeted text)
         - quote: only the text of the quoted Tweet
         - retweet: the text of the retweet

        Returns:
            str: value returned by calling
                 tweet_text.get_quote_or_rt_text on 'self'
        """
        return tweet_text.get_quote_or_rt_text(self)

    @lazy_property
    def all_text(self):
        """
        All of the text of the tweet. This includes @ mentions, long links,
        quote-tweet contents (separated by a newline), RT contents
        & poll options

        Returns:
            str: value returned by calling tweet_text.get_all_text on 'self'
        """
        return tweet_text.get_all_text(self)

    @lazy_property
    def geo_coordinates(self):
        """
        The user's geo coordinates, if they are included in the payload
        (otherwise return None)

        Returns:
            dict: dictionary with the keys "latitude" and "longitude" or None
            value returned by calling tweet_geo.get_geo_coordinates on 'self'
        """
        return tweet_geo.get_geo_coordinates(self)

    @lazy_property
    def profile_location(self):
        """
        User's derived location data from the profile location enrichment
        If unavailable, returns None.

        Returns:
            dict: {"country":     Two letter ISO-3166 country code
                   "locality":    The locality location (~ city)
                   "region":      The region location (~ state/province)
                   "sub_region":  The sub-region location (~ county)
                   "full_name":   The full name (excluding sub-region)
                   "geo":         An array that includes a lat/long value
                                  coordinate that corresponds to the lowest
                                  granularity location for where the user that
                                  created the Tweet is from
                   }
            value returned by calling tweet_geo.get_profile_location on 'self'
        """
        return tweet_geo.get_profile_location(self)

    @lazy_property
    def tweet_links(self):
        """
        The links that are included in the Tweet as "urls"
        (if there are no links, this is an empty list)
        This includes links that are included in quoted or retweeted Tweets
        Returns unrolled or expanded_url information if it is available

        Returns:
            list (list of dicts): A list of dictionaries containing information
            about urls. Each dictionary entity can have these keys; without
            unwound url or expanded url Twitter data enrichments many of these
            fields will be missing.
                {'display_url': the url that shows up in the tweet text
                 'expanded_url': long (expanded) url,
                 'indices': [55, 78], # characters where the display link is
                 'unwound': {
                    'description': description from the linked webpage
                    'status': 200,
                    'title': title of the webpage,
                    'url': long (expanded) url},
                 'url': url the tweet directs to, often t.co}
            value returned by calling tweet_links.get_tweet_links on 'self'
        """
        return tweet_links.get_tweet_links(self)

    @lazy_property
    def most_unrolled_urls(self):
        """
        For each url included in the Tweet "urls", get the most unrolled
        version available. Only return 1 url string per url in tweet.tweet_links
        In order of preference for "most unrolled":
          Keys from the dict at tweet.tweet_links:
            1. "unwound"/"url"
            2. "expanded_url"
            3. "url"

        Returns:
            list (a list of strings): list of urls
            value returned by calling tweet_links.get_most_unrolled_urls on 'self'
        """
        return tweet_links.get_most_unrolled_urls(self)

    @lazy_property
    def user_mentions(self):
        """
        The @-mentions in the Tweet as dictionaries.

        Returns:
            list (list of dicts): 1 item per @ mention, each item has the fields:
                 {
                    "indices": [14,26], #characters where the @ mention appears
                    "id_str": "2382763597", #id of @ mentioned user as a string
                    "screen_name": "notFromShrek", #screen_name of @ mentioned user
                    "name": "Fiona", #display name of @ mentioned user
                    "id": 2382763597 #id of @ mentioned user as an int
                  }
            value returned by calling tweet_entities.get_user_mentions on 'self'
        """
        return tweet_entities.get_user_mentions(self)

    @lazy_property
    def quoted_user(self):
        """
        quoted users don't get included in the @ mentions
        which doesn't seem that intuitive, so I'm adding a getter to add them
        """
        return tweet_entities.get_quoted_user(self)

    @lazy_property
    def quoted_mentions(self):
        """
        users mentioned in the quoted Tweet don't get included
        which doesn't seem that intuitive, so I'm adding a getter to add them
        """
        return tweet_entities.get_quoted_mentions(self)

    @lazy_property
    def hashtags(self):
        """
        A list of hashtags in the Tweet

        Returns:
            list (a list of strings): list of all of the hashtags in the Tweet
            value returned by calling tweet_entities.get_hashtags on 'self'
        """
        return tweet_entities.get_hashtags(self)

    @lazy_property
    def quote_tweet(self):
        """
        get the quote tweet and return a tweet obj of the quote tweet
        """
        quote_tweet = tweet_embeds.get_quote_tweet(self)
        if quote_tweet is not None:
            try:
                return Tweet(quote_tweet)
            except NotATweetError as nate:
                raise(NotATweetError("The quote-tweet payload appears malformed. Failed with '{}'".format(nate)))

    @lazy_property
    def retweet(self):
        """
        get the retweet and return a tweet obj of the retweet
        """
        retweet = tweet_embeds.get_retweet(self)
        if retweet is not None:
            try:
                return Tweet(retweet)
            except NotATweetError as nate:
                raise(NotATweetError("The retweet payload appears malformed. Failed with '{}'".format(nate)))

    @lazy_property
    def embedded_tweet(self):
        """
        get the quote tweet or the retweet and return a tweet object of it
        """
        embedded_tweet = tweet_embeds.get_embedded_tweet(self)
        if embedded_tweet is not None:
            try:
                return Tweet(embedded_tweet)
            except NotATweetError as nate:
                raise(NotATweetError("The embedded tweet payload {} appears malformed. \nFailed with '{}'".format(embedded_tweet, nate)))
