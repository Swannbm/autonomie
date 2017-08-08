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
    Invoice views
"""
import logging
import datetime

from pyramid.httpexceptions import HTTPFound
from colanderalchemy import SQLAlchemySchemaNode

from autonomie.models.task import (
    Invoice,
)
from autonomie_base.utils.date import format_date
from autonomie.utils.strings import format_amount

from autonomie.utils.widgets import ViewLink
from autonomie.forms.tasks.invoice import (
    get_payment_schema,
)
from autonomie.views import (
    BaseEditView,
    BaseFormView,
    submit_btn,
    cancel_btn,
)
from autonomie.views.files import FileUploadView
from autonomie.views.sage import SageSingleInvoiceExportPage

from autonomie.views.task.views import (
    TaskAddView,
    TaskEditView,
    TaskDeleteView,
    TaskHtmlView,
    TaskPdfView,
    TaskDuplicateView,
    TaskMetadatasEditView,
    TaskSetProductsView,
)


logger = log = logging.getLogger(__name__)


class InvoiceAddView(TaskAddView):
    """
    Invoice add view
    context is a project
    """
    title = "Nouvelle facture"
    factory = Invoice

    def _more_init_attributes(self, invoice, appstruct):
        """
        Add Invoice's specific attribute while adding this task
        """
        invoice.course = appstruct['course']
        invoice.financial_year = datetime.date.today().year
        invoice.prefix = self.request.config.get('invoiceprefix', '')
        return invoice

    def _after_flush(self, invoice):
        """
        Launch after the new invoice has been flushed
        """
        logger.debug(
            "  + Invoice successfully added : {0}".format(invoice.id)
        )


class InvoiceEditView(TaskEditView):

    def title(self):
        return u"Modification de la facture {task.name}".format(
            task=self.context
        )


class InvoiceDeleteView(TaskDeleteView):
    msg = u"La facture {context.name} a bien été supprimé."

    def pre_delete(self):
        """
        If an estimation is attached to this invoice, ensure geninv is set to
        False
        """
        if self.context.estimation is not None:
            if len(self.context.estimation.invoices) == 1:
                self.context.estimation.geninv = False
                self.request.dbsession.merge(self.context.estimation)


class InvoiceHtmlView(TaskHtmlView):
    label = u"Facture"


class InvoiceDuplicateView(TaskDuplicateView):
    label = u"la facture"


class InvoicePdfView(TaskPdfView):
    pass


def gencinv_view(context, request):
    """
    Cancelinvoice generation view
    """
    try:
        cancelinvoice = context.gen_cancelinvoice(request.user)
        request.dbsession.add(cancelinvoice)
        request.dbsession.flush()
    except:
        logger.exception(
            u"Error while generating a cancelinvoice for {0}".format(
                context.id
            )
        )
        request.session.flash(
            u"Erreur à la génération de votre avoir, "
            u"contactez votre administrateur",
            'error'
        )
        return HTTPFound(request.route_path("/invoices/{id}", id=context.id))
    return HTTPFound(
        request.route_path("/cancelinvoices/{id}", id=cancelinvoice.id)
    )


class InvoiceSetTreasuryiew(BaseEditView):
    """
    View used to set treasury related informations

    context

        An invoice

    perms

        set_treasury.invoice
    """
    factory = Invoice
    schema = SQLAlchemySchemaNode(
        Invoice,
        includes=('prefix', 'financial_year',),
        title=u"Modifier l'année fiscale de référence et le préfixe "
        u"du numéro de facture",
    )

    def redirect(self):
        return HTTPFound(
            self.request.route_path(
                "/invoices/{id}.html",
                id=self.context.id,
                _anchor="treasury"
            )
        )

    def before(self, form):
        BaseEditView.before(self, form)
        self.request.actionmenu.add(
            ViewLink(
                label=u"Revenir à la facture",
                path="/invoices/{id}.html",
                id=self.context.id,
                _anchor="treasury",
            )
        )

    @property
    def title(self):
        return u"Facture numéro {0} en date du {1}".format(
            self.context.official_number,
            format_date(self.context.date),
        )


class InvoiceMetadatasSetView(TaskMetadatasEditView):
    """
    View used for editing invoice metadatas
    """

    @property
    def title(self):
        return u"Modification de la facture {task.name}".format(
            task=self.context
        )


class InvoiceSetProductsView(TaskSetProductsView):
    @property
    def title(self):
        return (
            u"Configuration des codes produits pour la facture {0.name}".format(
                self.context
            )
        )


class InvoicePaymentView(BaseFormView):
    buttons = (submit_btn, cancel_btn)
    add_template_vars = ('help_message',)

    @property
    def help_message(self):
        return (
            u"Enregistrer un paiement pour la facture {0} dont le montant "
            u"ttc restant à payer est de {1} €".format(
                self.context.official_number,
                format_amount(self.context.topay(), precision=5)
            )
        )

    @property
    def schema(self):
        return get_payment_schema(self.request).bind(request=self.request)

    @schema.setter
    def schema(self, value):
        """
        A setter for the schema property
        The BaseClass in pyramid_deform gets and sets the schema attribute that
        is here transformed as a property
        """
        self._schema = value

    @property
    def title(self):
        return (
            u"Enregistrer un encaissement pour la facture "
            u"{0.official_number}".format(self.context)
        )

    def before(self, form):
        BaseFormView.before(self, form)
        self.request.actionmenu.add(
            ViewLink(
                label=u"Revenir à la facture",
                path="/invoices/{id}.html",
                id=self.context.id,
                _anchor="payment",
            )
        )

    def submit_success(self, appstruct):
        self.context.record_payment(user=self.request.user, **appstruct)
        self.request.dbsession.merge(self.context)
        return HTTPFound(
            self.request.route_path(
                '/invoices/{id}.html',
                id=self.context.id,
                _anchor='payment',
            )
        )

    def cancel_success(self, appstruct):
        return HTTPFound(
            self.request.route_path(
                '/invoices/{id}.html',
                id=self.context.id,
                _anchor='payment',
            )
        )
    cancel_failure = cancel_success


class InvoiceAdminView(BaseEditView):
    """
    Vue pour l'administration de factures /invoices/id/admin

    Vue accessible aux utilisateurs admin
    """
    factory = Invoice
    schema = SQLAlchemySchemaNode(
        Invoice,
        title=u"Formulaire d'édition forcée de devis/factures/avoirs",
        help_msg=u"Les montants sont *10^5   10 000==1€",
    )


def add_routes(config):
    """
    add module related routes
    """
    config.add_route(
        'project_invoices',
        '/projects/{id:\d+}/invoices',
        traverse='/projects/{id}'
    )

    config.add_route(
        '/invoices/{id}',
        '/invoices/{id:\d+}',
        traverse='/invoices/{id}',
    )
    for extension in ('html', 'pdf', 'txt'):
        config.add_route(
            '/invoices/{id}.%s' % extension,
            '/invoices/{id:\d+}.%s' % extension,
            traverse='/invoices/{id}'
        )
    for action in (
        'addfile',
        'delete',
        'duplicate',
        'admin',
        'set_treasury',
        'set_products',
        'addpayment',
        'gencinv',
        'set_metadatas',
    ):
        config.add_route(
            '/invoices/{id}/%s' % action,
            '/invoices/{id:\d+}/%s' % action,
            traverse='/invoices/{id}'
        )


def includeme(config):
    add_routes(config)

    config.add_view(
        InvoiceAddView,
        route_name="project_invoices",
        renderer='tasks/add.mako',
        permission='add_invoice',
    )

    config.add_view(
        InvoiceEditView,
        route_name='/invoices/{id}',
        renderer='tasks/form.mako',
        permission='view.invoice',
        layout='opa',
    )

    config.add_view(
        InvoiceDeleteView,
        route_name='/invoices/{id}/delete',
        permission='delete.invoice',
    )

    config.add_view(
        InvoiceAdminView,
        route_name='/invoices/{id}/admin',
        renderer="base/formpage.mako",
        permission="admin",
    )

    config.add_view(
        InvoiceDuplicateView,
        route_name="/invoices/{id}/duplicate",
        permission="view.invoice",
        renderer='base/formpage.mako',
    )

    config.add_view(
        InvoiceHtmlView,
        route_name='/invoices/{id}.html',
        renderer='tasks/invoice_view_only.mako',
        permission='view.invoice',
    )

    config.add_view(
        InvoicePdfView,
        route_name='/invoices/{id}.pdf',
        permission='view.invoice',
    )

    config.add_view(
        FileUploadView,
        route_name="/invoices/{id}/addfile",
        renderer='base/formpage.mako',
        permission='add.file',
    )

    config.add_view(
        gencinv_view,
        route_name="/invoices/{id}/gencinv",
        permission="gencinv.invoice",
    )

    config.add_view(
        SageSingleInvoiceExportPage,
        route_name="/invoices/{id}.txt",
        renderer='/treasury/sage_single_export.mako',
        permission='admin_treasury'
    )
    config.add_view(
        InvoicePaymentView,
        route_name="/invoices/{id}/addpayment",
        permission="add_payment.invoice",
        renderer='base/formpage.mako',
    )
    config.add_view(
        InvoiceSetTreasuryiew,
        route_name="/invoices/{id}/set_treasury",
        permission="set_treasury.invoice",
        renderer='base/formpage.mako',
    )
    config.add_view(
        InvoiceMetadatasSetView,
        route_name="/invoices/{id}/set_metadatas",
        permission="view.invoice",
        renderer='tasks/add.mako',
    )
    config.add_view(
        InvoiceSetProductsView,
        route_name="/invoices/{id}/set_products",
        permission="admin_treasury",
        renderer='base/formpage.mako',
    )
