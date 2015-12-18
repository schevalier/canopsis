
from canopsis.event.check import Check
from canopsis.configuration.configurable.decorator import conf_paths
from canopsis.configuration.configurable.decorator import add_category


CONF_PATH = 'event/selector.conf'
CATEGORY = 'SELECTOR'
CONTENT = []


class Selector(Check):
    DEFAULT_EVENT_TYPE = 'selector'

    @classmethod
    def get_configurable(cls):
        confcls = Check.get_configurable()

        conf_decorator = conf_paths(CONF_PATH)
        cat_decorator = add_category(CATEGORY, content=CONTENT)

        return conf_decorator(cat_decorator(confcls))
