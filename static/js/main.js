(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();



    // Sticky Navbar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 45) {
            $('.navbar').addClass('sticky-top shadow-sm');
        } else {
            $('.navbar').removeClass('sticky-top shadow-sm');
        }
    });
    
    
    // Dropdown on mouse hover
    const $dropdown = $(".dropdown");
    const $dropdownToggle = $(".dropdown-toggle");
    const $dropdownMenu = $(".dropdown-menu");
    const showClass = "show";
    
    $(window).on("load resize", function() {
        if (this.matchMedia("(min-width: 992px)").matches) {
            $dropdown.hover(
            function() {
                const $this = $(this);
                $this.addClass(showClass);
                $this.find($dropdownToggle).attr("aria-expanded", "true");
                $this.find($dropdownMenu).addClass(showClass);
            },
            function() {
                const $this = $(this);
                $this.removeClass(showClass);
                $this.find($dropdownToggle).attr("aria-expanded", "false");
                $this.find($dropdownMenu).removeClass(showClass);
            }
            );
        } else {
            $dropdown.off("mouseenter mouseleave");
        }
    });

})(jQuery);




$(document).ready(function() {
    $("#get-user-location").click(function() {
        navigator.geolocation.getCurrentPosition(function(position) {
            let latitude = position.coords.latitude;
            let longitude = position.coords.longitude;

            // Show loading indicator
            $('#user-loc-animation').show();

            // Send coordinates to Flask using AJAX (explained in Flask code)
            $.ajax({
                url: "/send-coordinates", // Replace with your Flask endpoint
                type: "POST",
                data: {
                    latitude: latitude,
                    longitude: longitude
                },
                success: function(response) {
                      console.log("Location received:", response);
//                    alert(response); // Display a success message from Flask
                      // hide loading indicator
                      $('#user-loc-animation').hide();
//                },
//                error: function(jqXHR, textStatus, errorThrown) {
//                    console.error("Error sending coordinates:", textStatus, errorThrown);
//                    alert("Error sending coordinates. Please check the console for details.");
                }
            });
        }, function(error) {
            console.error("Error getting geolocation:", error);
            alert("Error getting your location. Please check your browser settings.");
        });
    });
});



function showLoading() {
    // Show the loading animation
    document.getElementById('loading-animation').style.display = 'block';
}






function showDirections(button) {
    // Get the value of the data-item attribute
    var itemData = button.getAttribute('data-item');

    // Split the data-item attribute to extract latitude and longitude
    var coordinates = itemData.split(',');
    var latitude = coordinates[0].trim(); // Latitude
    var longitude = coordinates[1].trim(); // Longitude

    // Construct the Google Maps URL
    var mapsUrl = "https://www.google.com/maps?q=" + latitude + "," + longitude;

    // Open Google Maps in a new tab
    window.open(mapsUrl, "_blank");
}




var multipleCardCarousel = document.querySelector(
  "#carouselExampleControls"
);
if (window.matchMedia("(min-width: 768px)").matches) {
  var carousel = new bootstrap.Carousel(multipleCardCarousel, {
    interval: false,
  });
  var carouselWidth = $(".carousel-inner")[0].scrollWidth;
  var cardWidth = $(".carousel-item").width();
  var scrollPosition = 0;
  $("#carouselExampleControls .carousel-control-next").on("click", function () {
    if (scrollPosition < carouselWidth - cardWidth * 4) {
      scrollPosition += cardWidth;
      $("#carouselExampleControls .carousel-inner").animate(
        { scrollLeft: scrollPosition },
        600
      );
    }
  });
  $("#carouselExampleControls .carousel-control-prev").on("click", function () {
    if (scrollPosition > 0) {
      scrollPosition -= cardWidth;
      $("#carouselExampleControls .carousel-inner").animate(
        { scrollLeft: scrollPosition },
        600
      );
    }
  });
} else {
  $(multipleCardCarousel).addClass("slide");
}

