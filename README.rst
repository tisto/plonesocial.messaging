.. contents::

Introduction
============

.. image:: https://travis-ci.org/tisto/plonesocial.messaging.png?branch=master
    :target: http://travis-ci.org/tisto/plonesocial.messaging


plonesocial.messaging provides a base to send private messages between plone
users. The messages are stored in a seperate tree outside the user folders
and are not plone content for performance reasons.

This packages provides only the building block without integration to plone.

The functionality provided is:

* Send a message from one user to another.
* List the conversations a user has with the amount of unread
  messages and the time of the last update. A conversation is the
  list of messages between two users. There is only one conversation
  between two users.
* List the messages in a conversation.
* Mark a conversation read.
* Delete a message or the whole conversation.



Usage
=====

First we want to get the messaging tool

    >>> from datetime import datetime
    >>> from plonesocial.messaging.interfaces import IMessagingLocator
    >>> from zope.component import getUtility
    >>> locator = getUtility(IMessagingLocator)
    >>> inboxes = locator.get_inboxes()

Now we can start sending messages between users. As we don't care about
the 'real' users, we do not need any members in the site to start.
(If you don't specify the creation date, it will default to datetime.now())

    >>> bob = 'Bob'
    >>> dave = 'Dave'
    >>> inboxes.send_message(bob, dave, 'Hi Dave',
    ...                      created=datetime(2013, 1, 1))

`Inboxes.send_message()` will take care to create the inboxes for Bob
and Dave, Conversations in both inboxes and add the Message to both
Inboxes. Inboxes are `Inbox` objects inside the `Inboxes` container.
All Objects except messages provide a dict api.

    >>> bob in inboxes
    True
    >>> dave in inboxes
    True
    >>> daves_inbox = inboxes[dave]
    >>> daves_inbox
    <plonesocial.messaging.messaging.Inbox object at ...>


In Dave's inbox we can find his conversation with Bob that Dave did
not read yet

    >>> conversation = daves_inbox[bob]
    >>> conversation
    <plonesocial.messaging.messaging.Conversation object at ...>
    >>> conversation.new_messages_count
    1
    >>> conversation.username
    'Bob'

Messages are returned in an iterable that yields its itmes, not in a
real list. So we iterate over the messages to get the content

    >>> def print_messages(conversation):
    ...     for message in conversation.get_messages():
    ...         print 'sender:', message.sender
    ...         print 'recipient:', message.recipient
    ...         print 'text:', message.text
    ...         print 'created:', message.created
    ...         print 'new:', message.new

    >>> print_messages(conversation)
    sender: Bob
    recipient: Dave
    text: Hi Dave
    created: 2013-01-01 00:00:00
    new: True

Now let Dave read his mail and answer Bob. His message will show up in
the conversation.

    >>> conversation.mark_read()
    >>> print_messages(conversation)
    sender: Bob
    recipient: Dave
    text: Hi Dave
    created: 2013-01-01 00:00:00
    new: False

    >>> inboxes.send_message(dave, bob, 'Thanks Bob',
    ...                      created=datetime(2013, 1, 2))
    >>> print_messages(conversation)
    sender: Bob
    recipient: Dave
    text: Hi Dave
    created: 2013-01-01 00:00:00
    new: False
    sender: Dave
    recipient: Bob
    text: Thanks Bob
    created: 2013-01-02 00:00:00
    new: True


Now Dave does not want to keep the conversation with Bob and deletes it:

    >>> del inboxes[dave][bob]
    >>> list(inboxes[dave].get_conversations())
    []

Even then Bob still has the conversation with Dave in his inbox:

    >>> print_messages(inboxes[bob][dave])
    sender: Bob
    recipient: Dave
    text: Hi Dave
    created: 2013-01-01 00:00:00
    new: True
    sender: Dave
    recipient: Bob
    text: Thanks Bob
    created: 2013-01-02 00:00:00
    new: True
