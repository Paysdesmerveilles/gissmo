function spread_date(id) {
  var $ = django.jQuery;
  var current_date = $('#' + id + '_0');
  var current_time = $('#' + id + '_1');
  var date_inputs = $('input.vDateField');
  var time_inputs = $('input.vTimeField');
  if (typeof date_inputs !== 'undefined') {
    $.each(date_inputs, function(i){
      date_inputs[i].value = current_date.val();
    });
  }
  if (typeof time_inputs !== 'undefined') {
    $.each(time_inputs, function(j){
    time_inputs[j].value = current_time.val();
    });
  }
  return
}
