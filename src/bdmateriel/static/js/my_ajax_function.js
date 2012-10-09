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
      }
    });

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

    /*
    Check that the station is filled
    else the call to the ajax while not work as expected
    */
    if (! station_id) {
       alert('Il est préférable d\'inscrire le site sur lequel on intervient avant toutes actions sur les équipements')  
       }
 
    var equipselect = 'select#id_chain_set-'+singleValues+'-equip';
    $.ajax({
      type: "GET",
      url: xhr_equip_oper_url,
      data: { station : station_id},
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

