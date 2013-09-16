(function($) {
    $(document).ready(function() {
        // Hack to expand a specific collapse zone
        // in this case it's the Interventions sur l'equipement zone in the equipment change_form
        $("fieldset.collapse").each(function(i, elem) {
            if ( $(elem).find("h2")[0].innerHTML.toString().search("Interventions") == 0 ) {
                $('a.collapse-toggle',elem).trigger('click');
            }
        }); 
    });
})(django.jQuery);



