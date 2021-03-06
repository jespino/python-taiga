import datetime
from .base import InstanceResource, ListResource


class CustomAttributeResource(InstanceResource):

    def set_attribute(self, id, value, version=1):
        attributes = self.get_attributes()
        formatted_id = '{0}'.format(id)
        attributes['attributes_values'][formatted_id] = value
        response = self.requester.patch(
            '/{endpoint}/custom-attributes-values/{id}',
            endpoint=self.endpoint, id=self.id,
            payload={
                'attributes_values': attributes['attributes_values'],
                'version': version
            }
        )
        return response.json()

    def get_attributes(self):
        response = self.requester.get(
            '/{endpoint}/custom-attributes-values/{id}',
            endpoint=self.endpoint, id=self.id,
        )
        return response.json()


class CustomAttribute(InstanceResource):

    repr_attribute = 'name'

    allowed_params = [
        'name', 'description', 'order', 'project'
    ]


class CustomAttributes(ListResource):

    def create(self, project, name, **attrs):
        attrs.update(
            {
                'project': project, 'name': name
            }
        )
        return self._new_resource(payload=attrs)


class User(InstanceResource):

    endpoint = 'users'

    repr_attribute = 'full_name'

    def starred_projects(self):
        response = self.requester.get(
            '/{endpoint}/{id}/starred', endpoint=self.endpoint,
            id=self.id
        )
        return Projects.parse(self.requester, response.json())


class Users(ListResource):

    instance = User


class Membership(InstanceResource):

    endpoint = 'memberships'

    allowed_params = ['email', 'role', 'project']

    repr_attribute = 'email'


class Memberships(ListResource):

    instance = Membership

    def create(self, project, email, role, **attrs):
        attrs.update({'project': project, 'email': email, 'role': role})
        return self._new_resource(payload=attrs)


class Priority(InstanceResource):

    endpoint = 'priorities'

    allowed_params = ['name', 'color', 'order', 'project']

    repr_attribute = 'name'


class Priorities(ListResource):

    instance = Priority

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class Attachment(InstanceResource):

    repr_attribute = 'subject'

    allowed_params = [
        'object_id', 'project', 'attached_file',
        'description', 'is_deprecated'
    ]


class Attachments(ListResource):

    def create(self, project, object_id, attached_file, **attrs):
        attrs.update({'project': project, 'object_id': object_id})
        return self._new_resource(
            files={'attached_file': open(attached_file, 'rb')},
            payload=attrs
        )


class UserStoryAttachment(Attachment):

    endpoint = 'userstories/attachments'


class UserStoryAttachments(Attachments):

    instance = UserStoryAttachment


class UserStory(CustomAttributeResource):

    endpoint = 'userstories'

    repr_attribute = 'subject'

    allowed_params = [
        'assigned_to', 'backlog_order', 'blocked_note',
        'client_requirement', 'description', 'is_archived', 'is_blocked',
        'is_closed', 'kanban_order', 'milestone', 'points', 'project',
        'sprint_order', 'status', 'subject', 'tags', 'team_requirement',
        'watchers', 'version'
    ]

    def add_task(self, subject, status, **attrs):
        return Tasks(self.requester).create(
            self.project, subject, status,
            user_story=self.id, **attrs
        )

    def list_tasks(self):
        return Tasks(self.requester).list(user_story=self.id)

    def attach(self, attached_file, **attrs):
        return UserStoryAttachments(self.requester).create(
            self.project, self.id,
            attached_file, **attrs
        )


class UserStories(ListResource):

    instance = UserStory

    def create(self, project, subject, **attrs):
        attrs.update({'project': project, 'subject': subject})
        return self._new_resource(payload=attrs)

    def import_(self, project, subject, status, **attrs):
        attrs.update(
            {
                'project': project,
                'subject': subject,
                'status': status
            }
        )
        response = self.requester.post('/{endpoint}/{id}/{type}',
                                       endpoint="importer", id=project,
                                       type="us", payload=attrs)
        return self.instance.parse(self.requester, response.json())


