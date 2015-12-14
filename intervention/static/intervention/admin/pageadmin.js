/* 
 * Get allowed transition regarding choosen site.
*/
function get_transitions(select, url){
  var site_id = select.options.selectedIndex;
  django.jQuery.ajax({
    url: url,
    data: { site: site_id },
    dataType: 'json',
    success: function(result, status, xhr) {
      var transitions = result.allowed_transitions;
      var select = django.jQuery('td.field-transition select')
      var options = django.jQuery('td.field-transition select option')
      // first remove all available options
      options.remove()
      // then display compatible ones
      django.jQuery.each(transitions, function(i){
        select.append(django.jQuery("<option></option>")
               .attr("value", i)
               .text(transitions[i]));
      });
    },
  });
}
