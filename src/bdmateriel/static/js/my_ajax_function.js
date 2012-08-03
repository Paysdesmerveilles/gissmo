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

function get_equip_state(selectBox, urlparm1, urlparm2, urlparm3, urlparm4){
    var actiontypevalue = selectBox.options[selectBox.options.selectedIndex].value;
    var singleValues = selectBox.id.split("-")[1];
    var xhr_equip_state_url = urlparm1;
    var xhr_equipment_url = urlparm2;
    var xhr_station_url = urlparm3;
    var xhr_built = urlparm4;

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