class UserStoryStatus(InstanceResource):

    repr_attribute = 'subject'

    endpoint = 'userstory-statuses'

    allowed_params = [
        'color', 'is_closed', 'name', 'order', 'project', 'wip_limit'
    ]


class UserStoryStatuses(ListResource):

    instance = UserStoryStatus

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class Point(InstanceResource):

    endpoint = 'points'

    repr_attribute = 'subject'

    allowed_params = ['color', 'value', 'name', 'order', 'project']


class Points(ListResource):

    instance = Point

    def create(self, project, name, value, **attrs):
        attrs.update({'project': project, 'name': name, 'value': value})
        return self._new_resource(payload=attrs)


class Milestone(InstanceResource):

    endpoint = 'milestones'

    allowed_params = [
        'name', 'project', 'estimated_start', 'estimated_finish',
        'disponibility', 'slug', 'order', 'watchers'
    ]

    parser = {
        'user_stories': UserStories,
    }

    def stats(self):
        response = self.requester.get(
            '/{endpoint}/{id}/stats',
            endpoint=self.endpoint, id=self.id
        )
        return response.json()


class Milestones(ListResource):

    instance = Milestone

    def create(self, project, name, estimated_start,
               estimated_finish, **attrs):
        if isinstance(estimated_start, datetime.datetime):
            estimated_start = estimated_start.strftime('%Y-%m-%d')
        if isinstance(estimated_finish, datetime.datetime):
            estimated_finish = estimated_finish.strftime('%Y-%m-%d')
        attrs.update({
            'project': project,
            'name': name,
            'estimated_start': estimated_start,
            'estimated_finish': estimated_finish
        })
        return self._new_resource(payload=attrs)

    def import_(self, project, name, estimated_start,
                estimated_finish, **attrs):
        if isinstance(estimated_start, datetime.datetime):
            estimated_start = estimated_start.strftime('%Y-%m-%d')
        if isinstance(estimated_finish, datetime.datetime):
            estimated_finish = estimated_finish.strftime('%Y-%m-%d')
        attrs.update({
            'project': project,
            'name': name,
            'estimated_start': estimated_start,
            'estimated_finish': estimated_finish
        })
        response = self.requester.post('/{endpoint}/{id}/{type}',
                                       endpoint="importer", id=project,
                                       type="milestone", payload=attrs)
        return self.instance.parse(self.requester, response.json())


class TaskStatus(InstanceResource):

    endpoint = 'task-statuses'

    allowed_params = ['name', 'color', 'order', 'project', 'is_closed']


class TaskStatuses(ListResource):

    instance = TaskStatus

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class TaskAttachment(Attachment):

    endpoint = 'tasks/attachments'


class TaskAttachments(Attachments):

    instance = TaskAttachment


class Task(CustomAttributeResource):

    endpoint = 'tasks'

    repr_attribute = 'subject'

    allowed_params = [
        'assigned_to', 'blocked_note', 'description',
        'is_blocked', 'is_closed', 'milestone', 'project', 'user_story',
        'status', 'subject', 'tags', 'us_order', 'taskboard_order',
        'is_iocaine', 'external_reference', 'watchers', 'version'
    ]

    def attach(self, attached_file, **attrs):
        return TaskAttachments(self.requester).create(
            self.project, self.id,
            attached_file, **attrs
        )


class Tasks(ListResource):

    instance = Task

    def create(self, project, subject, status, **attrs):
        attrs.update(
            {
                'project': project, 'subject': subject,
                'status': status
            }
        )
        return self._new_resource(payload=attrs)

    def import_(self, project, subject, status, **attrs):
        attrs.update(
            {
                'project': project,
                'subject': subject,
                'status': status
            }
        )
        response = self.requester.post('/{endpoint}/{id}/{type}',
                                       endpoint="importer", id=project,
                                       type="task", payload=attrs)
        return self.instance.parse(self.requester, response.json())


class IssueType(InstanceResource):

    endpoint = 'issue-types'

    allowed_params = ['name', 'color', 'order', 'project']


class IssueTypes(ListResource):

    instance = IssueType

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class IssueStatus(InstanceResource):

    endpoint = 'issue-statuses'

    allowed_params = ['name', 'color', 'order', 'project', 'is_closed']


