window.addEventListener('load', function() {

    updateParkings = 
        function(){
            var url = '/update_parkings/';
            fetch(url, {headers:{'Accept': 'application/json','X-Requested-With': 'XMLHttpRequest'},})

            .then(response => response.json())
            .then((dict) => {
                alert('then');
                alert(document.getElementById('park_status'));
                document.getElementById('park_status').innerHTML = dict.park_status;
                alert(document.getElementById('park_status'));
                document.getElementById('park_percent').style.width = String(dict.park_percent)+'%';
                document.getElementById('park1').firstChild.src="/media/park_1.png?t="+ new Date().getTime();;
                alert('ok');
                console.log(dict.park_status);
            });
        };

    setInterval(updateParkings(), 5000);

});