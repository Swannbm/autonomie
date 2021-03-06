# -*- coding: utf-8 -*-
# * Authors:
#       * TJEBBES Gaston <g.t@majerti.fr>
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
import logging
from autonomie.exception import (
    Forbidden,
    BadRequest,
)


logger = logging.getLogger(__name__)


class Action(object):
    """
        a state object with a name, permission and a callback callbacktion
        :param name: The state name
        :param permission: The permission needed to set this state
        :param callback: A callback function to call on state process
        :param status_attr: The attribute storing the model's status
        :param userid_attr: The attribute storing the status person's id
    """
    def __init__(
        self,
        name,
        permission,
        callback=None,
        status_attr=None,
        userid_attr=None,
        **kwargs
    ):
        self.name = name
        if not hasattr(permission, "__iter__"):
            permission = [permission]
        self.permissions = permission
        self.callback = callback
        self.status_attr = status_attr
        self.userid_attr = userid_attr
        self.options = kwargs

    def allowed(self, context, request):
        """
        return True if this state assignement on context is allowed
        in the current request

        :param obj context: An object with acl
        :param obj request: The Pyramid request object
        :returns: True/False
        :rtype: bool
        """
        res = False
        for permission in self.permissions:
            if request.has_permission(permission, context):
                res = True
                break

        return res

    def __json__(self, request):
        result = dict(
            status=self.name,
            value=self.name,
        )
        result.update(self.options)
        return result

    def process(self, model, request, user_id, **kw):
        """
        Process the action

        Set the model's status_attr if needed (status)
        Set the model's status user_id attribute if needed (status_person_id)

        Fire a callback if needed
        """
        if self.status_attr is not None:
            setattr(model, self.status_attr, self.name)
        if self.userid_attr:
            setattr(model, self.userid_attr, user_id)
        if self.callback:
            return self.callback(request, model, user_id=user_id, **kw)
        else:
            return model

    def __repr__(self):
        return (
            "< State %s allowed for %s (status_attr : %s, "
            "userid_attr : %s )>" % (
                self.name, self.permissions, self.status_attr, self.userid_attr
            )
        )


class ActionManager(object):
    def __init__(self):
        self.items = []

    def add(self, action):
        self.items.append(action)

    def get_allowed_actions(self, request, context=None):
        """
        Return the list of next available actions regarding the current user
        perm's

        """
        result = []
        context = context or request.context

        for action in self.items:
            if action.allowed(context, request):
                result.append(action)
        return result

    def _get_action(self, action_name):
        """
        Retrieve the action called "action_name"

        :param str action_name: The name of the action we're looking for
        :returns: An instance of Action
        """
        action = None
        for item in self.items:
            if item.name == action_name:
                action = item
                break
        return action

    def check_allowed(self, action_name, context, request):
        """
        Check that the given status could be set on the current context

        :param str action_name: The name of the action
        :param obj context: The context to manage
        :param obj request: The current request object
        :raises: Forbidden if the action isn't allowed
        :raises: BadRequest if the action doesn't exists
        """
        context = context or request.context
        action = self._get_action(action_name)

        if action is None:
            logger.error("Unknown action : %s" % action_name)
            raise BadRequest()

        elif not action.allowed(context, request):
            raise Forbidden(
                u"This action is not allowed for %s : %s" % (
                    request.user.id,
                    action_name,
                )
            )
        return action

    def process(self, action_name, context, request, **params):
        """
        Process a specific action

        :param str action_name: The name of the action
        :param obj context: The context to manage
        :param obj request: The current request object
        :param dict params: The params to pass to the callback

        :raises: colander.Invalid if the action is unknown
        :raises: Forbidden if the action is not allowed for the current request
        """
        action = self.check_allowed(action_name, context, request)
        return action.process(context, request, request.user.id, **params)
