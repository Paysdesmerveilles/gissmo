/*
Function that validate the date format yyyy-mm-dd and the value
*/
function isValidDate(date)
{
    var matches = /^(\d{4})[-](\d{2})[-](\d{2})$/.exec(date);
    if (matches == null) return false;
    var d = matches[3];
    var m = matches[2] - 1;
    var y = matches[1];
    var composedDate = new Date(y, m, d);
    return composedDate.getDate() == d &&
            composedDate.getMonth() == m &&
            composedDate.getFullYear() == y;
}

/*
Function that validate the time format hh:mm:ss and the value
*/
function isValidTime(time)
{
    var matches = /^(\d{2})[:](\d{2})[:](\d{2})$/.exec(time);
    if (matches == null) return false;
    var hour = matches[1];
    var minute = matches[2];
    var second = matches[3];
    if (hour < 0  || hour > 23) return false;
    if (minute < 0 || minute > 59) return false;
    if (second < 0 || second > 59) return false;
    return true;
}

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
Function that list the possible equipment
according to the equipment action choice
when we describe the intervention 
The trigger is the field equip
*/
function get_equip(selectBox, urlparm1){
    var singleValues = selectBox.id.split("-")[1];
    var xhr_equipment_url = urlparm1;
    /*
    We obtain the actiontypevalue by the document.getElementById and not by
    selectBox.options[selectBox.options.selectedIndex].value because we call this function
    from : onfocus on equip
    The last one to reflect the change on intervention date 
    */    
    var actiontypevalue = document.getElementById('id_intervequip_set-'+singleValues+'-equip_action').value;
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
       $(equipselect).html('<option value= ""> -- choose an action -- </option>');
       var equipstateselect = 'select#id_intervequip_set-'+singleValues+'-equip_state';
       $(equipstateselect).html('<option value= ""> -- choose an action -- </option>');
       var stationselect = 'select#id_intervequip_set-'+singleValues+'-station';
       $(stationselect).html('<option value= ""> -- choose an action -- </option>');
       var builtselect = 'select#id_intervequip_set-'+singleValues+'-built';
       $(builtselect).html('<option value= ""> -- choose an action -- </option>');
       var note = $('textarea#id_intervequip_set-'+singleValues+'-note').val('');
       }

    var station = document.getElementById('id_station');
    var station_id = station.options[station.options.selectedIndex].value;
    var date_intervention = document.getElementById('id_intervention_date_0').value;
    var heure_intervention = document.getElementById('id_intervention_date_1').value;
    /* 
    06/08/2013 Add to keep the intervention number when we change the intervention date of an existing one
    This trick permit us to exclude the intervention from the function equip_state_todate and equip_place_todate_id
    We need this trick because the functions look in the DB for the state and place for a date before the change occur
    and if the date of the intervention change this interfere. Thus we have to exclude this from the query only if the date change
    */
    var intervention_id = document.getElementById('id_intervequip_set-'+singleValues+'-intervention').value;

    /*
    Check that the station, date and time are filled
    else the call to the ajax while not work as expected
    */
    if (! actiontypevalue) {
       alert('It\'s better to registrate an action before accessing equipments');
       return  
       }
    if (! station_id) {
       alert('It\'s better to registrate the site on which we perfom an intervention before adding action on equipments.');
       return  
       }
    if (! isValidDate(date_intervention)) {
       alert('It\'s better to registrate a valid intervention date before any action on equipments');
       return
       }
    if (! isValidTime(heure_intervention)) {
       alert('It\'s better to registrate a valide intervention time before any action on equipments');
       return
       }

    var equipment = document.getElementById('id_intervequip_set-'+singleValues+'-equip');
    var equip_id = equipment.options[equipment.options.selectedIndex].value;

    var equipselect = "select#id_intervequip_set-"+singleValues+"-equip";
    
    var myselect = $("select#id_intervequip_set-"+singleValues+"-equip");

    $.ajax({
      type: "GET",
      url: xhr_equipment_url,
      async: false,
      data: { action: actiontypevalue, station : station_id, date : date_intervention, heure : heure_intervention, intervention : intervention_id},
      dataType: "json",
      success: function(data) {
          var options = '';
          for (var i = 0; i < data.length; i++) {
            if (data[i].optionValue == equip_id)
               {
                /*options += '<option value="' + data[i].optionValue + '" selected="selected">' + data[i].optionDisplay + '</option>';*/
                options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
               }               
            else
               { 
                options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
               }  
          }
          /*
          We select the options by two methods
          1) Via .val
          2) Get the index value (set by .val in point 1), put this in the selectedIndex and refresh
          All this to obtain the good value in the box of the select in FireFox
          */
          $(equipselect).empty().append(options);
          $(equipselect).val(equip_id);
          var selection = $(equipselect).attr("selectedIndex");
          myselect[0].selectedIndex = selection;
          myselect.selectmenu("refresh", true);
      }
    });
}

