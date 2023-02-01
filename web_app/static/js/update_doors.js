window.addEventListener('load', function() {

    updateLiveGate = 
        function(smartpark, door){
            var url = 'state/door_'+ smartpark +'_'+ door +'/';
            var div = null

            fetch(url)
            .then((response) => {
                return response.text()
            })
            .then((html) => {
                if (door == 1){
                    document.getElementById("entry_state").innerHTML = html;
                    // alert("ok entry" + html);
                }
                else{
                    document.getElementById("exit_state").innerHTML=html;
                    // alert("ok exit"+html); 
                }
            })

        };

    setInterval(updateLiveGate, 3000, 1, 1); //entry door state

    setInterval(updateLiveGate, 3000, 1, 2); //exit door state


});