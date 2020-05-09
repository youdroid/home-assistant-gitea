# Gitea repository tracker

Home Assistant component to feed Home Assistant component to feed all your repositories on Gitea.

## Installation
1. Install this component by copying [these files](https://github.com/youdroid/home-assistant-gitea/tree/master/custom_components/gitea) to `custom_components/gitea/`.
2. Install the card: [Entity attributes](https://github.com/custom-cards/entity-attributes-card)
3. Add the code to your `configuration.yaml` using the config options below.
4. Add the card code to your `ui-lovelace.yaml`. 
5. **You will need to restart after installation for the component to start working.**

### Options

| key | default | required | description
| --- | --- | --- | ---
| token | | yes | Your Gitea token [(Find your Gitea token)](https://wiki.debian.org/Gitea)
| host |  | yes | The host which Gitea is running on.
| protocol |  | yes | The HTTP protocol used by Gitea.
| port |  | yes | The port which Gitea is running on.
| repositories |  | yes | A List of your repositores you want to track that contain repository path.

## Exemples

### Example for minimal config needed in configuration.yaml:
```yaml
    sensor:
      - platform: gitea
        token: YOUR_GITEA_TOKEN
        host: localhost
        protocol: http
        port: 80
        repositories:
          - path: 'user/crazy_repo'
```
### Example for ui-lovelace.yaml:
```yaml
    - type: custom:entity-attributes-card
      title: Gitea repository 
       heading_name: Attributes
       heading_state: States
       filter:
         include:
           - key: sensor.gitea_crazy_repo.*
```
### Multiple repositories for configuration.yaml:
```yaml
    sensor:
      - platform: gitea
        token: YOUR_GITEA_TOKEN
        host: localhost
        protocol: http
        port: 80
        repositories:
          - path: 'user/crazy_repo'
          - path: 'user/awesome_repo'
          - path: 'user/amazing _repo'

```