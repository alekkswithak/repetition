exit_integer = parseInt("{{ exit_integer }}")

  function showDiv(data) {
    $("#ele-" + data).show();
    hideElement(exit_integer, data);
  }

  function hideElement(total, active) {
    for (i = 0; i <= total; i++) {
      if (i != active)
        $("#ele-" + i).hide();
    }
  }

  function hideAnswers(total, active) {
    for (i = 0; i <= total; i++) {
      if (i != active)
        $("#card-answer-" + i).hide();
    }
    $("div[id*='card-answer']").each(function (i, el) {
         $('#'+el.id).hide()
     });
  }

  $(document).ready(function(){
    showDiv(counter);
});

var counter = 0
var dict = {"deck_id": "{{ deck_id }}"}
var shown = false
console.log(exit_integer)
document.addEventListener("keypress", function onPress(event) {
  if (event.key === "z") {
      id = $("#card-id-" + counter).text()
      counter++;
      dict[counter] = {id: id, result: 'z'}
      console.log(dict);
      $('#card-answer-' + counter).hide();
      showDiv(counter);
  } else if (event.key === "x") {
      id = $("#card-id-" + counter).text()
      counter++;
      dict[counter] = {id: id, result: 'x'}
      console.log(dict);
      $('#card-answer-'+counter).hide();
      showDiv(counter);
  } else if (event.key === "s") {
      $('#card-answer-'+counter).show()
  }
  if (counter === exit_integer) {
    fetch("{{ redirect_url }}", {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(dict)
    }).then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
    })
    .catch(function(err) {
        console.info(err + " url: " + url);
    });
  }
});
window.onbeforeunload = function() {
  fetch("{{ redirect_url }}", {
      method: "POST",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(dict)
    })
    console.log('POSTING')
return;
}
