import logging

from pyworks import Actor

logger = logging.getLogger(__file__)


class MathActor(Actor):
    def factorial(self, n):
        logger.debug("factorial(%d)" % n)
        i = n
        while i > 1:
            i -= 1
            n *= i
        logger.debug("fact done...")
        return n
