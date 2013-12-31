from framework.actions import FlaskAction as Action
from modularodm import exceptions
from website import settings

from .node import add_child_component_action
from .log import add_log_action
from .git import clone_repo_action

import datetime

class add_to_fork_list_action(Action):

    def __init__(self, original, forked):
        self.__dict__.update(locals())

    def redo(self):
        self.original.fork_list.append(self.forked._primary_key)
        self.original.save()

    def undo(self):
        self.original.fork_list.remove(self.forked._primary_key)
        self.original.save()

    def cleanup(self):
        try:
            self.undo()
        except ValueError:
            pass

class fork_component_action(Action):

    def __init__(self, original, user, title):
        self.original = original
        self.user = user
        self.title = title

    def redo(self):

        when = datetime.datetime.utcnow()

        self.forked = self.original.clone()

        self.forked.nodes = []
        self.forked.contributors = []
        self.forked.contributor_list = []
        self.forked.title = self.title + self.forked.title
        self.forked.is_fork = True
        self.forked.forked_date = when
        self.forked.forked_from = self.original
        self.forked.is_public = False

        # Recursively fork children
        for child in self.original.nodes:

            # Fork child
            forked_child = fork_component_action(
                child, self.user, title=''
            ).call()

            # Add to forked parent
            add_child_component_action(
                self.forked, forked_child
            ).call()

        # might not work
        self.forked.add_contributor(self.user, log=False, save=False)

        # Add log to forked component
        add_log_action(
            self.forked,
            log=None,
            action='node_forked',
            params={
                'project' : self.original.node__parent[0]._primary_key if self.original.node__parent else None,
                'node' : self.original._primary_key,
                'registration' : self.forked._primary_key,
            },
            user=self.user,
            log_date=when,
        ).call()

        # Copy git repo
        clone_repo_action(
            settings.uploads_path, self.original, self.forked
        ).call()

        # Add forked component to forks list of original
        add_to_fork_list_action(
            self.original, self.forked
        ).call()

        self.forked.save()

        return self.forked

    def undo(self):
        self.forked.remove_one(self.forked)

    def cleanup(self):
        try:
            self.undo()
        except AttributeError:
            pass
        except exceptions.NoResultsFound:
            pass
