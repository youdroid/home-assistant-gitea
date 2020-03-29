"""Platform for sensor integration."""
import logging
import requests
import json
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import PLATFORM_SCHEMA
import xml.etree.ElementTree as ET
from homeassistant.const import CONF_TOKEN, CONF_PORT, CONF_HOST, CONF_PATH, CONF_NAME, CONF_USERNAME, CONF_PROTOCOL

_LOGGER = logging.getLogger(__name__)

CONF_REPOS = "repositories"

REPO_SCHEMA = vol.Schema(
    {vol.Required(CONF_PATH): cv.string, vol.Optional(CONF_NAME): cv.string}
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TOKEN): cv.string,
    vol.Required(CONF_PORT): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PROTOCOL): cv.string,
    vol.Required(CONF_REPOS): vol.All(cv.ensure_list, [REPO_SCHEMA])

})


def setup_platform(hass, config, add_entities, discovery_info=None):
    for repo in config[CONF_REPOS]:
        add_entities([DealabsSensor(config.get(CONF_USERNAME), config.get(CONF_TOKEN), config.get(CONF_PROTOCOL),
        config.get(CONF_HOST), config.get(CONF_PORT), repo)])


class DealabsSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, username=None, token=None, proto=None, api_url=None, api_port=None, repo=None,
                 id=None, description=None, open_issues_count=None, default_branch=None, size=None,
                 owner_name=None, private=None):
        self._state = None
        self.token = token
        self.proto = proto
        self.api_url = api_url
        self.api_port = api_port
        self.username = username
        self.repo = repo[CONF_PATH]
        self.id_repo = id
        self.description = description
        self.open_issues_count = open_issues_count
        self.default_branch = default_branch
        self.size = size
        self.owner_name = owner_name
        self.private = private

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Gitea"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:coffee"

    def update(self):
        join_url = str(self.proto) + "://" + str(self.api_url) + str(self.api_port) + "/api/v1/repos/" + str(self.username) + "/" + str(self.repo);
        _LOGGER.error(join_url)
        _LOGGER.error(self.getHeader())
        rqt = requests.request(method='GET', url=join_url, headers=self.getHeader()).json()
        _LOGGER.error(rqt)
        self.id_repo = rqt["id"]
        self.description = rqt["description"]
        self.open_issues_count = rqt["description"]
        self.open_issues_count = rqt["open_issues_count"]
        self.default_branch = rqt["default_branch"]
        self.size = rqt["size"]
        self.owner_name = rqt["owner"]["login"]
        self.private = rqt["private"]

    def getHeader(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }
        return headers