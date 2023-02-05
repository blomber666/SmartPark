window.addEventListener('load', function() {

    updateParkings = function(){
        var url = '/update_parkings/';
        fetch(url, {headers:{'Accept': 'application/json','X-Requested-With': 'XMLHttpRequest'},})
        .then(response => response.json())
        .then((dict) => {
            //alert(dict.park_percent);
            //alert(dict.park_status);
            document.getElementById('park_status').innerHTML = dict.park_status;
            document.getElementById('status-details').innerHTML = dict.park_status;
            document.getElementById('park_percent').style.width = String(dict.park_percent)+'%';
            document.getElementById('img-park').src="/media/park_1.png";
            //alert('ok');
            console.log(dict.park_status);
        });
    };

    setInterval(updateParkings, 5000);

});