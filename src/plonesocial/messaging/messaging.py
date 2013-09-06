import time

from BTrees.LOBTree import LOBTree
from BTrees.OOBTree import OOBTree
from Persistence import Persistent
from zope.interface import implementer
from zope.interface.verify import verifyObject

from plonesocial.messaging.interfaces import IConversation, IInbox, IInboxes
from plonesocial.messaging.interfaces import IMessage, IMessagingLocator


@implementer(IMessage)
class Message(Persistent):

    __parent__ = None

    sender = None
    recipient = None
    text = None
    created = None
    deleted = None
    uuid = None
    new = True

    def __init__(self, sender, recipient, text, created):
        if sender == recipient:
            raise ValueError('Sender and recipient are identical'
                             '(%s, %s)' % (sender, recipient))  # FIXME: test
        if not text.strip():
            raise ValueError('Message has no text')  # FIXME: test

        self.sender = sender
        self.recipient = recipient
        self.text = text
        self.created = created


@implementer(IConversation)
class Conversation(LOBTree):

    __parent__ = None

    username = None
    last_updated = None
    new_messages_count = 0

    def __init__(self, username, created):
        self.username = username
        self.last_updated

    def to_long(self, dt):
        """Turns a `datetime` object into a long"""
        return long(time.mktime(dt.timetuple()) * 1000000 + dt.microsecond)

    def generate_key(self, message):
        """Generate a long int key for a message"""
        key = self.to_long(message.created)
        while key in self:
            key = key + 1
        return key

    def add_message(self, message):
        key = self.generate_key(message)
        message.uid = key
        self[key] = message
        return key

    def __setitem__(self, key, message):
        if key != message.uid:
            raise KeyError('key and message.uid differ (%s/%s)' %
                           (key, message.uid))
        message.__parent__ = self

        # delete old message if there is one to make sure the
        # new_messages_count is correct and update the new_messages_count
        # with the new message
        if key in self:
            del self[key]
        if message.new is True:
            self.update_new_messages_count(+1)

        super(Conversation, self).__setitem__(key, message)

    def __delitem__(self, uid):
        message = self[uid]
        if message.new is True:
            self.update_new_messages_count(-1)
        super(Conversation, self).__delitem__(uid)

    def get_messages(self):
        return self.values()

    def mark_read(self):
        # use update function to update inbox too
        self.update_new_messages_count(self.new_messages_count * -1)

        # update messages
        for message in self.values():
            message.new = False

    def update_new_messages_count(self, difference):
        count = self.new_messages_count
        count = count + difference
        if count < 0:
            # FIXME: Error. Log?
            count = 0
        self.new_messages_count = count

        # update the inbox accordingly
        self.__parent__.update_new_messages_count(difference)


@implementer(IInbox)
class Inbox(OOBTree):

    __parent__ = None

    username = None
    new_messages_count = 0

    def __init__(self, username):
        self.username = username

    def add_conversation(self, conversation):
        self[conversation.username] = conversation
        return conversation

    def __setitem__(self, key, conversation):
        if key != conversation.username:
            raise KeyError('conversation.username and key differ (%s, %s)' %
                           (conversation.username, key))

        if conversation.username == self.username:
            raise ValueError("You can't speak to yourself")

        verifyObject(IConversation, conversation)

        if key in self:
            raise KeyError('Conversation exists already')

        super(Inbox, self).__setitem__(conversation.username, conversation)
        conversation.__parent__ = self
        self.update_new_messages_count(conversation.new_messages_count)
        return conversation

    def __delitem__(self, key):
        conversation = self[key]
        self.update_new_messages_count(conversation.new_messages_count * -1)
        super(Inbox, self).__delitem__(key)

    def get_conversations(self):
        return self.values()

    def is_blocked(self, username):
        # FIXME: not implemented
        return False

    def update_new_messages_count(self, difference):
        count = self.new_messages_count
        count = count + difference
        if count < 0:
            # FIXME: Error. Log?
            count = 0
        self.new_messages_count = count


@implementer(IInboxes)
class Inboxes(OOBTree):

    __parent__ = None

    def add_inbox(self, username):
        if username in self:
            raise ValueError('Inbox for user %s exists' % username)

        inbox = Inbox(username)
        self[username] = inbox
        return inbox

    def __setitem__(self, key, inbox):
        verifyObject(IInbox, inbox)
        if key != inbox.username:
            raise KeyError("Inbox username and key differ (%s/%s)" %
                           (inbox.username, key))
        inbox.__parent__ = self
        return super(Inboxes, self).__setitem__(key, inbox)


@implementer(IMessagingLocator)
class MessagingLocator(object):
    """A utility used to locate conversations and messages.
    """