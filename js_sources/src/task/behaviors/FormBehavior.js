/*
 * File Name : FormBehavior.js
 *
 * Copyright (C) 2012 Gaston TJEBBES g.t@majerti.fr
 * Company : Majerti ( http://www.majerti.fr )
 *
 * This software is distributed under GPLV3
 * License: http://www.gnu.org/licenses/gpl-3.0.txt
 *
 */
import Mn from 'backbone.marionette';
import Validation from 'backbone-validation';
import { serializeForm } from '../../tools.js';
import {displayServerError, displayServerSuccess} from '../../backbone-tools.js';
import BaseFormBehavior from './BaseFormBehavior.js';

var FormBehavior = Mn.Behavior.extend({
    behaviors: [BaseFormBehavior],
	ui: {
        form: "form",
        submit: "button[type=submit]",
        reset: "button[type=reset]"
    },
    events: {
        'submit @ui.form': 'onSubmitForm',
        'click @ui.reset': 'onCancelForm',
    },
    defaults: {
        errorMessage: "Une erreur est survenue"
    },
    serializeForm: function(){
        return serializeForm(this.getUI('form'));
    },
    onSyncError: function(){
        displayServerError("Une erreur a été rencontrée lors de la " +
                           "sauvegarde de vos données");
        Validation.unbind(this.view);
    },
    onSyncSuccess: function(){
        displayServerSuccess("Vos données ont bien été sauvegardées");
        Validation.unbind(this.view);
        console.log("Trigger success:sync from FormBehavior");
        this.view.triggerMethod('success:sync');
    },
    syncServer: function(datas, bound){
        var bound = bound || false;
        var datas = datas || this.view.model.toJSON();

        if (!bound){
            Validation.bind(this.view, {
                attributes: function(view){return _.keys(datas)}
            });
        }
        if (this.view.model.isValid()){
            if (! this.view.model.get('id')){
                this.addSubmit(datas);
            } else {
                this.editSubmit(datas);
            }
        }
    },
    addSubmit: function(datas){
        var destCollection = this.view.getOption('destCollection');
        destCollection.create(
            datas,
            {
                success: this.onSyncSuccess.bind(this),
                error: this.onSyncError.bind(this),
                wait: true,
                sort: true
            },
        )
    },
    editSubmit: function(datas){
        this.view.model.save(
            datas,
            {
                success: this.onSyncSuccess.bind(this),
                error: this.onSyncError.bind(this),
                wait: true
            }
        );
    },
    onSubmitForm: function(event){
        event.preventDefault();
        this.view.model.set(this.serializeForm(), {validate: true});
        this.syncServer();
    },
    onDataPersisted: function(datas){
        console.log("FormBehavior.onDataPersisted");
        this.syncServer(datas, true);
    },
    onCancelForm: function(){
        console.log("FormBehavior.onCancelForm");
        this.view.model.rollback();
    },
    onModalClose: function(){
        console.log("FormBehavior.onModalClose");
    }
});

export default FormBehavior;
