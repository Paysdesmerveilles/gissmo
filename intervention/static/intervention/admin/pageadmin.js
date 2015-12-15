/* 
 * Get allowed transition regarding choosen site.
*/
function get_transitions(select, url){
  var site_id = select.options[select.selectedIndex].value;
  var $ = django.jQuery;
  $.ajax({
    url: url,
    data: { site: site_id },
    dataType: 'json',
    success: function(result, status, xhr) {
      var transitions = result.allowed_transitions;
      var select = $('td.field-transition select')
      var options = $('td.field-transition select option')
      // first remove all available options
      options.remove()
      // then display compatible ones
      $.each(transitions, function(i){
        select.append($("<option></option>")
               .attr("value", i)
               .text(transitions[i]));
      });
    },
  });
}
