/*
Function that list the possible state of a station
according to the station action choice
when we describe the intervention 
The trigger is the field station_action
*/
function get_station_state(selectBox, urlparm){
    var actiontypevalue = selectBox.options[selectBox.options.selectedIndex].value;
    var singleValues = selectBox.id.split("-")[1];
    var changeselect = 'select#id_intervstation_set-'+singleValues+'-station_state';
    var xhr_station_state_url = urlparm
    $.ajax({
      type: "GET",
      url: xhr_station_state_url,
      data: { action: actiontypevalue},
      dataType: "json",
      success: function(data) {
          var options = '';
          for (var i = 0; i < data.length; i++) {
            options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
          }
          $(changeselect).html(options);
      }
    });
}

/*
Function that list the possible state of an equipment,
the possible equipment and
the possible place, station and built, that an equipement can take
according to the equipment action choice
when we describe the intervention 
The trigger is the field equip_action
*/
function get_equip_state(selectBox, urlparm1, urlparm2, urlparm3, urlparm4){
    var actiontypevalue = selectBox.options[selectBox.options.selectedIndex].value;
    var singleValues = selectBox.id.split("-")[1];
    var xhr_equip_state_url = urlparm1;
    var xhr_equipment_url = urlparm2;
    var xhr_station_url = urlparm3;
    var xhr_built = urlparm4;

    /*
    As soon as we have an action change the BUY action must disappear
    */
    $("#id_intervequip_set-"+singleValues+"-equip_action option[value='1']").remove();
    /*
    Check that the action is nothing
    */
    if (actiontypevalue == '') {
       /*
       Remove all associate error for that field
       */
       $("#intervequip_set-"+singleValues).find(".errorlist").remove();
       /*
       Initiate all other field to nothing
       */
       var equipselect = 'select#id_intervequip_set-'+singleValues+'-equip';
       $(equipselect).html('<option value= ""> -- choisir une action -- </option>');
       var equipstateselect = 'select#id_intervequip_set-'+singleValues+'-equip_state';
       $(equipstateselect).html('<option value= ""> -- choisir une action -- </option>');
       var stationselect = 'select#id_intervequip_set-'+singleValues+'-station';
       $(stationselect).html('<option value= ""> -- choisir une action -- </option>');
       var builtselect = 'select#id_intervequip_set-'+singleValues+'-built';
       $(builtselect).html('<option value= ""> -- choisir une action -- </option>');
       var note = $('textarea#id_intervequip_set-'+singleValues+'-note').val('');
       }

    /*
    Check that the action is not buying
    */
    if (actiontypevalue == 1) {
       alert('Cette action n\'est pas autorisée dans ce contexte')  
       }

    var equipstateselect = 'select#id_intervequip_set-'+singleValues+'-equip_state';
    $.ajax({
      type: "GET",
      url: xhr_equip_state_url,
      data: { action: actiontypevalue},
      dataType: "json",
      success: function(data) {
          var options = '';
          for (var i = 0; i < data.length; i++) {
            options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
          }
          $(equipstateselect).html(options);
      }
    });

    var station = document.getElementById('id_station');
    var station_id = station.options[station.options.selectedIndex].value;
    var date_intervention = document.getElementById('id_intervention_date_0').value;
    var heure_intervention = document.getElementById('id_intervention_date_1').value;


    /*
    Check that the station, date and time are filled
    else the call to the ajax while not work as expected
    */
    if (! station_id) {
       alert('Il est préférable d\'inscrire le site sur lequel on intervient avant toutes actions sur les équipements')  
       }
    if (! date_intervention) {
       alert('Il est préférable d\'inscrire une date d\'intervention avant toutes actions sur les équipements')  
       }
    if (! heure_intervention) {
       alert('Il est préférable d\'inscrire une heure d\'intervention avant toutes actions sur les équipements')  
       }

    var equipment = document.getElementById('id_intervequip_set-'+singleValues+'-equip');
    var equip_id = equipment.options[equipment.options.selectedIndex].value;

    var equipselect = 'select#id_intervequip_set-'+singleValues+'-equip';
    $.ajax({
      type: "GET",
      url: xhr_equipment_url,
      data: { action: actiontypevalue, station : station_id, date : date_intervention, heure : heure_intervention},
      dataType: "json",
      success: function(data) {
          var options = '';
          for (var i = 0; i < data.length; i++) {
            if (data[i].optionValue == equip_id)
               {
                options += '<option value="' + data[i].optionValue + '" selected="selected">' + data[i].optionDisplay + '</option>';
               }               
            else
               { 
                options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
               }  
          }
          $(equipselect).html(options);
      }
    });

    var stationselect = 'select#id_intervequip_set-'+singleValues+'-station';
    $.ajax({
      type: "GET",
      url: xhr_station_url,
      data: { action: actiontypevalue, station : station_id, date : date_intervention, heure : heure_intervention},
      dataType: "json",
      success: function(data) {
          var options = '';
          for (var i = 0; i < data.length; i++) {
            options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
          }
          $(stationselect).html(options);

          /*
          Obtain the built if we have only one site as destination 
          else display that they must choose a site first
          */
          var builtselect = 'select#id_intervequip_set-'+singleValues+'-built';
          if (data.length == 1)             
             {
              station_id = data[0].optionValue;
              $.ajax({
                type: "GET",
                url: xhr_built,
                data: { action: actiontypevalue, station : station_id, date : date_intervention, heure : heure_intervention},
                dataType: "json",
                success: function(data) {
                    var options = '';
                    for (var i = 0; i < data.length; i++) {
                      options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
                    }
                    $(builtselect).html(options);
                }
              });
             }
          else
             $(builtselect).html('<option value= ""> -- choisir un site -- </option>');
      }
    });
/*
    var builtselect = 'select#id_intervequip_set-'+singleValues+'-built';
    $.ajax({
      type: "GET",
      url: xhr_built,
      data: { action: actiontypevalue, station : station_id, date : date_intervention, heure : heure_intervention},
      dataType: "json",
      success: function(data) {
          var options = '';
          for (var i = 0; i < data.length; i++) {
            options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
          }
          $(builtselect).html(options);
      }
    });
*/
}

