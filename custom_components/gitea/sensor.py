"""Platform for sensor integration."""
import logging
import json
import requests
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_TOKEN,
    CONF_PORT,
    CONF_HOST,
    CONF_PATH,
    CONF_NAME,
    CONF_PROTOCOL,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "gitea"
CONF_REPOS = "repositories"
ATTR_REPO_NAME = "Repository"
ATTR_REPO_ID = "ID"
ATTR_DESCRIPTION = "Description"
ATTR_OPEN_ISSUES = "Open issues"
ATTR_DEFAULT_BR = "Branch"
ATTR_OWNER = "Owner"
ATTR_SIZE = "Size"
ATTR_PRIVATE_REPO = "isPrivate"
ATTR_FORK = "Forks"
ATTR_MIRROR = "isMirror"
ATTR_REPO_URL = "Repository Url"
ATTR_STARS = "Stars"
ATTR_WATCH = "Watchers"
ATTR_UPDATED_AT = "Updated at"
ATTR_LAST_ISSUE_LINK = "Last Issue Link"
ATTR_LAST_ISSUE_STATE = "Last Issue Status"
ATTR_LAST_ISSUE_TITLE = "Last Issue Title"
ATTR_ALL_ISSUES = "All Issues"


URL_ISSUE = "/issues?state=all"


REPO_SCHEMA = vol.Schema(
    {vol.Required(CONF_PATH): cv.string, vol.Optional(CONF_NAME): cv.string}
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_TOKEN): cv.string,
        vol.Required(CONF_PORT): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PROTOCOL): cv.string,
        vol.Required(CONF_REPOS): vol.All(cv.ensure_list, [REPO_SCHEMA]),
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup Platform."""
    for repo in config[CONF_REPOS]:
        add_entities(
            [
                GiteaSensor(
                    config.get(CONF_TOKEN),
                    config.get(CONF_PROTOCOL),
                    config.get(CONF_HOST),
                    config.get(CONF_PORT),
                    repo,
                )
            ]
        )


class GiteaSensor(Entity):
    """Representation of a Sensor."""

    def __init__(
        self,
        token=None,
        proto=None,
        api_url=None,
        api_port=None,
        repo=None,
        id=None,
        description=None,
        open_issues_count=None,
        default_branch=None,
        size=None,
        owner_name=None,
        private=None,
        stars=None,
        fork=None,
        mirror=None,
        url=None,
        updated_at=None,
        issue_title=None,
        issue_link=None,
        issue_state=None,
        all_issues=None,
    ):
        self._state = None
        self.token = token
        self.proto = proto
        self.api_url = api_url
        self.api_port = api_port
        self.repo = repo[CONF_PATH]
        self.id_repo = id
        self.description = description
        self.open_issues_count = open_issues_count
        self.default_branch = default_branch
        self.size = size
        self.owner_name = owner_name
        self.private = private
        self.mirror = mirror
        self.fork = fork
        self.stars = stars
        self.url = url
        self.watcher = None
        self.updated_at = updated_at
        self.issue_title = issue_title
        self.issue_link = issue_link
        self.issue_state = issue_state
        self.all_issues = all_issues

    @property
    def name(self):
        """Return the name of the sensor."""
        return DEFAULT_NAME + "_" + self.repo.split("/")[1]

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:tea"

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            ATTR_REPO_ID: self.id_repo,
            ATTR_REPO_NAME: self.repo,
            ATTR_OWNER: self.owner_name,
            ATTR_PRIVATE_REPO: self.private,
            ATTR_FORK: self.fork,
            ATTR_MIRROR: self.mirror,
            ATTR_STARS: self.stars,
            ATTR_DESCRIPTION: self.description,
            ATTR_OPEN_ISSUES: self.open_issues_count,
            ATTR_DEFAULT_BR: self.default_branch,
            ATTR_REPO_URL: self.url,
            ATTR_SIZE: self.size,
            ATTR_WATCH: self.watcher,
            ATTR_UPDATED_AT: self.updated_at,
            ATTR_LAST_ISSUE_LINK: self.issue_link,
            ATTR_LAST_ISSUE_STATE: self.issue_state,
            ATTR_LAST_ISSUE_TITLE: self.issue_title,
            ATTR_ALL_ISSUES: self.all_issues,
        }
        return attrs

    def update(self):
        """Update all sensor attributes."""
        infos = self.api_call(self.generate_url())
        self.id_repo = infos["id"]
        self.description = infos["description"]
        self.open_issues_count = infos["description"]
        self.open_issues_count = infos["open_issues_count"]
        self.default_branch = infos["default_branch"]
        self.size = str(infos["size"]) + " Mo"
        self.owner_name = infos["owner"]["login"]
        self.private = infos["private"]
        self.mirror = infos["mirror"]
        self.stars = infos["stars_count"]
        self.fork = infos["forks_count"]
        self.url = infos["html_url"]
        self._state = infos["default_branch"]
        self.watcher = infos["watchers_count"]
        self.updated_at = infos["updated_at"]

        if infos["open_issues_count"] != 0:
            issues_tab = []
            issues = self.api_call(self.generate_url(URL_ISSUE))
            self.issue_link = issues[0]["html_url"]
            self.issue_state = issues[0]["state"]
            self.issue_title = issues[0]["title"]

            for iss in issues:
                card_items = {}
                card_items["id"] = iss["id"]
                card_items["state"] = iss["state"]
                card_items["title"] = iss["title"]
                card_items["url"] = iss["html_url"]
                issues_tab.append(card_items)

            self.all_issues = json.dumps(issues_tab)

    def generate_url(self, path=""):
        """Return api url."""
        return "{0}://{1}:{2}/api/v1/repos/{3}/{4}{5}".format(
            self.proto,
            self.api_url,
            self.api_port,
            self.repo.split("/")[0],
            self.repo.split("/")[1],
            path,
        )

    def get_header(self):
        """Return headers for api request."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {0}".format(self.token),
        }
        return headers

    def api_call(self, url):
        """Return result of api request."""
        return requests.request(method="GET", url=url, headers=self.get_header()).json()
