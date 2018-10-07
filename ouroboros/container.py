import logging
import cli

log = logging.getLogger(__name__)

class NewContainerProperties:
    def __init__(self, old_container, new_image):
        """
        Store object for spawning new container in place of the one with outdated image
        """
        self.name = get_name(old_container)
        self.image = new_image
        self.command = old_container['Config']['Cmd']
        self.host_config = old_container['HostConfig']
        self.labels = old_container['Config']['Labels']
        self.detach = True
        self.entrypoint = old_container['Config']['Entrypoint']

def running():
    """Return running container objects list"""
    running_containers = []
    try:
        for container in cli.api_client.containers(filters={'status': 'running'}):
            running_containers.append(cli.api_client.inspect_container(container))
        return running_containers
    except:
        log.critical(f'Can\'t connect to Docker API at {cli.api_client.base_url}')

def to_monitor():
    """Return filtered running container objects list"""
    running_containers = []
    try:
        if cli.monitor:
            for container in cli.api_client.containers(filters={'name': cli.monitor, 'status': 'running'}):
                running_containers.append(cli.api_client.inspect_container(container))
        else:
            running_containers.extend(running())
        log.info(f'{len(running_containers)} running container(s) matched filter')
        return running_containers
    except:
        log.critical(f'Can\'t connect to Docker API at {cli.api_client.base_url}')

def get_name(container_object):
    """Parse out first name of container"""
    return container_object['Name'].replace('/','')

def stop(container_object):
    """Stop out of date container"""
    log.debug(f'Stopping container: {get_name(container_object)}')
    return cli.api_client.stop(container_object)

def remove(container_object):
    """Remove out of date container"""
    log.debug(f'Removing container: {get_name(container_object)}')
    return cli.api_client.remove_container(container_object)

def create_new_container(config):
    """Create new container with latest image"""
    return cli.api_client.create_container(**config)

def start(container_object):
    """Start newly created container with latest image"""
    log.debug(f"Starting container: {container_object['Id']}")
    return cli.api_client.start(container_object)
