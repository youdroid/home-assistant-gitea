"""Platform for sensor integration."""
import logging
import requests
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import CONF_TOKEN, CONF_PORT, CONF_HOST, CONF_PATH, CONF_NAME, CONF_PROTOCOL

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

REPO_SCHEMA = vol.Schema(
    {vol.Required(CONF_PATH): cv.string, vol.Optional(CONF_NAME): cv.string}
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TOKEN): cv.string,
    vol.Required(CONF_PORT): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PROTOCOL): cv.string,
    vol.Required(CONF_REPOS): vol.All(cv.ensure_list, [REPO_SCHEMA])

})


def setup_platform(hass, config, add_entities, discovery_info=None):
    for repo in config[CONF_REPOS]:
        add_entities([GiteaSensor(config.get(CONF_TOKEN), config.get(CONF_PROTOCOL),
                                  config.get(CONF_HOST), config.get(CONF_PORT), repo)])


class GiteaSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, token=None, proto=None, api_url=None, api_port=None, repo=None,
                 id=None, description=None, open_issues_count=None, default_branch=None, size=None,
                 owner_name=None, private=None, stars=None, fork=None, mirror=None, url=None):
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

    @property
    def name(self):
        """Return the name of the sensor."""
        return DEFAULT_NAME + "_" + self.repo.split('/')[1]

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
            ATTR_WATCH: self.watcher
        }
        return attrs

    def update(self):
        infos = self.apiCall()
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

    def getUrl(self):
        return '{0}://{1}:{2}/api/v1/repos/{3}/{4}'.format(self.proto, self.api_url, self.api_port, self.repo.split('/')[0],
                                                           self.repo.split('/')[1])

    def getHeader(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(self.token)
        }
        return headers

    def apiCall(self):
        return requests.request(method='GET', url=self.getUrl(), headers=self.getHeader()).json()







