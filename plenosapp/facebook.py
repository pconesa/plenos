import os
from plenos import settings
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
import logging
logger = logging.getLogger(__name__)


def postOnFacebook(message):

    try:

        app_id = settings.FB_PLENOS_APP_ID # App Id - Identificador de plenos app
        page_id = settings.FB_PLENOS_ID # Page id de plenos
        plenos_access_token = settings.FB_PLENOS_ACCESS_TOKEN # THis one expires every 2 hours need a better solution
        app_secret = settings.FB_PLENOS_SECRET

        # Initialize FB api
        FacebookAdsApi.init(app_id, app_secret, plenos_access_token)

        page = Page(page_id)
        page.create_feed(fields=[],params={'message':message})
        logger.info("Message posted on plenos feed: %s" % message)
    except Exception as e:
        logger.error("Message NOT posted on plenos feed: %s" % message, exc_info=e)