/*
Function that list the equipment operational for a station
when we describe the chain component of a channel
The trigger is the field order
*/
function get_equip_oper(selectBox, urlparm1){
    var singleValues = selectBox.id.split("-")[1];
    var xhr_equip_oper_url = urlparm1;

    var station = document.getElementById('id_station');
    var station_id = station.value;
    var start_date = document.getElementById('id_start_date_0').value;
    var start_heure = document.getElementById('id_start_date_1').value;

    /*
    Check that the station is filled
    else the call to the ajax while not work as expected
    */
    if (! station_id) {
       alert('Il est préférable d\'inscrire le site sur lequel on intervient avant toutes actions sur les équipements')  
       }
    if (! start_date) {
       alert('Il est préférable d\'inscrire une date de début pour le canal avant la description de la chaîne d\'acquisition')  
       }
    if (! start_heure) {
       alert('Il est préférable d\'inscrire une heure de début pour le canal avant la description de la chaîne d\'acquisition')  
       }
 
    var equipselect = 'select#id_chain_set-'+singleValues+'-equip';
    $.ajax({
      type: "GET",
      url: xhr_equip_oper_url,
      data: { station : station_id, date : start_date, heure : start_heure},
      dataType: "json",
      success: function(data) {
          var options = '';
          for (var i = 0; i < data.length; i++) {
            options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
          }
          $(equipselect).html(options);
      }
    });
}

/*
Function that return the dip and azimuth values
according to the channel code choice
when we describe the channel
The trigger is the field channel_code
*/
function get_dip_azimut_value(selectBox){
    var channel_code = document.getElementById('id_channel_code');
    var channel_value = channel_code.options[channel_code.options.selectedIndex].value;
    var dip = document.getElementById('id_dip');
    var azimuth = document.getElementById('id_azimuth');

    switch(channel_value.substring(2)){
    case 'E':
       dip.value = '0';
       azimuth.value = '90';
       break;
    case 'N':
       dip.value = '0';
       azimuth.value = '0';
       break;
    case 'Z':
       dip.value = '-90';
       azimuth.value = '0';
       break;
    }
}

/*
Function that return the latitude, longitude and elevation for a station
when we describe the channel
The trigger is the field station
*/
function get_station_position(selectBox, urlparm1){
    var singleValues = selectBox.id.split("-")[1];
    var xhr_station_position_url = urlparm1;

    var station = document.getElementById('id_station');
    var station_id = station.options[station.options.selectedIndex].value;

    /*
    Check that the station is filled
    else the call to the ajax while not work as expected
    */
    if (! station_id) {
       alert('Il est préférable d\'inscrire le site sur lequel on intervient avant toutes actions sur les équipements')  
       }
 
    var latitude = document.getElementById('id_latitude');
    var longitude = document.getElementById('id_longitude');
    var elevation = document.getElementById('id_elevation');
    $.ajax({
      type: "GET",
      url: xhr_station_position_url,
      data: { station : station_id},
      dataType: "json",
      success: function(data) {
          latitude.value = data[0].latitude;
          longitude.value = data[0].longitude;
          elevation.value = data[0].elevation;
      }
    });
}


/*
Function that list the built for a site
when we describe the intervention 
The trigger is the field station
*/
function get_site_built(selectBox, urlparm1){
    var singleValues = selectBox.id.split("-")[1];
    var stationvalue = selectBox.options[selectBox.options.selectedIndex].value;
    var xhr_built_url = urlparm1;

    var station_id = stationvalue;

    /*
    Check that the station is filled
    else the call to the ajax while not work as expected
    */
    if (! station_id) {
       alert('Il est préférable d\'inscrire le site résultant de l\'action avant de sélectionner un bâti')  
       }
 
    var builtselect = 'select#id_intervequip_set-'+singleValues+'-built';
    $.ajax({
      type: "GET",
      url: xhr_built_url,
      data: { station : station_id},
      dataType: "json",
      success: function(data) {
          var options = '';
          for (var i = 0; i < data.length; i++) {
            options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
          }
          $(builtselect).html(options);
      }
    });
}
