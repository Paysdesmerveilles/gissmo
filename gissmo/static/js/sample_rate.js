/*
 * Gives related sample rate regarding first code letter.
 * Do nothing if:
 *   - no code
 *   - sample rate already filled in
 *   - code first letter not found
*/
function set_sample_rate(selection){
  var $ = django.jQuery;
  var value = selection.value;
  var rate = $('input#id_rate');
  var bandcode_values = {
    'B': 20,
    'H': 100,
    'L': 1,
    'V': 0.1,
    'U': 0.01,
    'E': 100,
    'S': 50,
    'M': 5,
    'D': 500,
    'C': 500,
  }
  if (typeof rate == 'undefined') return False;
  if (typeof value == 'undefined') return False;
  if (typeof value !== 'string') return False;
  var first_letter = selection.value[0];
  if (! first_letter in bandcode_values) return False;
  $.each(rate, function(i){
    rate[i].value = bandcode_values[first_letter];
  })
}
