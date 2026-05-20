"""Chat channels module with plugin architecture."""

from kid_agent.tutorbot.channels.base import BaseChannel
from kid_agent.tutorbot.channels.manager import ChannelManager

__all__ = ["BaseChannel", "ChannelManager"]