class IssueStatuses(ListResource):

    instance = IssueStatus

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class IssueAttachment(Attachment):

    endpoint = 'issues/attachments'


class IssueAttachments(Attachments):

    instance = IssueAttachment


class Issue(CustomAttributeResource):

    endpoint = 'issues'

    repr_attribute = 'subject'

    allowed_params = [
        'assigned_to', 'blocked_note', 'description',
        'is_blocked', 'is_closed', 'milestone', 'project', 'status',
        'severity', 'priority', 'type', 'subject', 'tags', 'watchers'
    ]

    def upvote(self):
        self.requester.post(
            '/{endpoint}/{id}/upvote',
            endpoint=self.endpoint, id=self.id
        )
        return self

    def downvote(self):
        self.requester.post(
            '/{endpoint}/{id}/downvote',
            endpoint=self.endpoint, id=self.id
        )
        return self

    def attach(self, attached_file, **attrs):
        return IssueAttachments(self.requester).create(
            self.project, self.id,
            attached_file, **attrs
        )


class Issues(ListResource):

    instance = Issue

    def create(self, project, subject, priority, status,
               issue_type, severity, **attrs):
        attrs.update(
            {
                'project': project, 'subject': subject,
                'priority': priority, 'status': status,
                'type': issue_type, 'severity': severity
            }
        )
        return self._new_resource(payload=attrs)

    def import_(self, project, subject, priority, status,
                issue_type, severity, **attrs):
        attrs.update(
            {
                'project': project, 'subject': subject,
                'priority': priority, 'status': status,
                'type': issue_type, 'severity': severity
            }
        )
        response = self.requester.post('/{endpoint}/{id}/{type}',
                                       endpoint="importer", id=project,
                                       type="issue", payload=attrs)
        return self.instance.parse(self.requester, response.json())


class IssueAttribute(CustomAttribute):

    endpoint = 'issue-custom-attributes'


class IssueAttributes(CustomAttributes):

    instance = IssueAttribute


class TaskAttribute(CustomAttribute):

    endpoint = 'task-custom-attributes'


class TaskAttributes(CustomAttributes):

    instance = TaskAttribute


class UserStoryAttribute(CustomAttribute):

    endpoint = 'userstory-custom-attributes'


class UserStoryAttributes(CustomAttributes):

    instance = UserStoryAttribute


class Severity(InstanceResource):

    endpoint = 'severities'

    allowed_params = ['name', 'color', 'order', 'project']


class Severities(ListResource):

    instance = Severity

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class Role(InstanceResource):

    endpoint = 'roles'

    allowed_params = ['name', 'slug', 'order', 'computable']


class Roles(ListResource):

    instance = Role

    def create(self, project, name, **attrs):
        attrs.update({'project': project, 'name': name})
        return self._new_resource(payload=attrs)


