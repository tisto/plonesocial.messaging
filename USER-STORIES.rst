User Stories
==============================================================================

As a member I can send a message to another member
--------------------------------------------------

Core functionality. Simple z3c.form form (@@send-message) that writes a
message with the proper metadata into our custom data structure.


As a member I can browse through my messages
--------------------------------------------

Simple view (@@messages) that returns json or HTML based on the currently
logged in user.


As a member I can view a list of members that I have exchanged messages with
----------------------------------------------------------------------------

Simple view that returns json or HTML.


As a member I am notified if I received a message from another member
---------------------------------------------------------------------

plonesocial.messaging should fire events that integrators can use for the
notification.


As a member I can see unread messages
-------------------------------------

The @@messages view should return the messages with an unread flag.


As a member I can delete a single message
-----------------------------------------

Simple @@delete-message (with a message ID param). Should return True/False.


As a member I can delete a conversation with another member
-----------------------------------------------------------

Simple @@delete-conversation (with a member ID param). Should return True/False.


As a member I can insert links into my message
----------------------------------------------

Use https://pypi.python.org/pypi/plone.intelligenttext text transform for
messages.


As a member I can forward a message to the moderators
-----------------------------------------------------

This should fire up an event handler that integrators can use.
