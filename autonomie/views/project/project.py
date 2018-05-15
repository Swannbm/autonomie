# -*- coding: utf-8 -*-
# * Copyright (C) 2012-2013 Croissance Commune
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * Pettier Gabriel;
#       * TJEBBES Gaston <g.t@majerti.fr>
#
# This file is part of Autonomie : Progiciel de gestion de CAE.
#
#    Autonomie is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Autonomie is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Autonomie.  If not, see <http://www.gnu.org/licenses/>.
#

"""
    Project views
    Context could be either company:
        add and list view
    or project :
        simple view, add_phase, edit, ...
"""
import logging
import colander
from sqlalchemy import (
    or_,
    distinct,
)
from deform import Form

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

from autonomie_base.models.base import DBSESSION
from autonomie.models.project import (
    Project,
    Phase,
)
from autonomie.models.customer import Customer
from autonomie.utils.colors import COLORS_SET
from autonomie.forms.project import (
    get_list_schema,
    get_add_project_schema,
    get_add_step2_project_schema,
    get_edit_project_schema,
    PhaseSchema,
)
from autonomie.views import (
    BaseView,
    BaseAddView,
    BaseEditView,
    submit_btn,
    BaseListView,
    TreeMixin,
)
from autonomie.views.files import (
    FileUploadView,
)
from autonomie.views.project.routes import (
    COMPANY_PROJECTS_ROUTE,
    PROJECT_ITEM_ROUTE,
    PROJECT_ITEM_GENERAL_ROUTE,
    PROJECT_ITEM_PHASE_ROUTE,
    PROJECT_ITEM_ESTIMATION_ROUTE,
    PROJECT_ITEM_INVOICE_ROUTE,
)

log = logger = logging.getLogger(__name__)
ADD_FORM_GRID = (
    (
        ('name', 12),
    ),
    (
        ('project_type_id', 12),
    ),
    (
        ('customers', 12),
    ),
)
FORM_GRID = (
    (
        ('name', 6),
    ),
    (
        ('description', 4),
        ('', 2),
        ('code', 2),
    ),
    (
        ('customers', 8),
    ),
    (
        ('starting_date', 4),
        ('ending_date', 4),
    ),
    (
        ('definition', 10),
    )
)


def redirect_to_customerslist(request, company):
    """
        Force project page to be redirected to customer page
    """
    request.session.flash(u"Vous avez été redirigé vers la liste \
des clients")
    request.session.flash(u"Vous devez créer des clients afin \
de créer de nouveaux projets")
    raise HTTPFound(
        request.route_path("company_customers", id=company.id)
    )


class ProjectListView(BaseListView, TreeMixin):
    """
    The project list view is compound of :
        * the list of projects with action buttons (view, delete ...)
        * an action menu with:
            * links
            * an add projectform popup
            * a searchform
    """
    add_template_vars = ('title', 'stream_actions', 'add_url')
    title = u"Liste des projets"
    schema = get_list_schema()
    default_sort = "created_at"
    default_direction = "desc"
    sort_columns = {
        'name': Project.name,
        "code": Project.code,
        "created_at": Project.created_at,
    }
    route_name = COMPANY_PROJECTS_ROUTE
    item_route_name = PROJECT_ITEM_ROUTE

    @property
    def url(self):
        if isinstance(self.context, Project):
            cid = self.context.company_id
        else:
            cid = self.context.id
        return self.request.route_path(self.route_name, id=cid)

    def query(self):
        company = self.request.context
        # We can't have projects without having customers
        if not company.customers:
            redirect_to_customerslist(self.request, company)
        main_query = DBSESSION().query(distinct(Project.id), Project)
        main_query = main_query.outerjoin(Project.customers)
        return main_query.filter(Project.company_id == company.id)

    def filter_archived(self, query, appstruct):
        archived = appstruct.get('archived', False)
        if archived in (False, colander.null):
            query = query.filter(Project.archived == False)
        return query

    def filter_name_or_customer(self, query, appstruct):
        search = appstruct['search']
        if search:
            query = query.filter(
                or_(
                    Project.name.like("%" + search + "%"),
                    Project.customers.any(
                        Customer.name.like("%" + search + "%")
                    )
                )
            )
        return query

    def stream_actions(self, project):
        """
        Stream actions available for the given project

        :param obj project: A Project instance
        :rtype: generator
        """
        yield (
            self._get_item_url(project),
            u"Voir/Modifier",
            u"Voir/Modifier",
            u"pencil",
            {}
        )
        if self.request.has_permission('add_estimation', project):
            yield (
                self.request.route_path(
                    PROJECT_ITEM_ESTIMATION_ROUTE,
                    id=project.id,
                    _query={'action': 'add'},
                ),
                u"Nouveau devis",
                u"Créer un devis",
                u"file",
                {}
            )
        if self.request.has_permission('add_invoice', project):
            yield (
                self.request.route_path(
                    PROJECT_ITEM_INVOICE_ROUTE,
                    id=project.id,
                    _query={'action': 'add'},
                ),
                u"Nouvelle facture",
                u"Créer une facture",
                u"file",
                {}
            )
        if self.request.has_permission('edit_project', project):
            if project.archived:
                yield (
                    self._get_item_url(project, action='archive'),
                    u"Désarchiver le projet",
                    u"Désarchiver le projet",
                    u"book",
                    {}
                )
            else:
                yield (
                    self._get_item_url(project, action='archive'),
                    u"Archiver le projet",
                    u"Archiver le projet",
                    u"book",
                    {}
                )
        if self.request.has_permission('delete_project', project):
            yield (
                self._get_item_url(project, action='delete'),
                u"Supprimer",
                u"Supprimer ce projet",
                u"trash",
                {
                    "onclick": (
                        u"return confirm('Êtes-vous sûr de "
                        "vouloir supprimer ce projet ?')"
                    )
                }
            )

    @property
    def add_url(self):
        return self.request.route_path(
            COMPANY_PROJECTS_ROUTE,
            id=self.context.id,
            _query={'action': 'add'}
        )


