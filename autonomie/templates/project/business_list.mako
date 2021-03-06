<%doc>
    * Copyright (C) 2012-2016 Croissance Commune
 * Authors:
       * Arezki Feth <f.a@majerti.fr>;
       * Miotte Julien <j.m@majerti.fr>;
       * TJEBBES Gaston <g.t@majerti.fr>

 This file is part of Autonomie : Progiciel de gestion de CAE.

    Autonomie is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Autonomie is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Autonomie.  If not, see <http://www.gnu.org/licenses/>.
</%doc>
<%inherit file="${context['main_template'].uri}" />
<%namespace file="/base/utils.mako" import="dropdown_item"/>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%block name='mainblock'>
<div class='row page-header-block'>
% if request.has_permission('add.estimation'):
    <a class='btn btn-primary primary-action'
        href='${add_estimation_url}'>
        <i class='fa fa-plus-circle'></i>&nbsp;Créer un devis
    </a>
% endif
% if request.has_permission('add.invoice'):
    <a class='btn btn-primary primary-action'
        href='${add_invoice_url}'>
        <i class='fa fa-plus-circle'></i>&nbsp;Créer une facture
    </a>
% endif
</div>

% if form is not UNDEFINED and form:
<div class='panel panel-default page-block'>
    <div class='panel-heading'>
        <a  href='#filter-form'
            data-toggle='collapse'
            aria-expanded="false"
            aria-controls="filter-form">
            <i class='glyphicon glyphicon-search'></i>&nbsp;
            Filtres&nbsp;
            <i class='glyphicon glyphicon-chevron-down'></i>
        </a>
        % if '__formid__' in request.GET:
            <div class='help-text'>
                <small><i>Des filtres sont actifs</i></small>
            </div>
            <div class='help-text'>
                <a href="${request.current_route_path(_query={})}">
                    <i class='glyphicon glyphicon-remove'></i> Supprimer tous les filtres
                </a>
            </div>
        % endif
    </div>
    <div class='panel-body'>
        <div class='collapse' id='filter-form'>
            <div class='row'>
                <div class='col-xs-12'>
                    ${form|n}
                </div>
            </div>
        </div>
    </div>
</div>
% endif
<div class='panel panel-default page-block'>
    <div class='panel-heading'>
        ${records.item_count} Résultat(s)
    </div>
    <div class='panel-body'>
        <table class="table table-striped table-condensed table-hover">
            <thead>
                <tr>
                    <th class="visible-lg">${sortable(u"Créé le", "created_at")}</th>
                    <th>${sortable(u"Nom", "name")}</th>
                    <th>Documents</th>
                    <th>CA</th>
                    <th>Statut</th>
                    <th class="actions">Actions</th>
                </tr>
            </thead>
            <tbody>
                % if records:
                    % for id, business in records:
                    <tr class='tableelement business-closed-${business.closed} business-check-${business.file_requirement_service.check(business)}'>
                        <tr class='tableelement'>
                            <td>
                                ${api.format_date(business.created_at)}
                            </td>
                            <td>
                                ${business.name}
                            </td>
                            <td>
                                <ul>
                                    % for estimation in business.estimations:
                                        <li>
                                            Devis : ${estimation.name}
                                        </li>
                                    % endfor
                                    % for invoice in business.invoices:
                                        <li>
                                            ${api.format_task_type(invoice)}
                                            % if invoice.official_number:
                                            n°${invoice.official_number}
                                            % endif
                                            : ${invoice.name}
                                        </li>
                                    % endfor
                                </ul>
                            </td>
                            <td>
                            ${api.format_amount(sum([i.ttc for i in business.invoices]), precision=5)|n}&nbsp;€
                            </td>
                            <td>
                            % if business.closed:
                            <i class='fa fa-folder'></i>&nbsp;Clôturée
                            % else:
                            <i class="fa fa-folder-open"></i>&nbsp;En cours
                            % endif
                            </td>
                            <td class='text-right'>
                                ${request.layout_manager.render_panel('menu_dropdown', label="Actions", links=stream_actions(business))}
                            </td>
                        </tr>
                    % endfor
                % else:
                    <tr>
                        <td colspan='7'>
                            Aucune affaire n'a été initiée pour l'instant
                        </td>
                    </tr>
                % endif
            </tbody>
        </table>
        ${pager(records)}
    </div>
</div>
</%block>
<%block name='footerjs'>
$(function(){
        $('input[name=search]').focus();
});
</%block>
