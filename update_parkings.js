window.addEventListener('load', function() {

    updateParkings = 
        function(){
            var url = '/update_map/';

            fetch(url, {headers:{'Accept': 'application/json','X-Requested-With': 'XMLHttpRequest'},})
            .then(response => response.json())
            .then((dict) => {
                document.getElementById('park_status').innerHTML = dict.park_status;
                document.getElementById('park_percent').style.width = String(dict.park_percent)+'%';
                document.getElementById('park1').firstChild.src="/media/park_1.png";
            });
        };

    setInterval(updateLiveParkings(), 5000);

});