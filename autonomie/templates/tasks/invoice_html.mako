<%doc>
    Template for invoice readonly display
</%doc>
<%inherit file="/base.mako"></%inherit>
<%block name='content'>
<div class='container' style='overflow:hidden'>
<div>
    %if task.statusPersonAccount  is not UNDEFINED and task.statusPersonAccount:
        <strong>${task.get_status_str().format(genre='', firstname=task.statusPersonAccount.firstname, lastname=task.statusPersonAccount.lastname)}</strong>
        <br />
    %else:
        <strong>Aucune information d'historique ou de statut n'a pu être retrouvée</strong>
        <br />
    %endif
    %if task.CAEStatus in ('sent', 'valid'):
        Vous ne pouvez plus modifier ce document car il a déjà été validé.
    %elif task.CAEStatus in ('wait',):
        Vous ne pouvez plus modifier ce document car il est en attente de validation.
    %endif
        <br />
    <a class='btn btn-primary' href='${request.route_path("invoice", cid=company.id, id=task.IDProject, taskid=task.IDTask, _query=dict(view="pdf"))}' title="Télécharger la version PDF">
        Télécharger la version PDF
    </a>
    <br />
</div>

        <div style='border:1px solid #888'>
            ${html_datas|n}
        </div>
</div>
</%block>
