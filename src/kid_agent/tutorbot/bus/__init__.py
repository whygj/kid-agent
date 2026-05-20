"""Message bus module for decoupled channel-agent communication."""

from kid_agent.tutorbot.bus.events import InboundMessage, OutboundMessage
from kid_agent.tutorbot.bus.queue import MessageBus

__all__ = ["MessageBus", "InboundMessage", "OutboundMessage"]
