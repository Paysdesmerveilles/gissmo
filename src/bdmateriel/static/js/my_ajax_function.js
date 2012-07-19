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

function get_equip_state(selectBox, urlparm1, urlparm2, urlparm3){
    var actiontypevalue = selectBox.options[selectBox.options.selectedIndex].value;
    var singleValues = selectBox.id.split("-")[1];
    var equipstateselect = 'select#id_intervequip_set-'+singleValues+'-equip_state';
    var xhr_equip_state_url = urlparm1
    var xhr_equipment_url = urlparm2
    var xhr_station_url = urlparm3
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

    var equipselect = 'select#id_intervequip_set-'+singleValues+'-equip';
    var station = document.getElementById('id_station');
    var station_id = station.options[station.options.selectedIndex].value;
    var intervention_date = document.getElementById('id_intervention_date_0').value;        
    $.ajax({
      type: "GET",
      url: xhr_equipment_url,
      data: { action: actiontypevalue, station : station_id, date : intervention_date},
      dataType: "json",
      success: function(data) {
          var options = '';
          for (var i = 0; i < data.length; i++) {
            options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
          }
          $(equipselect).html(options);
      }
    });

    var stationselect = 'select#id_intervequip_set-'+singleValues+'-station';
    var station_id = station.options[station.options.selectedIndex].value;
    $.ajax({
      type: "GET",
      url: xhr_station_url,
      data: { action: actiontypevalue, station : station_id, date : intervention_date},
      dataType: "json",
      success: function(data) {
          var options = '';
          for (var i = 0; i < data.length; i++) {
            options += '<option value="' + data[i].optionValue + '">' + data[i].optionDisplay + '</option>';
          }
          $(stationselect).html(options);
      }
    });


}
