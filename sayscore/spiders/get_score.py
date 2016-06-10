import scrapy

from lxml import html
from selenium import webdriver
from sayscore.items import SayscoreItem


class BaseSpider(scrapy.Spider):
    """
    Base spider that help you crawl all data
    through out the domain given in start urls
    """
    name = "score"
    allowed_domains = []
    start_urls = ['http://synd.cricbuzz.com/j2me/1.0/livematches.xml']
    banned_responses = [404, 500, ]

    def __init__(self):
        super(BaseSpider, self).__init__()

    def __avoid_unwanted_responses(self, status):
        """
        Checks for valid responses
        :param status:
        :return: Boolean
        """
        if status in self.banned_responses:
            return False
        return True

    def parse(self, response):
        """
        Parses the main html response
        :param response:
        :return:
        """
        if self.__avoid_unwanted_responses(response.status):
            driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])
            driver.get(self.start_urls)
            doc = html.fromstring(driver.page_source)
            matches = doc.xpath('.//match')
            if matches:
                details = self.get_match(matches)
                item = SayscoreItem()
                item['match_details'] = details
                yield item

    def get_match(self, matches):
        """
        Get match details from matches
        :param matches:
        :return:
        """
        details = []
        for match in matches:
            detail = self.get_details(match)
            details.append(detail)
            detail = self.get_test_details(match)
            details.append(detail)
        return details

    def get_test_details(self, match):
        """
        For handling Test Matches
        :param match:
        :return:
        """
        series = match.xpath('.//@srs')[0]
        match_type = match.xpath('.//@type')
        if match_type[0] != "TEST":
            return None

        desc = match.xpath('.//@mchdesc')[0]
        ground = match.xpath('.//@grnd')[0]
        state = match.xpath('.//state/@mchstate')[0]
        status = match.xpath('.//state/@status')[0]
        if status[0].startswith("Starts") or status[0].startswith("Coming"):
            return None      #Match hasn't started Yet
        try:
            batting_team_name = match.xpath('.//mscr/bttm/@sname')[0]
            bowling_team_name = match.xpath('.//mscr/blgtm/@sname')[0]
            bat_runs = match.xpath('.//mscr/bttm/inngs/@r')[0]
            bat_overs = match.xpath('.//mscr/bttm/inngs/@ovrs')[0]
            bat_wickets = match.xpath('.//mscr/bttm/inngs/@wkts')[0]
            bat_desc = match.xpath('.//mscr/bttm/inngs/@desc')[0]
            bat_decl = match.xpath('.//mscr/bttm/inngs/@decl')[0]
            bat_follow_on = match.xpath('.//mscr/bttm/inngs/@followon')[0]

        except Exception:     #Match completed. Only Result is available now.
            batting_team_name = None
            bowling_team_name = None
            bat_runs = None
            bat_overs = None
            bat_wickets = None
            bat_desc = None
            bat_decl = None
            bat_follow_on = None

        try:
            bowl_runs = match.xpath('.//mscr/blgtm/inngs/@r')[0]
            bowl_overs = match.xpath('.//mscr/blgtm/inngs/@ovrs')[0]
            bowl_wickets = match.xpath('.//mscr/blgtm/inngs/@wkts')[0]

        except Exception:     # The opponent team hasn't yet started to Bat.
            bowl_runs = None
            bowl_overs = None
            bowl_wickets = None

        return { "Series": series, "Match_Format": "TEST", "Team": desc, "Venue":ground, "State": state,
                 "Status": status, "Batting_team": batting_team_name, "Bowling_team": bowling_team_name,
                 "Batting_Team_Runs": bat_runs, "Batting Team Overs": bat_overs, "Batting Team Wickets": bat_wickets,
                 "Bowling Team Runs": bowl_runs, "Bowling Team Overs": bowl_overs, "Bowling Team Wickets": bowl_wickets,
                 "Batting Innings": bat_desc,"Declare": bat_decl, "Follow On": bat_follow_on}

    def get_details(self, match):
        """
        For Handles ODI and T20 matches
        :param match:
        :return:
        """
        series = match.xpath('.//@srs')[0]
        match_type = match.xpath('.//@type')[0]
        if match_type == "TEST":
            return None

        desc = match.xpath('.//@mchdesc')[0]
        ground = match.xpath('.//@grnd')
        if ground:
            ground = ground[0]
        state = match.xpath('.//state/@mchstate')[0]
        status = match.xpath('.//state/@status')[0]
        if status[0].startswith("Starts") or status[0].startswith("Coming"):
            return None       #Match hasn't started Yet.
        try:
            batting_team_name = match.xpath('.//mscr/bttm/@sname')[0]
            bowling_team_name = match.xpath('.//mscr/blgtm/@sname')[0]
            bat_runs = match.xpath('.//mscr/bttm/inngs/@r')[0]
            bat_overs = match.xpath('.//mscr/bttm/inngs/@ovrs')[0]
            bat_wickets = match.xpath('.//mscr/bttm/inngs/@wkts')[0]

        except Exception:     #Match completed. Only Result is available now.
            batting_team_name = None
            bowling_team_name = None
            bat_runs = None
            bat_overs = None
            bat_wickets = None
        try:
            bowl_runs = match.xpath('.//mscr/blgtm/inngs/@r')[0]
            bowl_overs = match.xpath('.//mscr/blgtm/inngs/@ovrs')[0]
            bowl_wickets = match.xpath('.//mscr/blgtm/inngs/@wkts')[0]

        except Exception:     # The opponent team hasn't yet started to Bat.
            bowl_runs = None
            bowl_overs = None
            bowl_wickets = None

        return { "Series": series, "Match_Format": match_type, "Team": desc, "Venue":ground, "Match_State": state,
                 "Match_Status": status, "Batting_team": batting_team_name, "Bowling_team": bowling_team_name,
                 "Batting_Team_Runs": bat_runs, "Batting Team Overs": bat_overs, "Batting Team Wickets": bat_wickets,
                 "Bowling Team Runs": bowl_runs, "Bowling Team Overs": bowl_overs, "Bowling Team Wickets": bowl_wickets }