class ProjectView(BaseView, TreeMixin):
    route_name = PROJECT_ITEM_ROUTE

    @property
    def url(self):
        return self.request.route_path(self.route_name, id=self.context.id)

    @property
    def title(self):
        return u"Projet : {0}".format(self.context.name)

    def __call__(self):
        self.populate_navigation()
        return dict()


class ProjectByPhaseView(BaseView, TreeMixin):
    route_name = PROJECT_ITEM_PHASE_ROUTE

    @property
    def url(self):
        return self.request.route_path(self.route_name, id=self.context.id)

    @property
    def title(self):
        return u"Projet : {0}".format(self.context.name)

    def _get_phase_add_form(self):
        """
        Return a form object for phase add
        :param obj request: The pyramid request object
        :returns: A form
        :rtype: class:`deform.Form`
        """
        schema = PhaseSchema().bind(request=self.request)
        form = Form(
            schema,
            buttons=(submit_btn,),
            action=self.request.route_path(
                PROJECT_ITEM_ROUTE,
                id=self.context.id,
                _query={'action': 'addphase'}
            ),
        )
        return form

    def _get_latest_phase(self, phases):
        """
        Return the phase where we can identify the last modification
        :param list phases: The list of phases of the given project
        """
        result = 0
        if 'phase' in self.request.GET:
            result = Phase.get(self.request.GET['phase'])

        else:
            # We get the latest used task and so we get the latest used phase
            all_tasks = []
            for phase in phases:
                all_tasks.extend(phase.tasks)
            all_tasks.sort(key=lambda task: task.status_date, reverse=True)

            if all_tasks:
                result = all_tasks[0].phase
        return result

    def _get_color(self, index):
        """
        return the color for the given index (uses modulo to avoid index errors
        """
        return COLORS_SET[index % len(COLORS_SET)]

    def _set_task_colors(self, phases):
        """
        Set colors on the estimation/invoice/cancelinvoice objects so that we
        can visually identify related objects

        :param list phases: The list of phases of this project
        """
        index = 0

        for phase in phases:
            for estimation in phase.estimations:
                estimation.color = self._get_color(index)
                index += 1

        for phase in phases:
            for invoice in phase.invoices:
                if invoice.estimation and hasattr(invoice.estimation, 'color'):
                    invoice.color = invoice.estimation.color
                else:
                    invoice.color = self._get_color(index)
                    index += 1

        for phase in phases:
            for cancelinvoice in phase.cancelinvoices:
                if cancelinvoice.invoice and \
                        hasattr(cancelinvoice.invoice, 'color'):
                    cancelinvoice.color = cancelinvoice.invoice.color
                else:
                    cancelinvoice.color = self._get_color(index)
                    index += 1

    def __call__(self):
        self.populate_navigation()
        phases = self.context.phases
        self._set_task_colors(phases)
        return dict(
            project=self.context,
            latest_phase=self._get_latest_phase(phases),
            phase_form=self._get_phase_add_form(),
            estimation_add_route=PROJECT_ITEM_ESTIMATION_ROUTE,
            invoice_add_route=PROJECT_ITEM_INVOICE_ROUTE,
        )


class ProjectGeneralView(BaseView, TreeMixin):
    route_name = PROJECT_ITEM_GENERAL_ROUTE

    @property
    def url(self):
        return self.request.route_path(self.route_name, id=self.context.id)

    @property
    def title(self):
        return u"Projet : {0}".format(self.context.name)

    def __call__(self):
        """
            Return datas for displaying one project
        """
        self.populate_navigation()

        return dict(
            title=self.title,
            project=self.context,
            company=self.context.company,
        )