class Project(InstanceResource):

    endpoint = 'projects'

    allowed_params = [
        'name', 'description', 'creation_template',
        'is_backlog_activated', 'is_issues_activated',
        'is_kanban_activated', 'is_private', 'is_wiki_activated',
        'videoconferences', 'videoconferences_salt', 'total_milestones',
        'total_story_points'
    ]

    parser = {
        'users': Users,
        'priorities': Priorities,
        'issue_statuses': IssueStatuses,
        'issue_types': IssueTypes,
        'task_statuses': TaskStatuses,
        'severities': Severities,
        'roles': Roles,
        'points': Points,
        'us_statuses': UserStoryStatuses
    }

    def stats(self):
        response = self.requester.get(
            '/{endpoint}/{id}/stats',
            endpoint=self.endpoint, id=self.id
        )
        return response.json()

    def star(self):
        self.requester.post(
            '/{endpoint}/{id}/star',
            endpoint=self.endpoint, id=self.id
        )
        return self

    def unstar(self):
        self.requester.post(
            '/{endpoint}/{id}/unstar',
            endpoint=self.endpoint, id=self.id
        )
        return self

    def add_membership(self, email, role, **attrs):
        return Memberships(self.requester).create(
            self.id, email, role, **attrs
        )

    def list_memberships(self):
        return Memberships(self.requester).list(project=self.id)

    def add_user_story(self, subject, **attrs):
        return UserStories(self.requester).create(
            self.id, subject, **attrs
        )

    def import_user_story(self, subject, status, **attrs):
        return UserStories(self.requester).import_(
            self.id, subject, status, **attrs
        )

    def list_user_stories(self):
        return UserStories(self.requester).list(project=self.id)

    def add_issue(self, subject, priority, status,
                  issue_type, severity, **attrs):
        return Issues(self.requester).create(
            self.id, subject, priority, status,
            issue_type, severity, **attrs
        )

    def import_issue(self, subject, priority, status,
                     issue_type, severity, **attrs):
        return Issues(self.requester).import_(
            self.id, subject, priority, status,
            issue_type, severity, **attrs
        )

    def list_issues(self):
        return Issues(self.requester).list(project=self.id)

    def add_milestone(self, name, estimated_start, estimated_finish, **attrs):
        return Milestones(self.requester).create(
            self.id, name, estimated_start,
            estimated_finish, **attrs
        )

    def import_milestone(
            self,
            name,
            estimated_start,
            estimated_finish,
            **attrs):
        return Milestones(self.requester).import_(
            self.id, name, estimated_start,
            estimated_finish, **attrs
        )

    def list_milestones(self):
        return Milestones(self.requester).list(project=self.id)

    def add_point(self, name, value, **attrs):
        return Points(self.requester).create(self.id, name, value, **attrs)

    def list_points(self):
        return Points(self.requester).list(project=self.id)

    def add_task_status(self, name, **attrs):
        return TaskStatuses(self.requester).create(self.id, name, **attrs)

    def list_task_statuses(self):
        return TaskStatuses(self.requester).list(project=self.id)

    def import_task(self, subject, status, **attrs):
        return Tasks(self.requester).import_(
            self.id, subject, status
        )

    def add_user_story_status(self, name, **attrs):
        return UserStoryStatuses(self.requester).create(self.id, name, **attrs)

    def list_user_story_statuses(self):
        return UserStoryStatuses(self.requester).list(project=self.id)

    def add_issue_type(self, name, **attrs):
        return IssueTypes(self.requester).create(self.id, name, **attrs)

    def list_issue_types(self):
        return IssueTypes(self.requester).list(project=self.id)

    def add_severity(self, name, **attrs):
        return Severities(self.requester).create(self.id, name, **attrs)

    def list_severities(self):
        return Severities(self.requester).list(project=self.id)

    def add_role(self, name, **attrs):
        return Roles(self.requester).create(self.id, name, **attrs)

    def list_roles(self):
        return Roles(self.requester).list(project=self.id)

    def add_priority(self, name, **attrs):
        return Priorities(self.requester).create(self.id, name, **attrs)

    def list_priorities(self):
        return Priorities(self.requester).list(project=self.id)

    def add_issue_status(self, name, **attrs):
        return IssueStatuses(self.requester).create(self.id, name, **attrs)

    def list_issue_statuses(self):
        return IssueStatuses(self.requester).list(project=self.id)

    def add_wikipage(self, slug, content, **attrs):
        return WikiPages(self.requester).create(
            self.id, slug, content, **attrs
        )

    def import_wikipage(self, slug, content, **attrs):
        return WikiPages(self.requester).import_(
            self.id, slug, content, **attrs
        )

    def list_wikipages(self):
        return WikiPages(self.requester).list(project=self.id)

    def add_wikilink(self, title, href, **attrs):
        return WikiLinks(self.requester).create(self.id, title, href, **attrs)

    def import_wikilink(self, title, href, **attrs):
        return WikiLinks(self.requester).import_(self.id, title, href, **attrs)

    def list_wikilinks(self):
        return WikiLinks(self.requester).list(project=self.id)

    def add_issue_attribute(self, name, **attrs):
        return IssueAttributes(self.requester).create(
            self.id, name, **attrs
        )

    def list_issue_attributes(self):
        return IssueAttributes(self.requester).list(project=self.id)

    def add_task_attribute(self, name, **attrs):
        return TaskAttributes(self.requester).create(
            self.id, name, **attrs
        )

    def list_task_attributes(self):
        return TaskAttributes(self.requester).list(project=self.id)

    def add_user_story_attribute(self, name, **attrs):
        return UserStoryAttributes(self.requester).create(
            self.id, name, **attrs
        )

    def list_user_story_attributes(self):
        return UserStoryAttributes(self.requester).list(project=self.id)


