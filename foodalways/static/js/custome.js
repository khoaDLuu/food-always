// Click on the custom js file

// Back to top
function gotoTop(min_height) {
    // Predefine the HTML code that returns to the top , and its css style is not displayed by default
    var gotoTop_html = '<div id="gotoTop"></div>';
    // Insert the html code back to the top into the end of the element whose id is page on the page
    $("#page").append(gotoTop_html);
    $("#gotoTop").click( // Define the animation that returns to the top and clicks to scroll up
        function () {
            $('html,body').animate({scrollTop: 0}, 700);
        }).hover( // In order to return to the top to increase the feedback effect of mouse entry, use the add and delete css class to achieve
        function () {
            $(this).addClass("hover");
        },
        function () {
            $(this).removeClass("hover");
        });
    // Get the minimum height of the page, if no value is passed in, the default is 600 pixels
    min_height ? min_height = min_height : min_height = 1000;
    // Bind the processing function for the scroll event of the window
    $(window).scroll(function () {
        // Get the vertical position of the scroll bar of the window
        var s = $(window).scrollTop();
        // When the vertical position of the scroll bar of the window is greater than the minimum height of the page,
        // let the return to the top element gradually appear, otherwise fade out
        if (s > min_height) {
            $("#gotoTop").fadeIn(100);
        } else {
            $("#gotoTop").fadeOut(200);
        }
    });
}

// Call the function
gotoTop();
