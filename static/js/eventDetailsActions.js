$(window).scroll(function() {
    var hT = $('#circle').offset().top,
        hH = $('#circle').outerHeight(),
        wH = $(window).height(),
        wS = $(this).scrollTop();
    console.log((hT - wH), wS);
    if (wS > (hT + hH - wH)) {
        $('.count').each(function() {
            $(this).prop('Counter', 0).animate({
                Counter: $(this).text()
            }, {
                duration: 900,
                easing: 'swing',
                step: function(now) {
                    $(this).text(Math.ceil(now));
                }
            });
        }); {
            $('.count').removeClass('count').addClass('counted');
        };
    }
});

//paso 3
//drawRoute() pintará la ruta entre 2 puntos
function drawRoute(destinationAddress, originAddress, _waypoints,_directionsRenderer) {
    //Define la variable request para route .
    var _request = '';

    var directionsService = new google.maps.DirectionsService();
    //Esto es para más de 2 localizaciones por si se añaden con el listener
    if (_waypoints.length > 0) {
        _request = {
            origin: originAddress,
            destination: destinationAddress,
            waypoints: _waypoints, //un array de waypoints
            optimizeWaypoints: true, //set a true if si se quiere determinar la ruta mas corta.
            travelMode: google.maps.DirectionsTravelMode.DRIVING
        };
    } else {
        //para 1 o 2 direcciones, aqui no se usan puntos
        _request = {
            origin: originAddress,
            destination: destinationAddress,
            travelMode: google.maps.DirectionsTravelMode.DRIVING
        };
    }
 
    //This will take the request and draw the route and return response and status as output
    directionsService.route(_request, function (_response, _status) {
        if (_status == google.maps.DirectionsStatus.OK) {
            _directionsRenderer.setDirections(_response);
        }
    });

    return _directionsRenderer;
}

//paso 2
//getRoutePointsAndWaypoints() calcula los puntos que usa drawRoute()
function getRoutePointsAndWaypoints(_directionsRenderer,_mapPoints) {
    //Define a variable for waypoints.
    var _waypoints = new Array();
 
    if (_mapPoints.length > 2) //Waypoints will be come.
    {
        for (var j = 1; j < _mapPoints.length - 1; j++) {
            var address = _mapPoints[j];
            if (address !== "") {
                _waypoints.push({
                    location: address,
                    stopover: true  //stopover is used to show marker on map for waypoints
                });
            }
        }
        //Call a drawRoute() function
        _directionsRenderer = drawRoute(_mapPoints[0], _mapPoints[_mapPoints.length - 1], _waypoints,_directionsRenderer);
    } else if (_mapPoints.length > 1) {
        //Call a drawRoute() function only for start and end locations
        _directionsRenderer = drawRoute(_mapPoints[_mapPoints.length - 2], _mapPoints[_mapPoints.length - 1], _waypoints,_directionsRenderer);
    } else {
        //Call a drawRoute() function only for one point as start and end locations.
        _directionsRenderer = drawRoute(_mapPoints[_mapPoints.length - 1], _mapPoints[_mapPoints.length - 1], _waypoints,_directionsRenderer);
    }
    return _directionsRenderer;
}
 
//paso 1
//InitializeMap() inicializa el mapa que se carga en la API
function InitializeMap() {
    
    //Define a variable with all map points.
    var _mapPoints = new Array();

    //Define a DirectionsRenderer variable.
    var _directionsRenderer = '';

    //DirectionsRenderer() is a used to render the direction
    _directionsRenderer = new google.maps.DirectionsRenderer();
 
    //Set the your own options for map.
    var myOptions = {
        zoom: 14,
        center: new google.maps.LatLng(myLat, myLng),
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
 
    //Define the map.
    var map = new google.maps.Map(document.getElementById("map"), myOptions);
   
    //Set the map for directionsRenderer
    _directionsRenderer.setMap(map);
    
    if (navigator.geolocation) {


      //Set different options for DirectionsRenderer mehtods.
      //draggable option will used to drag the route.
      _directionsRenderer.setOptions({
          draggable: true
      });
      
      navigator.geolocation.getCurrentPosition(function(position) {
       var pos = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        var origen = new google.maps.LatLng(pos.lat, pos.lng);
          _mapPoints.push(origen);
          _directionsRenderer = getRoutePointsAndWaypoints(_directionsRenderer,_mapPoints);
      });

      var destino = new google.maps.LatLng(myLat, myLng);
          _mapPoints.push(destino);
          _directionsRenderer = getRoutePointsAndWaypoints(_directionsRenderer,_mapPoints);

      
       /*     //Add the doubel click event to map.
      google.maps.event.addListener(map, "dblclick", function (event) {
          //Check if Avg Speed value is enter.
          if ($("#txtAvgSpeed").val() == '') {
              alert("Please enter the Average Speed (km/hr).");
              $("#txtAvgSpeed").focus();
              return false;
          }
         
          var _currentPoints = event.latLng;
          _mapPoints.push(_currentPoints);
          _directionsRenderer = getRoutePointsAndWaypoints(_directionsRenderer,_mapPoints);
      });
     
      //Add an event to route direction. This will fire when the direction is changed.
      google.maps.event.addListener(_directionsRenderer, 'directions_changed', function () {
          computeTotalDistanceforRoute(_directionsRenderer.directions);
      });
      */
    }else{
      alert("no se ha dado permisos de localización");
      var uluru = {lat: myLat, lng: myLng };
      var marker = new google.maps.Marker({
        position: uluru,
        map: map
      });
    }
}

