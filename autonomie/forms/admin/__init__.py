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
    Form schemes for administration
"""
import colander
import logging
import simplejson as json
import deform

from colanderalchemy import SQLAlchemySchemaNode
from speaklater import make_lazy_string

from autonomie.models.config import Config
from autonomie.models.competence import (
    CompetenceScale,
)
from autonomie import forms
from autonomie.forms.files import ImageNode
from autonomie.forms.widgets import CleanMappingWidget, CleanSequenceWidget
from autonomie.utils.image import ImageResizer
from autonomie.utils.strings import safe_unicode


log = logging.getLogger(__name__)


HEADER_RESIZER = ImageResizer(4, 1)


def invoice_number_template_validator(node, value):
    from autonomie.models.services.invoice_sequence_number import (
        InvoiceNumberService,
    )
    try:
        InvoiceNumberService.validate_template(value)
    except ValueError as e:
        raise colander.Invalid(node, str(e))


@make_lazy_string
def help_text_libelle_comptable():
    """
    Hack to allow dynamic content in a description field description.
    """
    base = u"Les variables disponibles \
pour la génération des écritures sont décrites en haut de page."
    maxlength = Config.get_value('accounting_label_maxlength', None)
    if maxlength:
        return u"{} NB : les libellés sont tronqués à ".format(base) + \
            u"{} caractères au moment de l'export.".format(maxlength) + \
            u"Il est possible de changer cette taille dans  " +\
            u"Configuration → Logiciel de comptabilité."
    else:
        return base


CONFIGURATION_KEYS = {
    'coop_cgv': {
        "title": u"Conditions générales de vente",
        "description": u"Les conditions générales sont placées en dernière \
page des documents (devis/factures/avoirs)",
        "widget": forms.richtext_widget(admin=True)
    },
    'coop_pdffootertitle': {
        'title': u"Titre du pied de page",
        "widget": deform.widget.TextAreaWidget(rows=4),
    },
    'coop_pdffootertext': {
        'title': u"Contenu du pied de page",
        "widget": deform.widget.TextAreaWidget(rows=4),
    },
    'coop_pdffootercourse': {
        'title': u"Pied de page spécifique aux formations",
        "description": u"Ce contenu ne s'affiche que sur les documents liés à \
des formations",
        "widget": deform.widget.TextAreaWidget(rows=4),
    },
    "coop_estimationheader": {
        "title": u"Cadre d'information spécifique (en entête des devis)",
        "description": u"Permet d'afficher un texte avant la description des \
prestations ex : <font color='red'>Le RIB a changé</font>",
        "widget": deform.widget.TextAreaWidget(rows=4),
    },
    "coop_invoiceheader": {
        "title": u"Cadre d'information spécifique (en entête des factures)",
        "description": u"Permet d'afficher un texte avant la description des \
prestations ex : <font color='red'>Le RIB a changé</font>",
        "widget": deform.widget.TextAreaWidget(rows=4),
    },
    'cae_admin_mail': {
        "title": u"Adresse e-mail de contact pour les notifications Autonomie",
        "description": (
            u"Les e-mails de notifications (par ex : retour "
            u"sur le traitement de fichiers de trésorerie "
            u") sont envoyés à cette adresse"
        )
    },
    'receipts_active_tva_module': {
        "title": u"Activer le module TVA pour les encaissements",
        "description": u"Inclue les écritures pour le paiement de la TVA \
sur encaissement",
        "widget": deform.widget.CheckboxWidget(true_val='1', false_val='0')
    },
    'code_journal': {
        'title': u"Code journal ventes",
        'description': u"Le code du journal dans votre logiciel de \
comptabilité",
    },
    'numero_analytique': {
        'title': u"Numéro analytique de la CAE",
    },
    'compte_cg_contribution': {
        'title': u"Compte CG contribution",
        'description': u"Compte CG correspondant à la contribution des \
entrepreneurs à la CAE",
        "section": u"Module Contribution",
    },
    "compte_frais_annexes": {
        "title": u"Compte de frais annexes",
    },
    "compte_cg_banque": {
        "title": u"Compte banque de l'entrepreneur",
    },
    'compte_rrr': {
        "title": u"Compte RRR",
        "description": u"Compte Rabais, Remises et Ristournes",
        "section": u"Configuration des comptes RRR"
    },
    'compte_cg_tva_rrr': {
        "title": u"Compte CG de TVA spécifique aux RRR",
        "description": u"",
        "section": u"Configuration des comptes RRR"
    },
    'code_tva_rrr': {
        "title": u"Code de TVA spécifique aux RRR",
        "description": u"",
        "section": u"Configuration des comptes RRR"
    },
    'compte_rg_interne': {
        "title": u"Compte CG RG Interne",
        "description": u"",
        "section": u"Module RG Interne",
    },
    'compte_rg_externe': {
        "title": u"Compte CG RG Client",
        "description": u"",
        "section": u"Module RG Client",
    },
    'contribution_cae': {
        "title": u"Pourcentage de la contribution",
        "description": u"Valeur par défaut de la contribution (nombre entre \
0 et 100). Elle peut être individualisée sur les pages entreprises.",
        "section": u"Module Contribution",
    },
    'taux_rg_interne': {
        "title": u"Taux RG Interne",
        "description": u"(nombre entre 0 et 100) Requis pour les écritures \
RG Interne",
        "section": u"Module RG Interne",
    },
    'taux_rg_client': {
        "title": u"Taux RG Client",
        "description": u"(nombre entre 0 et 100) Requis pour le module \
d'écriture RG Client",
        "section": u"Module RG Client",
    },
    'bookentry_facturation_label_template': {
        'title': u"Gabarit pour les libellés d'écriture",
        'description': help_text_libelle_comptable,
        "section": u"Module Facturation",
    },
    'bookentry_payment_label_template': {
        'title': u"Gabarit pour les libellés d'écriture",
        'description': help_text_libelle_comptable,
        "section": u"Encaissements",
    },
    'bookentry_rg_client_label_template': {
        'title': u"Gabarit pour les libellés d'écriture",
        'description': help_text_libelle_comptable,
        "section": u"Module RG Client",
    },
    'bookentry_rg_interne_label_template': {
        'title': u"Gabarit pour les libellés d'écriture",
        'description': help_text_libelle_comptable,
        "section": u"Module RG Interne",
    },
    'bookentry_contribution_label_template': {
        'title': u"Gabarit pour les libellés d'écriture",
        'description': help_text_libelle_comptable,
        "section": u"Module Contribution",
    },
    'bookentry_expense_label_template': {
        'title': u"Gabarit pour les libellés d'écriture",
        'description': help_text_libelle_comptable,
    },
    'bookentry_expense_payment_main_label_template': {
        'title': u"Gabarit pour les libellés d'écriture",
        'description': help_text_libelle_comptable,
        "section": u"Paiement des notes de dépenses",
    },
    'bookentry_expense_payment_waiver_label_template': {
        'title': u"Gabarit pour les libellés d'écriture",
        'description': help_text_libelle_comptable,
        "section": u"Abandon de créance",
    },
    'sage_contribution': {
        "title": u"Module contribution",
        "widget": deform.widget.CheckboxWidget(true_val='1', false_val='0'),
        "section": u"Activation des modules d'export Sage",
    },
    'sage_rginterne': {
        "title": u"Module RG Interne",
        "widget": deform.widget.CheckboxWidget(true_val='1', false_val='0'),
        "section": u"Activation des modules d'export Sage",
    },
    'sage_rgclient': {
        "title": u"Module RG Client",
        "widget": deform.widget.CheckboxWidget(true_val='1', false_val='0'),
        "section": u"Activation des modules d'export Sage",
    },
    'sage_facturation_not_used': {
        "title": u"Module facturation",
        "description": u"Activé par défaut",
        "widget": deform.widget.CheckboxWidget(
            template='checkbox_readonly.pt'
        ),
        "section": u"Activation des modules d'export Sage",
    },
    # NDF
    "code_journal_ndf": {
        "title": u"Code journal utilisé pour les notes de dépense",
    },
    "compte_cg_ndf": {
        "title": u"Compte de tiers (classe 4) pour les dépenses dues aux \
entrepreneurs",
        "description": u"Le compte général pour les notes de dépense",
    },
    "code_journal_waiver_ndf": {
        "title": u"Code journal spécifique aux abandons de créance",
        "description": u"Code journal utilisé pour l'export des abandons \
de créance, si ce champ n'est pas rempli, le code journal d'export des notes \
de dépense est utilisé. Les autres exports de décaissement utilisent \
    le code journal de la banque concernée.",
        "section": u"Abandon de créance",

    },
    "compte_cg_waiver_ndf": {
        "title": u"Compte abandons de créance",
        "description": u"Compte de comptabilité générale spécifique aux \
abandons de créance dans les notes de dépense",
        "section": u"Abandon de créance",
    },
    "code_tva_ndf": {
        "title": u"Code TVA utilisé pour les décaissements",
        "description": u"Le code TVA utilisé pour l'export des décaissements",
        "section": u"Paiement des notes de dépenses",
    },
    "treasury_measure_ui": {
        "title": u"Indicateur à mettre en évidence",
        "description": u"Indicateur qui sera mis en évidence dans l'interface "
        u"entrepreneur",
        "widget": forms.get_radio(
            values=(
                ('1', u"Trésorerie du jour"),
                ("4", u"Trésorerie de référence"),
                ("8", u"Trésorerie future"),
                ("10", u"Résultat de l'entreprise"),
            )
        )
    },
    "invoice_number_template": {
        "title": u"Gabarit du numéro de facture",
        "description": u"Peut contenir des caractères (préfixes, \
séparateurs… etc), ainsi que des variables et séquences. Ex: {YYYY}-{SEQYEAR}.",
        "missing": colander.required,
        "validator": invoice_number_template_validator,
    },
    "global_sequence_init_value": {
        "title": u"Valeur à laquelle on initialise de la séquence globale",
        "section": u"Séquence globale (SEQGLOBAL)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "year_sequence_init_value": {
        "title": u"Valeur à laquelle on initialise la séquence annuelle",
        "section": u"Séquence annuelle (SEQYEAR)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "year_sequence_init_date": {
        "title": u"Date à laquelle on initialise la séquence annuelle",
        "section": u"Séquence annuelle (SEQYEAR)",
        "widget": deform.widget.DateInputWidget(),
    },
    "month_sequence_init_value": {
        "title": u"Valeur à laquelle on initialise la séquence annuelle",
        "section": u"Séquence annuelle (SEQMONTH)",
        "type": colander.Int(),
        "validator": colander.Range(min=0),
    },
    "month_sequence_init_date": {
        "title": u"Date à laquelle on initialise la séquence annuelle",
        "section": u"Séquence annuelle (SEQMONTH)",
        "widget": deform.widget.DateInputWidget(),
    },
    "accounting_label_maxlength": {
        "title": u"Taille maximum des libellés d'écriture (troncature)",
        "description": u"Autonomie tronquera les libellés d'écriture comptable exportés à cette longueur. Dépend de votre logiciel de comptabilité. Ex :  30 pour quadra, 35 pour sage, 25 pour ciel. Mettre à zéro pour désactiver la troncature.",
        "type": colander.Int(),
    },
}


def get_config_key_schemanode(key, ui_conf):
    """
    Returns a schema node to configure the config 'key'
    This key should appear in the dict here above CONFIGURATION_KEYS
    """
    return colander.SchemaNode(
        ui_conf.get('type', colander.String()),
        title=ui_conf.get('title', key),
        description=ui_conf.get('description'),
        missing=ui_conf.get('missing', u""),
        name=key,
        widget=ui_conf.get('widget'),
        validator=ui_conf.get('validator', None),
    )


def get_config_schema(keys):
    """
    Returns a schema to configure Config objects

    :param list keys: The list of keys we want to configure (ui informations
    should be provided in the CONFIGURATION_KEYS dict

    :results: A colander Schema to configure the given keys
    :rtype: object colander Schema
    """
    schema = colander.Schema()
    mappings = {}
    index = 0
    for key in keys:
        ui_conf = CONFIGURATION_KEYS.get(key, {})
        node = get_config_key_schemanode(key, ui_conf)

        if "section" in ui_conf:  # This element should be shown in a mapping

            section_title = ui_conf['section']
            section_name = safe_unicode(section_title)
            if section_name not in mappings:
                mappings[section_name] = mapping = colander.Schema(
                    title=section_title,
                    name=section_name,
                )
                schema.add(mapping)
            else:
                mapping = mappings[section_name]
            mapping.add(node)
        else:
            schema.insert(index, node)
            index += 1

#    for mapping in mappings.values():
#        schema.add(mapping)
    return schema


def build_config_appstruct(request, keys):
    """
    Build the configuration appstruct regarding the config keys we want to edit

    :param obj request: The pyramid request object (with a config attribute)
    :param list keys: the keys we want to edit
    :returns: A dict storing the configuration values adapted to a schema
    generated by get_config_schema
    """
    appstruct = {}
    for key in keys:
        value = request.config.get(key, "")
        if value:
            ui_conf = CONFIGURATION_KEYS[key]

            if "section" in ui_conf:
                appstruct.setdefault(safe_unicode(ui_conf['section']), {})[key] = value
            else:
                appstruct[key] = value
    return appstruct


TVA_UNIQUE_VALUE_MSG = u"Veillez à utiliser des valeurs différentes pour les \
différents taux de TVA. Pour les tvas de valeurs nulles, merci d'utiliser des \
valeurs négatives pour les distinguer (-1, -2...), elles seront ramenées à 0 \
pour toutes les opérations de calcul."


TVA_NO_DEFAULT_SET_MSG = u"Veuillez définir au moins une tva par défaut \
(aucune TVA par défaut n'a été configurée)."


def get_tva_value_validator(current):
    """
    Return a validator for tva entries

    :param int tva_id: The current configured tva
    :rtype: func
    """
    from autonomie.models.tva import Tva
    if isinstance(current, Tva):
        current_id = current.id
    else:
        current_id = None

    def validator(node, value):
        if not Tva.unique_value(value, current_id):
            raise colander.Invalid(node, TVA_UNIQUE_VALUE_MSG)

    return validator


@colander.deferred
def deferred_tva_value_validator(node, kw):
    """
    Ensure we've got a unique tva value and at least one default tva

    :param obj form: The deform.Form object
    :param dict tva_value: The value configured
    """
    context = kw['request'].context
    return get_tva_value_validator(context)


def has_tva_default_validator(node, value):
    """
    Validator for tva uniqueness
    """
    from autonomie.models.tva import Tva
    if Tva.get_default() is None and not value:
        raise colander.Invalid(node, TVA_NO_DEFAULT_SET_MSG)


def get_tva_edit_schema():
    """
    Add a custom validation schema to the tva edition form
    :returns: :class:`colander.Schema` schema for single tva admin
    """
    from autonomie.models.tva import Tva
    schema = SQLAlchemySchemaNode(Tva)
    schema['value'].validator = deferred_tva_value_validator
    schema['default'].validator = has_tva_default_validator
    return schema


class ActivityTypeConfig(colander.MappingSchema):
    """
        Schema for the configuration of different activity types
    """
    id = forms.id_node()

    label = colander.SchemaNode(
        colander.String(),
        title=u"Libellé",
        validator=colander.Length(max=100)
        )


class ActivityTypesSeqConfig(colander.SequenceSchema):
    """
        The sequence Schema associated with the ActivityTypeConfig
    """
    activity_type = ActivityTypeConfig(
        title=u"Nature du rendez-vous",
        widget=CleanMappingWidget(),
    )


class ActivityModeConfig(colander.MappingSchema):
    label = colander.SchemaNode(
        colander.String(),
        title=u"libellé",
        validator=colander.Length(max=100)
        )


class ActivityModesSeqConfig(colander.SequenceSchema):
    """
    Sequence schema for activity modes configuration
    """
    activity_mode = ActivityModeConfig(
        title=u"Mode d'entretien",
        widget=CleanMappingWidget(),
    )


class ActionConfig(colander.MappingSchema):
    id = forms.id_node()
    label = colander.SchemaNode(
        colander.String(),
        title=u"Sous-titre",
        description=u"Sous-titre dans la sortie pdf",
        validator=colander.Length(max=100)
        )


class ActivitySubActionSeq(colander.SequenceSchema):
    subaction = ActionConfig(
        title=u"",
        widget=CleanMappingWidget(),
    )


class ActivityActionConfig(colander.Schema):
    id = forms.id_node()
    label = colander.SchemaNode(
        colander.String(),
        title=u"Titre",
        description=u"Titre dans la sortie pdf",
        validator=colander.Length(max=255)
    )
    children = ActivitySubActionSeq(
        title=u"",
        widget=CleanSequenceWidget(
            add_subitem_text_template=u"Ajouter un sous-titre",
        )
    )


class ActivityActionSeq(colander.SequenceSchema):
    action = ActivityActionConfig(
        title=u"Titre",
        widget=CleanMappingWidget(),
    )


class WorkshopInfo3(colander.MappingSchema):
    id = forms.id_node()
    label = colander.SchemaNode(
        colander.String(),
        title=u"Sous-titre 2",
        description=u"Sous-titre 2 dans la sortie pdf",
        validator=colander.Length(max=100)
    )


class WorkshopInfo3Seq(colander.SequenceSchema):
    child = WorkshopInfo3(
        title=u"Sous-titre 2",
        widget=CleanMappingWidget(),
    )


class WorkshopInfo2(colander.Schema):
    id = forms.id_node()
    label = colander.SchemaNode(
        colander.String(),
        title=u"Sous-titre",
        description=u"Sous-titre dans la sortie pdf",
        validator=colander.Length(max=255)
    )
    children = WorkshopInfo3Seq(
        title=u"",
        widget=CleanSequenceWidget(
            add_subitem_text_template=u"Ajouter un sous-titre 2",
            orderable=True,
        )
    )


class WorkshopInfo2Seq(colander.SequenceSchema):
    child = WorkshopInfo2(
        title=u"Sous-titre",
        widget=CleanMappingWidget(),
    )


class WorkshopInfo1(colander.Schema):
    id = forms.id_node()
    label = colander.SchemaNode(
        colander.String(),
        title=u"Titre",
        description=u"Titre dans la sortie pdf",
        validator=colander.Length(max=255)
    )
    children = WorkshopInfo2Seq(
        title=u'',
        widget=CleanSequenceWidget(
            add_subitem_text_template=u"Ajouter un sous-titre",
            orderable=True,
        )
    )


class WorkshopInfo1Seq(colander.SequenceSchema):
    actions = WorkshopInfo1(
        title=u'Titre',
        widget=CleanMappingWidget(),
    )


class ActivityConfigSchema(colander.Schema):
    """
    The schema for activity types configuration
    """
    header_img = ImageNode(title=u'En-tête des sortie PDF')
    footer_img = ImageNode(
        title=u'Image du pied de page des sorties PDF',
        description=u"Vient se placer au-dessus du texte du pied de page",
    )
    footer = forms.textarea_node(
        title=u"Texte du pied de page des sorties PDF",
        missing=u"",
    )
    types = ActivityTypesSeqConfig(
        title=u"Configuration des natures de rendez-vous",
        widget=CleanSequenceWidget(
            add_subitem_text_template=u"Ajouter une nature de rendez-vous ",
            orderable=True,
        )
    )
    modes = ActivityModesSeqConfig(
        title=u"Configuration des modes d'entretien",
        widget=CleanSequenceWidget(
            add_subitem_text_template=u"Ajouter un mode d'entretien",
            orderable=True,
        )
    )
    actions = ActivityActionSeq(
        title=u"Configuration des titres disponibles pour la sortie PDF",
        widget=CleanSequenceWidget(
            add_subitem_text_template=u"Ajouter un titre",
            orderable=True,
        )
    )


class WorkshopConfigSchema(colander.Schema):
    header_img = ImageNode(title=u'En-tête des sortie PDF')
    footer_img = ImageNode(
        title=u'Image du pied de page des sorties PDF',
        description=u"Vient se placer au-dessus du texte du pied de page",
    )
    footer = forms.textarea_node(
        title=u"Texte du pied de page des sorties PDF",
        missing=u"",
    )
    actions = WorkshopInfo1Seq(
        title=u"Configuration des titres disponibles pour la sortie PDF",
        widget=CleanSequenceWidget(
            add_subitem_text_template=u"Ajouter une titre",
            orderable=True,
        )
    )


def load_filetypes_from_config(config):
    """
        Return filetypes configured in databas
    """
    attached_filetypes = json.loads(config.get('attached_filetypes', '[]'))
    if not isinstance(attached_filetypes, list):
        attached_filetypes = []
    return attached_filetypes


def get_element_by_name(list_, name):
    """
        Return an element from list_ which has the name "name"
    """
    found = None
    for element in list_:
        if element.name == name:
            found = element
    return found


def merge_config_datas(dbdatas, appstruct):
    """
        Merge the datas returned by form validation and the original dbdatas
    """
    flat_appstruct = forms.flatten_appstruct(appstruct)
    for name, value in flat_appstruct.items():
        dbdata = get_element_by_name(dbdatas, name)
        if not dbdata:
            # The key 'name' doesn't exist in the database, adding new one
            dbdata = Config(name=name, value=value)
            dbdatas.append(dbdata)
        else:
            dbdata.value = value
    return dbdatas


def get_sequence_model_admin(model, title=u"", excludes=(), **kw):
    """
    Return a schema for configuring sequence of models

        model

            The SQLAlchemy model to configure
    """
    node_schema = SQLAlchemySchemaNode(
        model,
        widget=CleanMappingWidget(),
        excludes=excludes,
    )
    node_schema.name = 'data'

    colanderalchemy_config = getattr(model, '__colanderalchemy_config__', {})

    default_widget_options = dict(
        orderable=True,
        min_len=1,
    )
    widget_options = colanderalchemy_config.get('seq_widget_options', {})
    widget_options.update(kw.get('widget_options', {}))

    for key, value in widget_options.items():
        default_widget_options[key] = value

    schema = colander.SchemaNode(colander.Mapping())
    schema.add(
        colander.SchemaNode(
            colander.Sequence(),
            node_schema,
            widget=CleanSequenceWidget(
                **default_widget_options
            ),
            title=title,
            name='datas')
    )

    def dictify(models):
        return {'datas': [node_schema.dictify(model) for model in models]}

    def objectify(datas):
        return [node_schema.objectify(data) for data in datas]

    schema.dictify = dictify
    schema.objectify = objectify
    return schema


class SubCompetenceConfigSchema(colander.MappingSchema):
    id = forms.id_node()
    label = colander.SchemaNode(
        colander.String(),
        title=u"Libellé",
    )


class SubCompetencesConfigSchema(colander.SequenceSchema):
    subcompetence = SubCompetenceConfigSchema(
        widget=CleanMappingWidget(),
    )


class CompetenceRequirement(colander.MappingSchema):
    deadline_id = forms.id_node()
    deadline_label = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.TextInputWidget(readonly=True),
        title=u"Pour l'échéance",
        missing=colander.drop,
    )
    scale_id = colander.SchemaNode(
        colander.Integer(),
        title=u"Niveau requis",
        description=u"Sera mis en évidence dans l'interface",
        widget=forms.get_deferred_select(CompetenceScale)
    )


class CompetenceRequirementSeq(colander.SequenceSchema):
    requirement = CompetenceRequirement(
        title=u'',
        widget=CleanMappingWidget(),
    )


@colander.deferred
def deferred_seq_widget(nodex, kw):
    elements = kw['deadlines']
    return CleanSequenceWidget(
        add_subitem_text_template=u"-",
        min_len=len(elements),
        max_len=len(elements),
    )


@colander.deferred
def deferred_deadlines_default(node, kw):
    """
    Return the defaults to ensure there is a requirement for each configured
    deadline
    """
    return [
        {
            'deadline_label': deadline.label,
            'deadline_id': deadline.id,
        }
        for deadline in kw['deadlines']
    ]


class CompetencePrintConfigSchema(colander.Schema):
    header_img = ImageNode(title=u'En-tête de la sortie imprimable')


def get_admin_schema(factory):
    """
    Return an edit schema for the given factory

    :param obj factory: A SQLAlchemy model
    :returns: A SQLAlchemySchemaNode schema
    :rtype: class:`SQLAlchemySchemaNode`
    """
    schema = SQLAlchemySchemaNode(factory)
    return schema