class ProjectAddView(BaseAddView, TreeMixin):
    title = u"Ajout d'un nouveau projet"
    schema = get_add_project_schema()
    msg = u"Le projet a été ajouté avec succès"
    named_form_grid = ADD_FORM_GRID
    factory = Project
    route_name = COMPANY_PROJECTS_ROUTE

    def before(self, form):
        BaseAddView.before(self, form)
        self.populate_navigation()
        # If there's no customer, redirect to customer view
        if len(self.request.context.customers) == 0:
            redirect_to_customerslist(self.request, self.request.context)

    def redirect(self, new_model):
        return HTTPFound(
            self.request.route_path(
                PROJECT_ITEM_ROUTE,
                id=new_model.id,
                _query={'action': 'addstep2'},
            )
        )

    def on_add(self, new_model, appstruct):
        """
        On add, set the project's company
        """
        new_model.company = self.context


class ProjectAddStep2View(BaseEditView, TreeMixin):
    named_form_grid = FORM_GRID
    add_template_vars = ('title', 'project_codes')
    schema = get_add_step2_project_schema()
    route_name = PROJECT_ITEM_ROUTE

    @property
    def project_codes(self):
        return Project.get_code_list_with_labels(self.context.company_id)

    @reify
    def title(self):
        return u"Création du projet : {0}, étape 2".format(self.context.name)

    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                PROJECT_ITEM_ROUTE,
                id=self.context.id,
            )
        )


class ProjectEditView(BaseEditView, TreeMixin):
    add_template_vars = ('project', 'project_codes',)
    named_form_grid = FORM_GRID
    schema = get_edit_project_schema()
    route_name = PROJECT_ITEM_ROUTE

    def before(self, form):
        BaseEditView.before(self, form)
        self.populate_navigation()

    @property
    def title(self):
        return u"Modification du projet : {0}".format(self.request.context.name)

    @property
    def project(self):
        return self.context

    @property
    def project_codes(self):
        return Project.get_code_list_with_labels(self.context.company_id)

    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                PROJECT_ITEM_GENERAL_ROUTE,
                id=self.context.id
            )
        )


def project_archive(request):
    """
    Archive the current project
    """
    project = request.context
    if not project.archived:
        project.archived = True
    else:
        project.archived = False
        request.session.flash(
            u"Le projet '{0}' a été désarchivé".format(project.name)
        )
    request.dbsession.merge(project)
    if request.referer is not None:
        return HTTPFound(request.referer)
    else:
        return HTTPFound(
            request.route_path(
                COMPANY_PROJECTS_ROUTE,
                id=request.context.company_id
            )
        )


def project_delete(request):
    """
        Delete the current project
    """
    project = request.context
    cid = project.company_id
    log.info(u"Project {0} deleted".format(project))
    request.dbsession.delete(project)
    request.session.flash(
        u"Le projet '{0}' a bien été supprimé".format(project.name)
    )
    if request.referer is not None:
        return HTTPFound(request.referer)
    else:
        return HTTPFound(
            request.route_path(COMPANY_PROJECTS_ROUTE, id=cid)
        )


def includeme(config):
    config.add_tree_view(
        ProjectListView,
        renderer='project/list.mako',
        request_method='GET',
        permission='list_projects',
    )
    config.add_tree_view(
        ProjectView,
        parent=ProjectListView,
        renderer='project/base.mako',
        permission='view_project',
        layout='project',
    )
    config.add_tree_view(
        ProjectByPhaseView,
        parent=ProjectListView,
        renderer='project/phases.mako',
        permission='view_project',
        layout='project',
    )
    config.add_tree_view(
        ProjectGeneralView,
        parent=ProjectListView,
        renderer='project/general.mako',
        permission='view_project',
        layout='project',
    )
    config.add_tree_view(
        ProjectAddView,
        parent=ProjectListView,
        renderer='autonomie:templates/base/formpage.mako',
        request_param='action=add',
        permission='add_project',
        layout='default',
    )
    config.add_tree_view(
        ProjectAddStep2View,
        parent=ProjectListView,
        renderer='project/edit.mako',
        request_param='action=addstep2',
        permission='edit_project',
        layout='default',
    )
    config.add_tree_view(
        ProjectEditView,
        parent=ProjectGeneralView,
        renderer='project/edit.mako',
        request_param='action=edit',
        permission='edit_project',
        layout='project',
    )
    config.add_view(
        project_delete,
        route_name=PROJECT_ITEM_ROUTE,
        request_param="action=delete",
        permission='edit_project',
    )
    config.add_view(
        project_archive,
        route_name=PROJECT_ITEM_ROUTE,
        request_param="action=archive",
        permission='edit_project',
    )
    config.add_view(
        FileUploadView,
        route_name=PROJECT_ITEM_ROUTE,
        renderer='base/formpage.mako',
        permission='edit_project',
        request_param='action=attach_file',
    )
