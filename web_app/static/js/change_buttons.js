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
            if (key == "day-") {
              // delete the elem from the DOM
              //create a select element and add it to the DOM
              var select = document.createElement("select");
              select.setAttribute("scope", "row");
              select.id = elem.id;
              select.setAttribute("placeholder", elem.innerHTML)
              select.setAttribute("form", "price_form-" + price_id);
              select.setAttribute("class", "val-chart")
              elem.parentNode.replaceChild(select, elem);
              select.style.backgroundColor = "#f2f2f2";
              // create the options for the select element
              select.name = "price_day";
              var days = ["", "Every day", "Every Monday", "Every Tuesday", "Every Wednesday", "Every Thursday", "Every Friday", "Every Saturday", "Every Sunday"];
              var options = [];
              for (var i = 0; i < days.length; i++) {
                options[i] = document.createElement("option");
                options[i].setAttribute("value", days[i]);
                options[i].innerHTML = days[i];
              }
              //print the options
              //set the selected option as elem.innerHTML
              for (var i = 0; i < options.length; i++) {
                select.appendChild(options[i]);
                if (options[i].innerHTML == elem.innerHTML) {
                  options[i].setAttribute("selected", "");
                }
              } 
              for (var i = 0; i < options.length; i++) {
                select.appendChild(options[i]);
              }          
            }
            else{
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
                input.setAttribute("datepicker", "");
                input.setAttribute("datepicker-format", "dd/mm/yyyy");
                input.setAttribute("type", "text");

                input.name = "price_date";
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
        }
      });
    // load the script src="https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.6.2/flowbite.min.js"
    var script = document.createElement('script');
    script.src = "https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.6.2/flowbite.min.js";
    script.src = "https://cdnjs.cloudflare.com/ajax/libs/flowbite/1.6.2/datepicker.min.js";
    document.head.appendChild(script);

    
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
        if (input.tagName.toLowerCase() === 'select') {
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
