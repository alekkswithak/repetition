// navbar tab highlighting
$(document).ready(function() {
    $('li.active').removeClass('active');
    $('a[href="' + location.pathname + '"]').closest('li').addClass('active');
  });

// show add card to custom deck form
$("#toggle").on("click", function(){
    $("#add-cards-dropdown").toggle();
    $("[id=add-check]").toggle();
  });