class Projects(ListResource):

    instance = Project

    def create(self, name, description, **attrs):
        attrs.update({'name': name, 'description': description})
        return self._new_resource(payload=attrs)

    def import_(self, name, description, roles, **attrs):
        attrs.update(
            {
                'name': name,
                'description': description,
                'roles': roles
            }
        )
        response = self.requester.post('/{endpoint}', endpoint="importer",
                                       payload=attrs)
        return self.instance.parse(self.requester, response.json())


class WikiAttachment(Attachment):

    endpoint = 'wiki/attachments'


class WikiAttachments(Attachments):

    instance = WikiAttachment


class WikiPage(InstanceResource):

    endpoint = 'wiki'

    repr_attribute = 'slug'

    allowed_params = ['project', 'slug', 'content', 'watchers']

    def attach(self, attached_file, **attrs):
        return WikiAttachments(self.requester).create(
            self.project, self.id,
            attached_file, **attrs
        )


class WikiPages(ListResource):

    instance = WikiPage

    def create(self, project, slug, content, **attrs):
        attrs.update({'project': project, 'slug': slug, 'content': content})
        return self._new_resource(payload=attrs)

    def import_(self, project, slug, content, **attrs):
        attrs.update({'project': project, 'slug': slug, 'content': content})
        response = self.requester.post('/{endpoint}/{id}/{type}',
                                       endpoint="importer", id=project,
                                       type="wiki_page", payload=attrs)
        return self.instance.parse(self.requester, response.json())


class WikiLink(InstanceResource):

    endpoint = 'wiki-links'

    repr_attribute = 'title'

    allowed_params = ['project', 'title', 'href', 'order']


class WikiLinks(ListResource):

    instance = WikiLink

    def create(self, project, title, href, **attrs):
        attrs.update({'project': project, 'title': title, 'href': href})
        return self._new_resource(payload=attrs)

    def import_(self, project, title, href, **attrs):
        attrs.update({'project': project, 'title': title, 'href': href})
        response = self.requester.post('/{endpoint}/{id}/{type}',
                                       endpoint="importer", id=project,
                                       type="wiki_link", payload=attrs)
        return self.instance.parse(self.requester, response.json())


class History(InstanceResource):

    def __init__(self, *args, **kwargs):
        super(History, self).__init__(*args, **kwargs)
        self.issue = HistoryIssue(self.requester)
        self.task = HistoryTask(self.requester)
        self.user_story = HistoryUserStory(self.requester)
        self.wiki = HistoryWiki(self.requester)


class HistoryEntity(object):

    endpoint = 'history'

    def __init__(self, requester):
        self.requester = requester

    def get(self, resource_id):
        response = self.requester.get(
            '/{endpoint}/{entity}/{id}',
            endpoint=self.endpoint, entity=self.entity, id=resource_id
        )
        return response.json()

    def delete_comment(self, resource_id, ent_id):
        self.requester.post(
            '/{endpoint}/{entity}/{id}/delete_comment?id={ent_id}',
            endpoint=self.endpoint, entity=self.entity,
            id=resource_id, ent_id=ent_id
        )

    def undelete_comment(self, resource_id, ent_id):
        self.requester.post(
            '/{endpoint}/{entity}/{id}/undelete_comment?id={ent_id}',
            endpoint=self.endpoint, entity=self.entity,
            id=resource_id, ent_id=ent_id
        )


class HistoryIssue(HistoryEntity):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.entity = 'issue'


class HistoryTask(HistoryEntity):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.entity = 'task'


class HistoryUserStory(HistoryEntity):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.entity = 'userstory'


class HistoryWiki(HistoryEntity):

    def __init__(self, *args, **kwargs):
        super(type(self), self).__init__(*args, **kwargs)
        self.entity = 'wiki'
