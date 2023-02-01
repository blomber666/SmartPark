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
        const elem = document.getElementById(key + price_id);
        if (elem) {
          elem.setAttribute("contenteditable", "true");
          elem.style.backgroundColor = "white";
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
};

function cancel_click(price_id) {

    var keys = ["date-", "day-", "s_time-", "e_time-", "price-"];
    keys.forEach(function(key) {
        const elem = document.getElementById(key + price_id);
        if (elem) {
          elem.setAttribute("contenteditable", "false");
          elem.style.backgroundColor = "";
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
