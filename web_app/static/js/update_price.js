window.addEventListener('load', function() {
    updateLivePrice = 
        function(){
            var start = $('start').data();
            var url = '/update_price/?'+start;
                fetch(url, {headers:{'Accept': 'application/json','X-Requested-With': 'XMLHttpRequest'},})
                .then(response => response.json())
                .then((dict) => {
                    document.getElementById('amount').innerHTML = dict.amount;
                });
        };
    
    var timeout = setInterval(updateLivePrice(), 10000); 
    var payed = $('payed').data();
    if(payed != null){
        clearInterval(timeout);
    };
});