from framework.actions import FlaskAction as Action
from modularodm import exceptions

from .analytics import increment_user_activity_counter_action

class create_log_action(Action):

    def __init__(self, action, params, user, log_date=None):
        self.__dict__.update(locals())

    def redo(self):
        from website.project.model import NodeLog
        self.log = NodeLog(
            action=self.action,
            params=self.params,
            user=self.user,
            log_date=self.log_date,
        )
        self.log.save()
        return self.log

    def undo(self):
        from website.project.model import NodeLog
        NodeLog.remove_one(self.log)

    def cleanup(self):
        if hasattr(self, 'log'):
            try:
                NodeLog.remove_one(self.log)
            except exceptions.NoResultsFound:
                pass

class add_log_action(Action):

    def __init__(self, component, log, action=None, params=None, user=None, log_date=None):
        self.__dict__.update(locals())

    def redo(self):

        if self.log is None:
            self.log = create_log_action(
                self.action,
                self.params,
                self.user,
                self.log_date,
            ).call()

            # def __init__(self, action, params, user, log_date=None):
            print 'created log', self.log

        self.component.logs.append(self.log)
        self.component.save()

        increment_user_activity_counter_action(
            self.user._primary_key,
            self.action,
            self.log.date
        ).call()

        if self.component.node__parent:
            parent = self.component.node__parent[0]
            add_log_action(
                parent,
                log=self.log,
                user=self.user,
            ).call()

    def undo(self):
        self.component.logs.remove(self.log)
        self.component.save()

    def cleanup(self):
        if hasattr(self, 'log') and self.log in self.component.logs:
            self.component.logs.remove(self.log)
            self.component.save()