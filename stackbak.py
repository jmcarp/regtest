import this

import logging
logging.basicConfig(logging=logging.DEBUG)

class Stack(object):

    def __init__(self):
        self.data = []

    def __nonzero__(self):
        return bool(self.data)

    def push(self, item):
        self.data.append(item)

    def pop(self):
        return self.data.pop()

    def peek(self):
        try:
            return self.data[-1]
        except:
            pass

    def clear(self):
        self.data = []

class ContextKeyedStack(Stack):

    def __init__(self, context):
        self._context = context
        self._data = {}

    @property
    def context(self):
        return self._context.peek()

    @property
    def data(self):
        if self.context not in self._data:
            self._data[self.context] = []
        return self._data[self.context]

    @data.setter
    def data(self, value):
        self._data[self.context] = value

class Action(object):

    def _undo(self):
        logging.debug(('undoing', self, self.__class__))
        output = self.undo()
        logging.debug(output)
        self.redo_stack.push(self)
        return output

    def _redo(self):
        logging.debug(('doing', self, self.__class__))
        self.current_action.push(self)
        output = self.redo()
        logging.debug(output)
        self.undo_stack.push(self)
        self.current_action.pop()
        return output

    def _cleanup(self):
        logging.debug(('cleaning', self, self.__class__))
        self.cleanup()

    def redo(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError

    def cleanup(self):
        try:
            self.undo()
        except:
            pass

    @classmethod
    def clear(cls):
        cls.undo_stack.clear()
        cls.redo_stack.clear()
        cls.context_stack.clear()
        cls.current_action.clear()

    def call(self):
        return self._redo()

Action.context_stack = Stack()

Action.undo_stack = ContextKeyedStack(Action.context_stack)
Action.redo_stack = ContextKeyedStack(Action.context_stack)
Action.current_action = ContextKeyedStack(Action.context_stack)

class ActionContext(object):

    action_class = Action

    def __enter__(self):
        self.action_class.context_stack.push(self)

    def __exit__(self, type, value, traceback):
        if type is not None:
            print 'CRASH'
            # An exception was raised
            if self.action_class.current_action:
                self.action_class.current_action.pop()._cleanup()
            while self.action_class.undo_stack:
                self.action_class.undo_stack.pop()._undo()
        print type, value, traceback
        self.action_class.context_stack.pop()
        if not self.action_class.context_stack:
            self.action_class.clear()

# Flask-based subclasses

from flask import request, Flask
from weakref import WeakKeyDictionary

class FlaskStack(Stack):

    def __init__(self):
        self._data = WeakKeyDictionary()

    @property
    def request(self):
        try:
            return request._get_current_object()
        except RuntimeError:
            return Flask

    @property
    def data(self):
        if self.request not in self._data:
            self._data[self.request] = []
        return self._data[self.request]

    @data.setter
    def data(self, value):
        self._data[self.request] = value

class FlaskContextKeyedStack(FlaskStack, ContextKeyedStack):

    def __init__(self, context):
        self._context = context
        self._data = WeakKeyDictionary()

    @property
    def data(self):
        if self.request not in self._data:
            self._data[self.request] = {}
        if self.context not in self._data[self.request]:
            self._data[self.request][self.context] = []
        return self._data[self.request][self.context]

    @data.setter
    def data(self, value):
        self._data[self.request][self.context] = value

    @data.setter
    def data(self, value):
        self._data[self.request][self.context] = value

class FlaskAction(Action):

    pass

FlaskAction.context_stack = FlaskStack()

FlaskAction.undo_stack = FlaskContextKeyedStack(FlaskAction.context_stack)
FlaskAction.redo_stack = FlaskContextKeyedStack(FlaskAction.context_stack)
FlaskAction.current_action = FlaskContextKeyedStack(FlaskAction.context_stack)

class FlaskActionContext(ActionContext):

    action_class = FlaskAction
