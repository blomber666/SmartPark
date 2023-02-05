window.addEventListener('load', function() {

    updateLivePrice = function(){
        if (document.getElementById("start").getAttribute("value") == null){
            //alert("no stop")
            return false;
        }
        else {
            var start = document.getElementById("start").getAttribute("value");
            if(document.getElementById("pay").getAttribute("value") == "payed"){
                //alert("payed");
                clearInterval(timeout);
                return false;
            }; 
        };
        //alert(start);
        var url = '/update_price/?'+start;
            fetch(url)
            .then(response => response.text())
            .then((dict) => {
                alert(dict.amount);
               document.getElementById('amount').innerHTML = dict.amount;
               document.getElementById('price-per-min').innerHTML = dict.amount;
            });
    };
    
    var timeout = setInterval(updateLivePrice(), 10000); 

});