/*
Function that list the possible state of an equipment,
the possible equipment and
the possible place, station and place, that an equipement can take
according to the equipment action choice
when we describe the intervention 
The trigger is the field equip_action
*/
function get_equip_state(selectBox, urlparm1, urlparm2, urlparm3, urlparm4){
    /*var actiontypevalue = selectBox.options[selectBox.options.selectedIndex].value;*/
    var singleValues = selectBox.id.split("-")[1];
    var xhr_equip_state_url = urlparm1;
    var xhr_equipment_url = urlparm2;
    var xhr_station_url = urlparm3;
    var xhr_built = urlparm4;

    /*
    We obtain the actiontypevalue by the document.getElementById and not by
    selectBox.options[selectBox.options.selectedIndex].value because we call this function
    from two places : onchange on equip_action and onfocus on equip
    The last one to reflect the change on intervention date 
    */
    var actiontypevalue = document.getElementById('id_intervequip_set-'+singleValues+'-equip_action').value;

    /*
    As soon as we have an action change the BUY action must disappear
    */
    /*$("#id_intervequip_set-"+singleValues+"-equip_action option[value='1']").remove();*/
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
       $(equipselect).html('<option value= ""> -- choose an action -- </option>');
       var equipstateselect = 'select#id_intervequip_set-'+singleValues+'-equip_state';
       $(equipstateselect).html('<option value= ""> -- choose an action -- </option>');
       var stationselect = 'select#id_intervequip_set-'+singleValues+'-station';
       $(stationselect).html('<option value= ""> -- choose an action -- </option>');
       var builtselect = 'select#id_intervequip_set-'+singleValues+'-built';
       $(builtselect).html('<option value= ""> -- choose an action -- </option>');
       var note = $('textarea#id_intervequip_set-'+singleValues+'-note').val('');
       }

    /*
    Check that the action is not buying
    */
    /*
    if (actiontypevalue == 1) {
       alert('This action is not allowed in this context')  
       }
    */

    var station = document.getElementById('id_station');
    var station_id = station.options[station.options.selectedIndex].value;
    var date_intervention = document.getElementById('id_intervention_date_0').value;
    var heure_intervention = document.getElementById('id_intervention_date_1').value;
    /* 
    06/08/2013 Add to keep the intervention number when we change the intervention date of an existing one
    This trick permit us to exclude the intervention from the function equip_state_todate and equip_place_todate_id
    We need this trick because the functions look in the DB for the state and place for a date before the change occur
    and if the date of the intervention change this interfere. Thus we have to exclude this from the query only if the date change
    */
    var intervention_id = document.getElementById('id_intervequip_set-'+singleValues+'-intervention').value;

    /*
    Check that the station, date and time are filled
    else the call to the ajax while not work as expected
    */
    if (! actiontypevalue) {
       return  
       }
    if (! station_id) {
       alert('It\'s better to registrate the site on which we perform an intervention before any action on equipments');
       return
       }
    if (! isValidDate(date_intervention)) {
       alert('It\'s better to registrate a valid intervention date before any action on equipments');
       return
       }
    if (! isValidTime(heure_intervention)) {
       alert('It\'s better to registrate a valid intervention time before any action on equipments');
       return
       }

    var equipment = document.getElementById('id_intervequip_set-'+singleValues+'-equip');
    var equip_id = equipment.options[equipment.options.selectedIndex].value;

    var equipselect = "select#id_intervequip_set-"+singleValues+"-equip";

    $.ajax({
      type: "GET",
      url: xhr_equipment_url,
      data: { action: actiontypevalue, station : station_id, date : date_intervention, heure : heure_intervention, intervention : intervention_id},
      dataType: "json",
      success: function(data) {
          var options = '';
          for (var i = 0; i < data.length; i++) {
            options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
          }
          $(equipselect).html(options);
          $(equipselect).val(equip_id);
      }
    });

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
          Obtain the place if we have only one site as destination 
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
                      {options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';}
                    }
                    $(builtselect).html(options);
                }
              });
             }
          else
              {$(builtselect).html('<option value= ""> -- choose a site -- </option>');}
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
    var start_date = document.getElementById('id_start_date_0').value;
    var start_heure = document.getElementById('id_start_date_1').value;

    /*
    Check that the station is filled
    else the call to the ajax while not work as expected
    */
    if (! station_id) {
       alert('It\'s better to registrate a site on which we perform an intervention before any action on equipments')  
       }
    if (! start_date) {
       alert('It\'s better to registrate a starting date for the channel before adding acquisition chain description')  
       }
    if (! start_heure) {
       alert('It\'s better to registrate a starting time for the channel before adding acquisition chain description')  
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
       dip.value = '0.0';
       azimuth.value = '90.0';
       break;
    case 'N':
       dip.value = '0.0';
       azimuth.value = '0.0';
       break;
    case 'Z':
       dip.value = '-90.0';
       azimuth.value = '0.0';
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
       alert('It\'s better to registrate the site on which you perform an intervention bafore any action on equipments')  
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
Function that list the place for a site
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
       alert('It\'s better to registrate the site that results from the action before selecting a place')
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

/*
Function that list the value for a parameter
when we describe the chainconfig
The trigger is the field parameter
*/
function get_parameter_value(selectBox, urlparm1){
    var singleValues = selectBox.id.split("-")[1];
    var parametervalue = document.getElementById('id_chainconfig_set-'+singleValues+'-parameter').value;
    var xhr_parameter_value_url = urlparm1;
    var parameter_id = parametervalue;


    var value = document.getElementById('id_chainconfig_set-'+singleValues+'-value');
    var value_id = value.options[value.options.selectedIndex].value;

    var valueselect = 'select#id_chainconfig_set-'+singleValues+'-value';
    var myselect = $("select#id_chainconfig_set-"+singleValues+"-value");

    $.ajax({
      type: "GET",
      url: xhr_parameter_value_url,
      data: { parameter : parameter_id},
      dataType: "json",
      success: function(data) {
          var options = '';
          for (var i = 0; i < data.length; i++) {
            options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
          }
          $(valueselect).html(options);
          $(valueselect).val(value_id);
          var selection = $(valueselect).attr("selectedIndex");
          myselect[0].selectedIndex = selection;
          myselect.selectmenu("refresh", true);
      }
    });
}
