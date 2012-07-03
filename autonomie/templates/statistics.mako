<%inherit file="base.mako"></%inherit>
<%block name='actionmenu'>
<br />
<div class='row'>
    <div class='span7'>
        <div class="form-horizontal">
            <div class="control-group">
                <label class="control-label" for="year">Choix de l'entreprise</label>
                <div class="controls">
                    <select id='company-select' name='company' data-placeholder="Sélectionner une entreprise">
                        <option value=''></option>
                        %for company in companies:
                            %if current_company is not UNDEFINED and company[0] == current_company.id:
                                <option selected='1' value='${request.route_path("statistic", id=company[0])}'>${company[1]}</option>
                            % else:
                                <option value='${request.route_path("statistic", id=company[0])}'>${company[1]}</option>
                            % endif
                        % endfor
                    </select>
                </div>
            </div>
        </div>
        % if current_company is not UNDEFINED:
            <form class='navbar-form form-search form-horizontal' id='search_form' method='GET'>
                <div class="control-group">
                    <label class="control-label" for="year">Chiffres depuis l'année</label>
                    <div class="controls">
                        <select name='year' id='year-select' class='span2' data-placeholder="Chiffres depuis">
                            %for year in years:
                                %if unicode(current_year) == unicode(year):
                                    <option selected="1" value='${year}'>${year}</option>
                                %else:
                                    <option value='${year}'>${year}</option>
                                %endif
                            %endfor
                        </select>
                    </div>
                </div>
            </form>
        % endif
    </div>
</div>
% if current_company is not UNDEFINED:
    <hr />
% endif
</%block>
<%block name="content">
% if current_company is not UNDEFINED:
    <div class='row'>
        <div class="span6 offset3">
            <div class="well">
                <b>Statistiques pour ${current_company.name}</b>
                <br />
                Nombre de projet(s) : ${len(projects)}
                <br />
                Nombre de client(s) : ${len(clients)}
                <br />
                Nombre de prospect(s) : ${len(prospects)}
                <br />
                %if current_year is not UNDEFINED:
                    <b>Depuis le 1er janvier ${current_year}</b>
                    <br />
                % endif
                Nombre de devis : ${len(estimations)}
                <br />
                Nombre de facture : ${len(invoices)}

                <br />
                Nombre de factures annulées : ${len([inv for inv in invoices if inv.is_cancelled])}
            </div>
        </div>
    </div>
% endif
</%block>
<%block name='footerjs'>
$('#company-select').chosen();
$('#company-select').change(function(){window.location = $("#company-select option:selected").val();});
% if current_company is not UNDEFINED:
    $('#year-select').chosen({allow_single_deselect: true});
    $('#year-select').change(function(){$(this).closest('form').submit()});
% endif
</%block>
