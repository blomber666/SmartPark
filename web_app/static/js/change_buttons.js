function edit_click(price_id) {

    var edit = document.getElementById('edit-'+ price_id);
    var remove = document.getElementById('remove-'+ price_id);
    var confirm = document.getElementById('confirm-'+ price_id);
    var cancel = document.getElementById('cancel-'+ price_id);

    edit.style.display = 'none';
    remove.style.display = 'none';
    confirm.style.display = 'block';
    cancel.style.display = 'block';
    confirm.setAttribute("name", "edit");

    var keys = ["date-", "day-", "s_time-", "e_time-", "price-"];
    keys.forEach(function(key) {
        var elem = document.getElementById(key + price_id);
        if (elem) {
          // create an input element and remove the elem from the DOM, but mantain its content, id and class
          var input = document.createElement("input");
          input.setAttribute("scope", "row");
          input.id = elem.id;
          input.setAttribute("placeholder", elem.innerHTML)
          input.value = elem.innerHTML;
          input.setAttribute("form", "price_form-" + price_id);
          input.setAttribute("class", "val-chart")
          elem.parentNode.replaceChild(input, elem);
          input.style.backgroundColor = "#f2f2f2";

          if (key == "price-") {
            input.setAttribute("type", "number");
            input.setAttribute("step", "0.01");
            input.name = "price_price";
          }
          if (key == "date-") {
            input.setAttribute("type", "date");
            input.name = "price_date";
          }
          if (key == "day-") {
            input.setAttribute("type", "text");
            input.name = "price_day";
          }
          if (key == "s_time-") {
            input.setAttribute("type", "time");
            input.name = "price_start_time";
            input.value = input.value.substring(0, 5);
          }
          if (key == "e_time-") {
            input.setAttribute("type", "time");
            input.name = "price_end_time";
            input.value = input.value.substring(0, 5);
          }          
         }
      });
};

function delete_click(price_id) {

    var edit = document.getElementById('edit-'+ price_id);
    var remove = document.getElementById('remove-'+ price_id);
    var confirm = document.getElementById('confirm-'+ price_id);
    var cancel = document.getElementById('cancel-'+ price_id);

    edit.style.display = 'none';
    remove.style.display = 'none';
    confirm.style.display = 'block';
    cancel.style.display = 'block';
    confirm.setAttribute("name", "delete");
    confirm.setAttribute("value", price_id);
};

function cancel_click(price_id) {
    var keys = ["date-", "day-", "s_time-", "e_time-", "price-"];
    keys.forEach(function(key) {
        var input = document.getElementById(key + price_id);
        if (input.tagName.toLowerCase() === 'input') {
          var td = document.createElement("td");
          td.setAttribute("scope","row");
          td.id = input.id;
          td.setAttribute("class","val-chart");
          td.innerHTML = input.getAttribute("placeholder");
          input.parentNode.replaceChild(td, input);
          input.remove();
        }
    });

    var edit = document.getElementById('edit-'+ price_id);
    var remove = document.getElementById('remove-'+ price_id);
    var confirm = document.getElementById('confirm-'+ price_id);
    var cancel = document.getElementById('cancel-'+ price_id);

    confirm.style.display = 'none';
    cancel.style.display = 'none';
    edit.style.display = 'block';
    remove.style.display = 'block';
};
